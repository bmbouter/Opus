from datetime import datetime
import time

from django.test import TestCase
from django.contrib.auth.models import User

from vdi.models import UserExperience, Application
from vdi import user_experience_tools

import core
log = core.log.getLogger()

class UserExperienceTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="Test1")
        self.app1 = Application.objects.create(name="TestApp1", image_id="1234", max_concurrent_instances=3, users_per_small=4, cluster_headroom=5, icon_url="http://nopath", ssh_key='key.fake')
        self.ue1 = UserExperience.objects.create(user=self.user1, application=self.app1, file_presented=datetime(2010,5,13,12,00), connection_closed=datetime(2010,5,13,12,45), access_date=datetime(2010,5,13,11,58))


    def test_get_all_user_wait_times(self):
        log.debug("user Wait Times: " + str(user_experience_tools.get_all_user_wait_times(self.app1)))    

    def test_get_user_applications_on_date(self):
        log.debug(user_experience_tools.get_user_applications_on_date(self.user1, 2010, 5, 13))

    def test_get_application_service_times(self):
        log.debug(user_experience_tools.get_application_service_times(self.app1))
            

    def test_get_user_application_arrival_times(self):
        self.failUnlessEqual(self.ue1.access_date.ctime(), user_experience_tools.get_user_application_arrival_times(self.app1)[0].ctime())
        log.debug(user_experience_tools.get_user_application_arrival_times(self.app1))

    #def test_get_concurrent_users(self):
