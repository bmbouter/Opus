##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

from celery.decorators import task
from django.conf import settings

from opus.lib.deployer import ProjectDeployer
import opus.project.deployment.models
from opus.lib.log import get_logger
log = get_logger()

@task
def destroy_project(projectid):
    project = opus.project.deployment.models.DeployedProject.objects.get(pk=projectid)

    log.info("Running task to destroy project %s", project)
    project.destroy()

@task
def destroy_project_by_name(projectname):
    """Used by the rollback functionality, since the model object is never
    committed to the database

    """
    project = opus.project.deployment.models.DeployedProject()
    project.name = projectname

    log.info("Running task to destroy project %s", project)
    project.destroy()

@task
def start_supervisord(projectdir):
    d = ProjectDeployer(projectdir)
    d.start_supervisord(settings.OPUS_SECUREOPS_COMMAND)

@task
def kill_processes(projectid):
    project = opus.project.deployment.models.DeployedProject.objects.get(pk=projectid)
    log.info("Killing all processes for %s", project.name)
    destroyer = opus.lib.deployer.ProjectUndeployer(project.projectdir)
    destroyer.kill_processes(settings.OPUS_SECUREOPS_COMMAND)
