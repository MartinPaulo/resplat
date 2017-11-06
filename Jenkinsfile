pipeline {
	agent none
	stages {
		stage('Build') {
			agent { 
				dockerfile {
					additionalBuildArgs '-t resplatimg'
				}
			}
			steps {
				sh 'curl http://localhost'
			}
		}
	}
}
