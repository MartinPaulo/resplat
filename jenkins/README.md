# Jenkins scripts and other things

This folder contains materials used in Jenkins builds and is referenced by the Jenkinsfile in the root directory.

## Design Overview
![UoMResplatReportingInfrastructure.png](UoMResplatReportingInfrastructure.png)

### Web Front

A simple web server that proxy passes to an application server. This allows the build pipeline to implement a Blue-Green deployment patten as well as stricting access to application servers.

See [web_front](web_front).

__Current Web Fronts__:
* _reporting.cloud.unimelb.edu.au_: The production instance that serves the application
* _internal_: Serves a "QA" instance of the application so that we can run a UAT on new builds before confirming deployment
* _~~jenkins~~_: Serves the Jenkins build server. (Currently this web front does not exist)

### Deployment Pattern

A jenkins pipeline is used to build, test and deploy instances of the application. The application is packaged as a whole VM instance, and orchestrated by OpenStack HEAT. This is captured by [OS_deploy_replace.bash](OS_deploy_replace) script which is invoked by the pipeline. The script will:
* HEAT deploy a new instance of the application following the [deploy.yaml](deploy.yaml) template
* Wait for deployment completion and confirmation of a successfuly deployment
* Update Web front server reporting.cloud.unimelb.edu.au (Prod) or internal (QA) to the new instance
* Delete all old stacks
By updating the web front server only when everything is successful, we can ensure minimal risks to operation of this application.

See [Setup](#setup) section for instructions.

### Databases

The application uses PostgreSQL for application state. As such they are not frequently brought down/up. They are hosted on OpenStack Trove instances.

Two instances are used:
* _Prod_: For the production application. This is the definitive source of the latest information for the application
* _TestDB_: For the QA instance of the application. A nightly process will ensure this database is a copy of the _Prod_ database. This allows the new code changes to be reviewed by testing to be applied to production data safely. Schema changes from code changes are applied via django's _python manage.py migrate_. This copy process is apart of the backup system. See Backup.

New instances of the application connect to their respective database instance simply through connection details in local\_settings.py that is copied by [OS_deploy_replace.bash](OS_deploy_replace.bash) on creation. See Setup section for instructions.

### Jenkins Server

A VM running Jenkins is used to facilitate the build pipeline. The build pipeline scope includes:
* Local build, test and test documentation
* Deploy QA instance
* Deploy Prod instance

For pipeline logic, see [Jenkinsfile](../Jenkinsfile)

For Jenkins server, see https://github.com/AlanCLo/JenkinsServer

See [Setup](#setup) for how to setup parameters for these builds

### Backup

Nightly processes will perform full database dumps of the Prod database. Backup is stored on OpenStack SWIFT using duplicity. This system is also used to mirror the QA database with Prod by executing database restoration with the latest backup. Backups stored includes:
* Daily
* Weekly
* Monthly

Rolling window policies are applied to each of these frequencies and backups older than X will be removed.

Currently, the Jenkins Server is reponsible for execution of backup scripts and restoration.

For backup scripts documentation, see https://github.com/AlanCLo/JenkinsServer/duplicity 

## Setup

This section covers the current instructure setup as per the diagram in overview.

### Database

TODO

### Web front

See [Web Front](web_front) for instructions.
 * QA instance is using 'Self-signed' mode
 * Prod instance is using 'Signed certificate' mode
 

### One instance of the deployment pattern

This section covers how to deploy once instance of the deployment pattern. This allows you to make one for yourself, or to setup the QA and Prod stages in the Jenkins build pipeline.

[OS_deploy_replace.bash](OS_deploy_replace.bash) expects a number of environment variables for deployment parameters and files which is organised into a __single__ folder for the Jenkins pipeline to reference. This script expects as an argument, a single file that will fill in all required parameters.

#### Prerequisites

* _OpenStack profile_: The user-tenancy on OpenStack for this infrastructure. Download from dashboard.
* _Database & local\_settings.py_: The application's django local\_settings.py that will be copied to the new instance. Copy [resplat/local_settings_template.py](../resplat/local_settings_template.py) to start a new one. The main properties to set are the database connection details the application will use.
* _extra\_ssh\_keys.pub_: A file with concatenated ssh public keys that will be appended to .ssh/authorized\_keys on the new server
* _Web Front server_: See [web_front](web_front) for setup. __Important__: Make sure the server that executes OS\_deploy\_replace.bash has ssh access to that server. For example, if you are getting a Jenkins server to run this script, you will need to add the ssh key for the jenkins user to that web front machine so it can talk to it. Do a quick ssh test to make sure it works.


#### Putting it together

Copy and complete [example.profile.template](example.profile.template). Follow the instructions in the comment to help you fill in the required parameters. Keep this profile and prerequisites in a single folder to keep it organised

The following is an example folder based on QA setup.
```bash
ubuntu@jenkins:/build_profiles/resplat.qa$ ls -1
deploy.params                # A completed version of example.profile.template
extra_ssh_keys.pub           # Keys of other team members who need to access the server
local_settings.py            # Connection settings to QA database
Resplat-Reporting-openrc.sh  # Tenancy for OpenStack
```

To run the script with the above example:
```bash
$ ./OS_deploy_replace.bash /build_profiles/resplat.qa/deploy.params
```

### Jenkins Building

This section documents how the Jenkins project is setup for this application on a Jenkins server.

#### Prerequisites

* A Jenkins build server
* The [Jenkins pipeline](../Jenkinsfile) uses:
  * Three database instances of the application (one for build/testing local to jenkins, a QA and Prod)
  * Two web front servers for QA and Prod
  * Two instances of the deployment pattern (QA and Prod), using the aforementioned databases and web fronts.

Follow the instructions above to setup both stacks inclusive of web front servers, database and profile details.

#### Jenkins Nodes

For any number of Jenkins nodes that may do the build, you'll need to setup enviornment variables the [Jenkinsfile](../Jenkinsfile) refers to for QA and Prod.

 1. Go to 'Manage Jenkins' > 'Manage Nodes' > (node) > Configure
 2. Under 'Node Properties', make sure 'Environment Variables' is checked.
 3. Add:
```
RESPLAT_TEST_SETTINGS=/build_profiles/resplat.test/
RESPLAT_QA_SETTINGS=/build_profiles/resplat.qa/
RESPLAT_PROD_SETTINGS=/build_profiles/resplat.prod/
```

#### Jenkins project

 1. Create a 'Multibranch Pipeline' project
 2. Add Branch sources to this Git repository

Once you save the project, Jenkins will start the first scan of the repository and initate a build. You can adjust the trigger for further builds (manual by default) under the project 'Configuration' page.



