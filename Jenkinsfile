#!groovy

node {
	stage ('Build') {
		checkout scm
		// Fetch a copy of the test settings to build into the container
		sh "cp $RESPLAT_TEST_SETTINGS/local_settings.py resplat/local_settings.py"
		docker.build('resplatimg')
	}
	stage ('Test') {
		//docker_undeploy(RESPLAT_DEV_SETTINGS)
		//docker_deploy(RESPLAT_DEV_SETTINGS)
		docker.image('resplatimg').inside('-u root --link postgres:postgres') {
			stage ('Setup tests') {
				sh 'python3 manage.py migrate'
			}
			stage ('Run tests') {
				sh 'coverage run manage.py test --keepdb storage -v 2'
				sh 'coverage html'
			}
			stage ('Archive results') {
				archive (includes: 'htmlcov/*')
			}
		}
	}
}

if (BRANCH_NAME == "master") {
	node {
		stage ('QA') {
			heat_deploy(RESPLAT_QA_SETTINGS)
		}
	}
/*
	input "Deploy to production?"
	node {
		stage ('Production') {
			heat_deploy(RESPLAT_QA_SETTINGS)
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
	timeout(time: 600, unit: 'SECONDS') {
		sh "SCRIPT_HOME=`pwd`/jenkins bash jenkins/OS_deploy_replace.bash $settings/deploy.params"
	}
}



