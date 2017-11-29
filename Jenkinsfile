#!groovy

node {
	stage ('Build') {
		checkout scm
		docker.build('resplatimg')
	}
}
/*
	}
	stage ('Test') {
		docker.image('resplatimg').inside('-u root') {
			stage ('Setup tests') {
				sh 'python3 --version'
				echo 'This is a place holder for setting up test settings if any'
			}
			stage ('Run tests') {
				echo 'This is a place holder for running tests'
			}
			stage ('Archive results') {
				echo 'This is a place holder to archive artefacts'
			}
		}
	}
}
*/

if (BRANCH_NAME == "master") {
	node {
		stage ('QA') {
			heat_deploy(RESPLAT_QA_SETTINGS)
			//docker_undeploy(RESPLAT_QA_SETTINGS)
			//docker_deploy(RESPLAT_QA_SETTINGS)
		}
	}
/*
	input "Deploy to production?"
	node {
		stage ('Production') {
			docker_undeploy(RESPLAT_PROD_SETTINGS)
			docker_deploy(RESPLAT_PROD_SETTINGS)
		}
	}
*/
}

def docker_deploy(settings) {
	sh "docker run -d -it -p `cat $settings/PORT`:80 --name=`cat $settings/NAME` --link postgres:postgres resplatimg"
	sh "docker cp $settings/local_settings.py `cat $settings/NAME`:/resplat/resplat/local_settings.py"
	sh "docker exec `cat $settings/NAME` service apache2 start"
}

def docker_undeploy(settings) {
	sh "docker stop `cat $settings/NAME` || true"
	sh "docker rm `cat $settings/NAME` || true"
}

def heat_deploy(settings) {
	timeout(time: 45, unit: 'SECONDS') {
		sh "SCRIPT_HOME=`pwd`/jenkins bash jenkins/OS_deploy_replace.bash $settings/deploy.params"
	}
}



