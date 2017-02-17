from django.test import TestCase
from django.template import Template, Context

from aboutconfig.utils import _get_cache
from aboutconfig.models import DataType, Config

class BaseGetConfigTest(TestCase):
    def setUp(self):
        int_dt = DataType.objects.get(name='Integer')

        config = Config(key='user.age', data_type=int_dt)
        config.set_value(42)
        config.save()

        config = Config(key='user.weight', data_type=int_dt, allow_template_use=False)
        config.set_value(100)
        config.save()

    def tearDown(self):
        _get_cache().clear()

    def do_test(self, template_str, expected):
        template = Template('{% load config %}' + template_str)
        result = template.render(Context())

        self.assertEqual(result, expected)


class FilterTest(BaseGetConfigTest):
    def test_exists(self):
        self.do_test("{{ 'user.age'|get_config|default:'unknown' }}", '42')

    def test_not_exists(self):
        self.do_test("{{ 'user.diameter'|get_config|default:'unknown' }}", 'unknown')

    def test_not_exists_empty(self):
        self.do_test("Hello{{ 'x'|get_config }}World", 'HelloWorld')

    def test_exists_not_allowed(self):
        self.do_test("{{ 'user.weight'|get_config|default:'unknown' }}", 'unknown')



class AssignmentTagTest(BaseGetConfigTest):
    def test_exists(self):
        self.do_test("{% get_config 'user.age' as age %}{{ age|default:'unknown' }}", '42')

    def test_not_exists(self):
        self.do_test("{% get_config 'user.diameter' as age %}{{ age|default:'unknown' }}", 'unknown')

    def test_not_exists_empty(self):
        self.do_test("{% get_config 'x' as x %}Hello{{ x }}World", 'HelloWorld')

    def test_exists_not_allowed(self):
        self.do_test("{% get_config 'user.weight' as age %}{{ age|default:'unknown' }}", 'unknown')
