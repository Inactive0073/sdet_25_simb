import jenkins.model.Jenkins
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def instance = Jenkins.get()
def jobName = System.getenv("JENKINS_SEED_JOB_NAME") ?: "bankingproject-ui-tests"
def repoUrl = System.getenv("JENKINS_GIT_URL") ?: "git@github.com:Inactive0073/sdet_25_simb.git"
def branchSpec = System.getenv("JENKINS_GIT_BRANCH") ?: "*/main"
def credentialsId = System.getenv("JENKINS_GIT_CREDENTIALS_ID") ?: "github-ssh"
def scriptPath = System.getenv("JENKINS_PIPELINE_PATH") ?: "Jenkinsfile"

WorkflowJob job = instance.getItem(jobName)
if (job == null) {
    job = instance.createProject(WorkflowJob, jobName)
}

def remoteConfig = new UserRemoteConfig(repoUrl, null, null, credentialsId)
def scm = new GitSCM(
    [remoteConfig],
    [new BranchSpec(branchSpec)],
    false,
    [],
    null,
    null,
    []
)

def definition = new CpsScmFlowDefinition(scm, scriptPath)
definition.setLightweight(true)

job.setDefinition(definition)
job.setDescription("Seeded pipeline from ${repoUrl} (${branchSpec}), script: ${scriptPath}")
job.save()
instance.save()

println("Seeded Jenkins pipeline job from SCM: ${jobName}")
