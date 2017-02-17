from bs4 import BeautifulSoup

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from aboutconfig.models import DataType, Config
from aboutconfig.utils import _get_cache
from aboutconfig.constants import CONFIG_ADMIN_TYPE_QUERY_KEY

User = get_user_model()


class AdminTestMixin(object):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create(
            username='admin', is_superuser=True, is_staff=True, is_active=True,
            password='sha1$995a3$6011485ea3834267d719b4c801409b8b1ddd0158') # pw=secret

        # force_login() is only available in 1.9+
        if hasattr(self.c, 'force_login'):
            self.c.force_login(self.user)
        else:
            self.c.login(username='admin', password='secret')


class ConfigAdminTest(AdminTestMixin, TestCase):
    def setUp(self):
        super(ConfigAdminTest, self).setUp()
        dt = DataType.objects.get(name='String')
        Config.objects.create(key='unique_namespace_1.b', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_1.c', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_1.d', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_2.a', value='bar', data_type=dt)
        Config.objects.create(key='unique_namespace_2.b', value='bar', data_type=dt)

        self.url = reverse('admin:aboutconfig_config_changelist')


    def tearDown(self):
        _get_cache().clear()


    def get_dom(self, res):
        return BeautifulSoup(res.content.decode('utf-8'), 'html.parser')


    def test_all(self):
        res = self.c.get(self.url)
        self.assertContains(res, 'unique_namespace_1.b')
        self.assertContains(res, 'unique_namespace_1.c')
        self.assertContains(res, 'unique_namespace_1.d')
        self.assertContains(res, 'unique_namespace_2.a')
        self.assertContains(res, 'unique_namespace_2.b')

        dom = self.get_dom(res)

        item = dom.select('#changelist-filter a[href="?namespace=unique_namespace_1"]')
        self.assertEqual(len(item), 1)
        self.assertEqual(item[0].text, 'unique_namespace_1')

        item = dom.select('#changelist-filter a[href="?namespace=unique_namespace_2"]')
        self.assertEqual(len(item), 1)
        self.assertEqual(item[0].text, 'unique_namespace_2')


    def test_namespace_filter(self):
        res = self.c.get(self.url + '?namespace=unique_namespace_1')
        self.assertContains(res, 'unique_namespace_1.b')
        self.assertContains(res, 'unique_namespace_1.c')
        self.assertContains(res, 'unique_namespace_1.d')
        self.assertNotContains(res, 'unique_namespace_2.a')
        self.assertNotContains(res, 'unique_namespace_2.b')

        dom = self.get_dom(res)

        item = dom.select('#changelist-filter a[href="?namespace=unique_namespace_1"]')
        print(item)
        self.assertEqual(len(item), 1)
        self.assertEqual(item[0].text, 'unique_namespace_1')
        self.assertTrue('selected' in item[0].parent['class'].split())

        item = dom.select('#changelist-filter a[href="?namespace=unique_namespace_2"]')
        self.assertEqual(len(item), 1)
        self.assertEqual(item[0].text, 'unique_namespace_2')
        self.assertTrue('selected' not in item[0].parent['class'].split())


class ConfigAdminAjaxTest(AdminTestMixin, TestCase):
    def setUp(self):
        super(ConfigAdminAjaxTest, self).setUp()
        self.url = reverse('admin:ac-fetch-value-field')
        self.dt = DataType.objects.get(name='String')
        Config.objects.create(key='a.b', value='1', data_type=self.dt)


    def test_unknown_datatype(self):
        res = self.c.get(self.url, {CONFIG_ADMIN_TYPE_QUERY_KEY: '9999'})
        self.assertEqual(res.status_code, 404)


    def test_no_id(self):
        res = self.c.get(self.url, {CONFIG_ADMIN_TYPE_QUERY_KEY: self.dt.pk})
        self.assertEqual(res.status_code, 400)


    def test_new_config_valid_value(self):
        res = self.c.get(self.url, {
            CONFIG_ADMIN_TYPE_QUERY_KEY: self.dt.pk,
            'id': 'my_unique_id',
            'value': 'abc123'
        })
        self.assertEqual(res.status_code, 200)
        parsed = self._get_json(res)

        self.assertTrue('content' in parsed)
        self.assertTrue('my_unique_id' in parsed['content'])
        self.assertTrue('abc123' in parsed['content'])


    def test_edit_config_invalid_value(self):
        int_dt = DataType.objects.get(name='Integer')
        config = Config.objects.create(key='x', value=1, data_type=int_dt)
        res = self.c.get(self.url, {
            CONFIG_ADMIN_TYPE_QUERY_KEY: int_dt.pk,
            'id': 'my_unique_id',
            'value': 'abc123',
            'config_pk': config.pk
        })

        self.assertEqual(res.status_code, 200)
        parsed = self._get_json(res)

        self.assertTrue('content' in parsed)
        self.assertTrue('my_unique_id' in parsed['content'])
        self.assertTrue('abc123' not in parsed['content'])

    def _get_json(self, res):
        try:
            return res.json() # django 1.9+ only
        except AttributeError:
            import json
            return json.loads(res.content.decode('utf-8'))


class ConfigAdminAjaxTest2(TestCase):
    """Same as ConfigAdminAjaxTest but uses a non-superuser to test."""
    def setUp(self):
        self.url = reverse('admin:ac-fetch-value-field')
        self.c = Client()


    def test_no_login(self):
        res = self.c.get(self.url)
        self.assertEqual(res.status_code, 302)


    def test_not_admin(self):
        user = User.objects.create(
            username='user', is_superuser=False, is_staff=False, is_active=True,
            password='sha1$995a3$6011485ea3834267d719b4c801409b8b1ddd0158') # pw=secret

        # force_login() is only available in 1.9+
        if hasattr(self.c, 'force_login'):
            self.c.force_login(user)
        else:
            self.c.login(username='user', password='secret')

        res = self.c.get(self.url)
        self.assertEqual(res.status_code, 302)


class ConfigAdminEditTest(AdminTestMixin, TestCase):
    def setUp(self):
        super(ConfigAdminEditTest, self).setUp()
        self.dt = DataType.objects.get(name='String')
        self.config = Config.objects.create(key='x', value='y', data_type=self.dt)
        self.url = reverse('admin:aboutconfig_config_change', args=(self.config.pk,))


    def test_attributes_edit(self):
        res = self.c.get(self.url)
        self.assertContains(res, 'class="aboutconfig-type-field"')
        self.assertContains(res, 'data-url="{}"'.format(reverse('admin:ac-fetch-value-field')))
        self.assertContains(res, 'data-instance-pk="{}"'.format(self.config.pk))


    def test_attributes_create(self):
        res = self.c.get(reverse('admin:aboutconfig_config_add'))
        self.assertContains(res, 'class="aboutconfig-type-field"')
        self.assertContains(res, 'data-url="{}"'.format(reverse('admin:ac-fetch-value-field')))
        self.assertContains(res, 'data-instance-pk=""')
