pipeline {
	agent none
	stages {
		stage('Build') {
			agent { 
				docker {
					image 'ubuntu:16.04'
					args '-u root'
				}
			}
			steps {
				sh 'apt-get update'
				sh 'apt-get upgrade'
				sh 'apt-get install -y python3-pip python3-dev python3-tk apache2 libapache2-mod-wsgi-py3'
				sh 'apt-get install -y postgresql postgresql-contrib'
				sh 'apt-get install -y git curl libpq-dev'
				sh 'apt-get install -y sudo'
				sh 'apt-get install -y vim'
				sh 'ln -fs /usr/bin/python3 /usr/bin/python'
				sh 'pip3 install --upgrade pip'
				sh 'pip install -r requirements.txt'

				sh 'sh jenkins/local_dbsetup.sh'

				sh 'sh jenkins/django_setup.sh'

				sh 'sh jenkins/apache_setup.sh'

				sh 'curl http://localhost'
			}
		}
	}
}
