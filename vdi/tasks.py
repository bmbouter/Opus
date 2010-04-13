from celery.task import PeriodicTask, Task
from celery.registry import tasks
from celery.decorators import task
from datetime import timedelta
from vdi.log import log
from django.http import HttpResponse, HttpResponseRedirect

'''
class MyPeriodicTask(Task):
#class MyPeriodicTask(PeriodicTask):
    #run_every = timedelta(seconds=30)

    def run(self, **kwargs):
        log.debug("Running periodic task!")

'''

class CreateUserTask(Task):
    def run(self, username, password):
        log.debug('8888888888888888888888')

'''
class MyTask(Task):
    def run(self, some_arg, **kwargs):
        logger = self.get_logger(**kwargs)
        log.debug('*************')
        logger.info('AEIOU')
        logger.info("Did something: %s" % some_arg)
'''

tasks.register(CreateUserTask)
#tasks.register(MyTask)
log.debug('AAAAAAAAASDFSDFASFDASFDASFDSA')
