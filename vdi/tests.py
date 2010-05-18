from datetime import datetime
import time

from django.test import TestCase
from django.contrib.auth.models import User

from vdi.models import UserExperience, Application, Instance
from vdi import user_experience_tools, cost_tools

import core
log = core.log.getLogger()


class CostToolsTest(TestCase):
    def setUp(self):
        self.app1 = Application.objects.create(name="TestApp1", image_id="1234", max_concurrent_instances=3, users_per_small=4, cluster_headroom=5, icon_url="http://nopath", ssh_key='key.fake')
        self.app2 = Application.objects.create(name="TestApp2", image_id="12345", max_concurrent_instances=3, users_per_small=4, cluster_headroom=5, icon_url="http://nopath", ssh_key='key.fake')
        self.inst1 = Instance.objects.create(instanceId='10', application=self.app1, priority=0, state=5) 
        self.inst1.shutdownDateTime=datetime(2010,5,13,18,00)
        self.inst1.startUpDateTime=datetime(2010,5,13,12,00)
        self.inst1.save()
        self.inst2 = Instance.objects.create(instanceId='11', application=self.app1, priority=0, state=2) 
        self.inst2.shutdownDateTime=datetime(2010,5,14,8,00)
        self.inst2.startUpDateTime=datetime(2010,5,14,8,00)
        self.inst2.save()
        self.inst3 = Instance.objects.create(instanceId='12', application=self.app2, priority=0, state=5) 
        self.inst3.shutdownDateTime=datetime(2010,5,12,18,00)
        self.inst3.startUpDateTime=datetime(2010,5,11,8,00)
        self.inst3.save()
        app = Application.objects.all()
        tmp_list = list(app)
        log.debug("TMP 2 : " + str(tmp_list[0]))
        log.debug("TMP 1 : " + str(tmp_list[1]))
        log.debug(tmp_list[0].image_id)
        tmp_list[0].image_id = '4321'
        tmp_list[0].save()
        log.debug(tmp_list[0].image_id)
        app_tmp = Application.objects.all()
        log.debug(app_tmp)

    def test_get_instance_hours_in_date_range(self):
        app = Application.objects.all()
        log.debug("***TEST*** APP CHANGE : " + app[0].image_id)
        self.failUnlessEqual(cost_tools.get_instance_hours_in_date_range(datetime(2010,5,14,1,00), datetime(2010,5,14,14,00)), 6)
        self.failUnlessEqual(cost_tools.get_instance_hours_in_date_range(datetime(2010,5,12,1,00), datetime(2010,5,14,14,00)), 12)

    def test_get_total_instance_hours(self):
        app = Application.objects.all()
        log.debug("***TEST*** APP CHANGE : " + app[0].image_id)
        instances = Instance.objects.all()
        self.failUnlessEqual(cost_tools.get_total_instance_hours(instances, datetime(2010,5,10,8,00), datetime(2010,5,14,22,00)), 54)

class UserExperienceTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="Test1")
        self.user2 = User.objects.create(username="local++Test2")
        self.user3 = User.objects.create(username="Test3")

        self.app1 = Application.objects.create(name="TestApp1", image_id="1234", max_concurrent_instances=3, users_per_small=4, cluster_headroom=5, icon_url="http://nopath", ssh_key='key.fake')
        self.app2 = Application.objects.create(name="TestApp2", image_id="12345", max_concurrent_instances=3, users_per_small=4, cluster_headroom=5, icon_url="http://nopath", ssh_key='key.fake')
        
        self.ue1 = UserExperience.objects.create(user=self.user1, application=self.app1, file_presented=datetime(2010,5,13,12,00), connection_closed=datetime(2010,5,13,12,45), access_date=datetime(2010,5,13,11,58), connection_opened=datetime(2010,5,14,12,02))
        self.ue2 = UserExperience.objects.create(user=self.user1, application=self.app1, file_presented=datetime(2010,5,14,16,00), connection_closed=datetime(2010,5,14,17,45), access_date=datetime(2010,5,14,15,54), connection_opened=datetime(2010,5,14,16,3))
        self.ue3 = UserExperience.objects.create(user=self.user1, application=self.app2, file_presented=datetime(2010,5,14,18,00), connection_closed=datetime(2010,5,14,18,45), access_date=datetime(2010,5,14,17,57), connection_opened=datetime(2010,5,14,18,5))
        self.ue4 = UserExperience.objects.create(user=self.user2, application=self.app2, file_presented=datetime(2010,5,14,18,15), connection_closed=datetime(2010,5,14,18,40), access_date=datetime(2010,5,14,18,12), connection_opened=datetime(2010,5,14,18,17))
        self.ue5 = UserExperience.objects.create(user=self.user3, application=self.app2, file_presented=datetime(2010,5,14,18,15), access_date=datetime(2010,5,14,18,12))

        class AppNodeTest:
            def __init__(self):
                self.sessions = []
        
        self.app_node = AppNodeTest()
        self.session = {}
        self.session['username'] = "Test3"
        self.app_node.sessions.append(self.session)

    def test_get_all_user_wait_times(self):
        self.failUnlessEqual(user_experience_tools.get_all_user_wait_times(self.app1), [120, 360]) 
        log.debug("***TEST*** user Wait Times: " + str(user_experience_tools.get_all_user_wait_times(self.app1)))    

    def test_get_user_applications_on_date(self):
        self.failUnlessEqual(user_experience_tools.get_user_applications_in_date_range(self.user1, datetime(2010,5,14,00), datetime(2010,5,14,23,59)), [self.app1, self.app2]) 
        log.debug("***TEST*** User Applications on Date: " + str(user_experience_tools.get_user_applications_in_date_range(self.user1, datetime(2010,5,14,00), datetime(2010,5,14,23,59))))

    def test_get_application_service_times(self):
        self.failUnlessEqual(user_experience_tools.get_application_service_times(self.app1), [2700, 6300]) 
        log.debug("***TEST*** Service Times: " + str(user_experience_tools.get_application_service_times(self.app1)))
            

    def test_get_user_application_arrival_times(self):
        self.failUnlessEqual(self.ue1.access_date.ctime(), user_experience_tools.get_user_application_arrival_times(self.app1)[0].ctime())
        log.debug(user_experience_tools.get_user_application_arrival_times(self.app1))

    def test_get_concurrent_users_over_date_range(self):
        self.failUnlessEqual(user_experience_tools.get_concurrent_users_over_date_range(self.app2, datetime(2010,5,14,17,55), datetime(2010,5,14,19,00), 5*60), [0, 1, 1, 1, 2, 2, 2, 2, 2, 1, 0, 0, 0])

    def test_procesS_user_connections(self):
        user_experience_tools.process_user_connections(self.app_node)
        us_exp1 = UserExperience.objects.filter(user=self.user3).filter(connection_opened__isnull=False)
        self.failIfEqual(us_exp1[0].connection_opened, None)
        log.debug("****TEST**** connection opened = " + str(us_exp1[0].connection_opened))
        self.app_node.sessions.remove(self.session)
        user_experience_tools.process_user_connections(self.app_node)
        us_exp2 = UserExperience.objects.filter(user=self.user3).filter(connection_closed__isnull=False)
        self.failIfEqual(us_exp2[0].connection_closed, None)
        log.debug("****TEST**** connection closed = " + str(us_exp2[0].connection_closed))
