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
				sh 'python3 --version'
			}
		}
		stage('Dev-deploy') {
			when {
				expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
			}
			agent any
			steps {
				sh 'docker stop resplat || true && docker rm resplat || true'
				sh 'docker run -d -it --name resplat -p 33001:443 --link postgres:postgres resplatimg'
				sh 'docker cp $RESPLAT_DEV_SETTINGS resplat:/resplat/resplat/local_settings.py'
				sh 'docker exec resplat service apache2 start'
			}
		}
	}
}
