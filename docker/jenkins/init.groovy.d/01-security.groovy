import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import jenkins.install.InstallState
import jenkins.model.Jenkins

def instance = Jenkins.get()
def adminUser = System.getenv("JENKINS_ADMIN_ID") ?: "admin"
def adminPassword = System.getenv("JENKINS_ADMIN_PASSWORD") ?: "admin"

def securityRealm = instance.getSecurityRealm()
if (!(securityRealm instanceof HudsonPrivateSecurityRealm)) {
    securityRealm = new HudsonPrivateSecurityRealm(false)
    instance.setSecurityRealm(securityRealm)
}

if (securityRealm.getUser(adminUser) == null) {
    securityRealm.createAccount(adminUser, adminPassword)
}

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)
instance.setNumExecutors(2)

if (instance.getInstallState() != InstallState.INITIAL_SETUP_COMPLETED) {
    InstallState.INITIAL_SETUP_COMPLETED.initializeState()
}

instance.save()
