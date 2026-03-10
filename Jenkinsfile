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
                tar -czf allure-report.tar.gz "${ALLURE_RESULTS_DIR}" || true
            '''

            junit allowEmptyResults: true, testResults: 'allure-results/junit.xml'

            script {
                int allureFileCount = sh(
                    script: "if [ -d \"${env.ALLURE_RESULTS_DIR}\" ]; then find \"${env.ALLURE_RESULTS_DIR}\" -type f | wc -l; else echo 0; fi",
                    returnStdout: true
                ).trim() as Integer

                if (allureFileCount > 0) {
                    allure includeProperties: false, jdk: '', reportBuildPolicy: 'ALWAYS', results: [[path: "${env.ALLURE_RESULTS_DIR}"]]
                } else {
                    echo "Allure results are empty. Skipping Allure publish."
                }
            }

            archiveArtifacts artifacts: 'allure-results/**/*,allure-report.tar.gz,test-summary.env', allowEmptyArchive: true

            script {
                if (!env.CI_EMAIL_TO?.trim()) {
                    echo 'CI_EMAIL_TO is empty. Skip email notification.'
                    return
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

                emailext(
                    to: env.CI_EMAIL_TO,
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
                )
            }
        }
    }
}
