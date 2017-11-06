pipeline {
	agent none
	stages {
		stage('Build') {
			agent { 
				dockerfile {
					image 'ubuntu:16.04'
					additionalBuildArgs '-t resplatimg --build-arg'
				}
			}
			steps {
				sh 'curl http://localhost'
			}
		}
	}
}
