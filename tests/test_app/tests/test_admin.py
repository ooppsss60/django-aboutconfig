from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from aboutconfig.models import DataType, Config
from aboutconfig.utils import _get_cache

User = get_user_model()


class ConfigAdminTest(TestCase):
    def setUp(self):
        dt = DataType.objects.get(name='String')
        Config.objects.create(key='unique_namespace_1.b', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_1.c', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_1.d', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_2.a', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_2.b', value='bar', data_type=dt)

        self.url = reverse('admin:aboutconfig_config_changelist')
        self.c = Client()
        self.user = User.objects.create(username='admin', is_superuser=True, is_staff=True)

        self.c.force_login(self.user)


    def tearDown(self):
        _get_cache().clear()


    def test_all(self):
        res = self.c.get(self.url)
        self.assertContains(res, 'unique_namespace_1.b')
        self.assertContains(res, 'unique_namespace_1.c')
        self.assertContains(res, 'unique_namespace_1.d')
        self.assertContains(res, 'unique_namespace_2.a')
        self.assertContains(res, 'unique_namespace_2.b')

        self.assertContains(res, '<li><a href="?namespace=unique_namespace_1">unique_namespace_1</a></li>', html=True)
        self.assertContains(res, '<li><a href="?namespace=unique_namespace_2">unique_namespace_2</a></li>', html=True)


    def test_namespace_filter(self):
        res = self.c.get(self.url + '?namespace=unique_namespace_1')
        self.assertContains(res, 'unique_namespace_1.b')
        self.assertContains(res, 'unique_namespace_1.c')
        self.assertContains(res, 'unique_namespace_1.d')
        self.assertNotContains(res, 'unique_namespace_2.a')
        self.assertNotContains(res, 'unique_namespace_2.b')

        self.assertContains(res, '<li class="selected"><a href="?namespace=unique_namespace_1">unique_namespace_1</a></li>', html=True)
        self.assertContains(res, '<li><a href="?namespace=unique_namespace_2">unique_namespace_2</a></li>', html=True)
