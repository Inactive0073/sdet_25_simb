pipeline {
    agent {
        node {
            label 'built-in || master'
        }
    }

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    triggers {
        cron('H H * * *')
        pollSCM('H/5 * * * *')
    }

    environment {
        COMPOSE_FILE = 'docker-compose.yml'
        COMPOSE_PROFILE = 'ci'
        ALLURE_RESULTS_DIR = 'allure-results'
        SELENOID_BROWSER_IMAGE = 'selenoid/vnc_chrome:123.0'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    rm -rf "${ALLURE_RESULTS_DIR}" allure-report.tar.gz test-summary.env
                    mkdir -p "${ALLURE_RESULTS_DIR}"
                    docker compose -f "${COMPOSE_FILE}" --profile "${COMPOSE_PROFILE}" rm -sf autotests selenoid selenoid-ui || true
                '''
            }
        }

        stage('Prepare browser image') {
            steps {
                sh '''
                    if ! docker image inspect "${SELENOID_BROWSER_IMAGE}" >/dev/null 2>&1; then
                        docker pull "${SELENOID_BROWSER_IMAGE}"
                    fi
                '''
            }
        }

        stage('Run UI tests in Docker') {
            steps {
                script {
                    int exitCode = sh(
                        script: '''
                            docker compose -f "${COMPOSE_FILE}" --profile "${COMPOSE_PROFILE}" up --build --abort-on-container-exit --exit-code-from autotests autotests selenoid selenoid-ui
                        ''',
                        returnStatus: true
                    )

                    sh '''
                        docker cp sdet_autotests:/app/allure-results/. "${ALLURE_RESULTS_DIR}" || true
                        docker compose -f "${COMPOSE_FILE}" --profile "${COMPOSE_PROFILE}" rm -sf autotests selenoid selenoid-ui || true
                    '''

                    if (exitCode != 0) {
                        error("Autotests failed with exit code ${exitCode}")
                    }
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker compose -f "${COMPOSE_FILE}" --profile "${COMPOSE_PROFILE}" rm -sf autotests selenoid selenoid-ui || true
                mkdir -p "${ALLURE_RESULTS_DIR}"

                if [ -f "${ALLURE_RESULTS_DIR}/junit.xml" ]; then
                    tests=$(sed -n 's/.*tests="\\([0-9]\\+\\)".*/\\1/p' "${ALLURE_RESULTS_DIR}/junit.xml" | head -n1)
                    failures=$(sed -n 's/.*failures="\\([0-9]\\+\\)".*/\\1/p' "${ALLURE_RESULTS_DIR}/junit.xml" | head -n1)
                    errors=$(sed -n 's/.*errors="\\([0-9]\\+\\)".*/\\1/p' "${ALLURE_RESULTS_DIR}/junit.xml" | head -n1)
                    skipped=$(sed -n 's/.*skipped="\\([0-9]\\+\\)".*/\\1/p' "${ALLURE_RESULTS_DIR}/junit.xml" | head -n1)
                    tests=${tests:-0}
                    failures=${failures:-0}
                    errors=${errors:-0}
                    skipped=${skipped:-0}
                else
                    tests=0
                    failures=0
                    errors=0
                    skipped=0
                fi

                failed=$((failures + errors))
                passed=$((tests - failed - skipped))
                if [ "${passed}" -lt 0 ]; then
                    passed=0
                fi

                printf "PASSED=%s\\nFAILED=%s\\nERRORS=%s\\nSKIPPED=%s\\nTOTAL=%s\\n" "${passed}" "${failed}" "${errors}" "${skipped}" "${tests}" > test-summary.env
            '''

            junit allowEmptyResults: true, testResults: 'allure-results/junit.xml'

            script {
                int allureFileCount = sh(
                    script: "if [ -d \"${env.ALLURE_RESULTS_DIR}\" ]; then find \"${env.ALLURE_RESULTS_DIR}\" -type f | wc -l; else echo 0; fi",
                    returnStdout: true
                ).trim() as Integer

                if (allureFileCount > 0) {
                    echo "Publishing Allure report from ${env.ALLURE_RESULTS_DIR}"
                    try {
                        step([
                            $class: 'AllureReportPublisher',
                            includeProperties: false,
                            jdk: '',
                            reportBuildPolicy: 'ALWAYS',
                            results: [[path: "${env.ALLURE_RESULTS_DIR}"]]
                        ])
                        echo 'Allure action published'
                    } catch (Exception e) {
                        echo "Allure action publish failed: ${e.getMessage()}"
                        unstable('Allure build action publish failed. HTML fallback will still be published.')
                    }

                    String archiveSource = env.ALLURE_RESULTS_DIR
                    try {
                        String allureHome = tool 'allure'
                        sh """
                            rm -rf allure-report
                            "${allureHome}/bin/allure" generate "${env.ALLURE_RESULTS_DIR}" -o allure-report --clean
                        """
                        archiveSource = 'allure-report'
                        publishHTML(target: [
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'allure-report',
                            reportFiles: 'index.html',
                            reportName: 'Allure HTML Report',
                            reportTitles: 'Allure HTML Report'
                        ])
                        echo 'HTML report published'
                    } catch (Exception e) {
                        echo "Allure HTML publish fallback triggered: ${e.getMessage()}"
                    }

                    sh "tar -czf allure-report.tar.gz ${archiveSource} || true"
                } else {
                    echo "Allure results are empty. Skipping Allure publish."
                    sh "tar -czf allure-report.tar.gz ${env.ALLURE_RESULTS_DIR} || true"
                }
            }

            archiveArtifacts artifacts: 'allure-report.tar.gz,test-summary.env,allure-results/**/*', allowEmptyArchive: true

            script {
                List<String> recipients = (env.CI_EMAIL_TO ?: '')
                    .split(/[\\s,;]+/)
                    .collect { it.trim() }
                    .findAll { it }

                if (recipients.isEmpty()) {
                    echo 'CI_EMAIL_TO is empty. Skip email notification.'
                    return
                }
                String normalizedRecipients = recipients.join(',')
                echo "Email recipients normalized: ${normalizedRecipients}"

                String fromAddress = (env.CI_EMAIL_FROM ?: '').trim()
                if (!fromAddress) {
                    echo 'CI_EMAIL_FROM is empty. Jenkins SMTP default sender will be used.'
                }

                String passed = '0'
                String failed = '0'
                String errors = '0'
                String skipped = '0'
                String total = '0'

                if (fileExists('test-summary.env')) {
                    readFile('test-summary.env')
                        .split('\\n')
                        .findAll { it.contains('=') }
                        .each { line ->
                            def (key, value) = line.split('=', 2)
                            if (key == 'PASSED') {
                                passed = value
                            } else if (key == 'FAILED') {
                                failed = value
                            } else if (key == 'ERRORS') {
                                errors = value
                            } else if (key == 'SKIPPED') {
                                skipped = value
                            } else if (key == 'TOTAL') {
                                total = value
                            }
                        }
                }

                Map emailArgs = [
                    to: normalizedRecipients,
                    subject: "[${env.JOB_NAME}] #${env.BUILD_NUMBER} ${currentBuild.currentResult}",
                    mimeType: 'text/html',
                    body: """
                        <p>Build result: <b>${currentBuild.currentResult}</b></p>
                        <p>Total: ${total}</p>
                        <p>Passed: ${passed}</p>
                        <p>Failed: ${failed}</p>
                        <p>Errors: ${errors}</p>
                        <p>Skipped: ${skipped}</p>
                        <p>Build URL: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                    """.stripIndent(),
                    attachmentsPattern: 'allure-report.tar.gz'
                ]

                if (fromAddress) {
                    emailArgs.from = fromAddress
                    emailArgs.replyTo = fromAddress
                }

                try {
                    emailext(emailArgs)
                } catch (Exception e) {
                    echo "Email send failed: ${e.getMessage()}"
                    unstable('Email delivery failed. Check SMTP settings/deliverability.')
                }
            }
        }
    }
}
