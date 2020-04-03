# -*- coding: utf-8 -*-
import contextlib
import json
import os
import re
import unittest

from configparser import ConfigParser
from template.util import TemplateException
from uuid import uuid4

from KBaseReport.KBaseReportImpl import KBaseReport
from KBaseReport.utils.template_utils import render_template_to_file, _render_template
from KBaseReport.utils.validation_utils import validate_template_params

TEST_DATA = {
    'title':    { 'page_title': 'My First Template' },
    'content':  { 'value': ['this', 'that', 'the other'] },

    'template': '/kb/module/kbase_report_templates/views/test.tt',
    'scratch_dir': '/kb/module/work/tmp',
}

TEST_DATA['title_json'] = json.dumps(TEST_DATA['title'])
TEST_DATA['content_json'] = json.dumps(TEST_DATA['content'])

input_tests = [
    {   # missing required param
        'regex': "required field",
        'args': {},
    },
    {   # path does not exist
        'regex': "does not exist on filesystem",
        'args': {
            'template_file': '/does/not/exist',
        }
    },
    {   # wrong type
        'regex': "must be of string type",
        'args': {
            'template_file': { 'path': '/does/not/exist' },
        }
    },
    {   # invalid JSON
        'regex': "Invalid JSON",
        'args': {
            'template_data_json': '"this is not valid JSON',
            'template_file': 'data/template.tt',
        }
    },
    {   # invalid JSON
        'regex': "Invalid JSON",
        'args': {
            'template_data_json': '["this",{"is":"not"},{"valid":"json"]',
            'template_file': 'data/template.tt',
        }
    },
    {   # not in scratch dir
        'regex': "not in the scratch directory",
        'args': {
            'template_file': 'data/template.tt',
            'template_data_json': TEST_DATA['content_json'],
            'output_file': 'path/to/file',
        }
    }
]

content_test_content = [
    None,
    'title',
    'content',
]


@contextlib.contextmanager
def modified_environ(*remove, **update):
    """
    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


class TestTemplateRender(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Fake the callback URL for local testing
        with modified_environ(SDK_CALLBACK_URL='http://example.com'):

            config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
            cls.cfg = {}

            if (not config_file):
                cls.cfg = { 'scratch': TEST_DATA['scratch_dir'] }
            else:
                config = ConfigParser()
                config.read(config_file)
                for nameval in config.items('KBaseReport'):
                    cls.cfg[nameval[0]] = nameval[1]

            cls.scratch = cls.cfg['scratch']
            cls.serviceImpl = KBaseReport(cls.cfg)

    def getImpl(self):
        return self.__class__.serviceImpl


    def _title_check_rendering(self, string, has_title=False):
        no_title_compiled = re.compile('<title></title>')
        title_compiled = re.compile('<title>My First Template</title>')

        if (has_title):
            self.assertRegex(string, title_compiled)
            self.assertNotRegex(string, no_title_compiled)
        else:
            self.assertNotRegex(string, title_compiled)
            self.assertRegex(string, no_title_compiled)


    def _content_check_rendering(self, string, has_content=False):

        test_text = re.compile('This is a test.')

        no_value_text = re.compile('<div>The value is </div>')
        value_text = re.compile(
            '<div>The value is \[\s*[\"\']this[\"\'],\s*[\"\']that[\"\'],\s*[\"\']the other[\"\'],?\s*\]</div>')

        self.assertRegex(string, test_text)

        if (has_content):
            self.assertRegex(string, value_text)
            self.assertNotRegex(string, no_value_text)
        else:
            self.assertRegex(string, no_value_text)
            self.assertNotRegex(string, value_text)


    def check_rendering(self, string, params={}):

        title_bool = 'title' in params
        content_bool = 'content' in params
        self._title_check_rendering(string, title_bool)
        self._content_check_rendering(string, content_bool)


    def test_validate_template_params(self):
        """ test the input validation """
        for test_item in input_tests:
            with self.assertRaisesRegex(TypeError, test_item['regex']):
                validate_template_params(test_item['args'], self.scratch)

        # valid
        self.assertEqual(
            validate_template_params({
                'template_file': TEST_DATA['template'],
                'output_file': self.scratch + '/this/is/the/file.txt',
            }, self.scratch),
            {
                'template_file': TEST_DATA['template'],
                'template_data': {},
                'output_file': self.scratch + '/this/is/the/file.txt',
            }
        )

        self.assertEqual(
            validate_template_params({
                'template_file': TEST_DATA['template'],
                'template_data_json': TEST_DATA['content_json'],
                'output_file': self.scratch + '/this/is/the/file.txt',
            }, self.scratch),
            {
                'template_file': TEST_DATA['template'],
                'template_data': TEST_DATA['content'],
                'output_file': self.scratch + '/this/is/the/file.txt',
            }
        )


    def test__render_template(self):
        """ basic rendering test """
        with self.assertRaisesRegex(TemplateException,
            'file error - /does/not/exist: not found'):
            _render_template('/does/not/exist')

        for test_item in content_test_content:
            if (not test_item):
                # no title or content specified
                tmpl_str = _render_template(TEST_DATA['template'])
                self.check_rendering(tmpl_str)

            elif (test_item == 'title' or test_item == 'content'):
                tmpl_str = _render_template(TEST_DATA['template'], TEST_DATA[test_item])
                self.check_rendering(tmpl_str, { test_item: True })


    def test_render_template_to_file(self):
        """ test rendering and saving to a file """

        with self.assertRaisesRegex(TypeError, 'Missing required parameters'):
            render_template_to_file({ 'template_file': '/does/not/exist' })

        with self.assertRaisesRegex(TemplateException,
            'file error - /does/not/exist: not found'):
            render_template_to_file({
                'template_file': '/does/not/exist',
                'template_data': {},
                'output_file': 'whatever',
            })

        for test_item in content_test_content:

            test_args = {
                'template_file': TEST_DATA['template'],
                'output_file': self.scratch + '/temp_file-' + str(uuid4()) + '.txt'
            }
            if (test_item):
                test_args['template_data'] = TEST_DATA[test_item]
            else:
                test_args['template_data'] = {}

            new_file = render_template_to_file(test_args)

            self.assertEqual(new_file, { 'path': test_args['output_file'] })

            with open(new_file['path'], 'r') as f:
                # slurp file content
                all_the_text = f.read()

                if (test_item):
                    self.check_rendering(all_the_text, { test_item: True })
                else:
                    self.check_rendering(all_the_text)


    def test_impl_render_template(self):
        """ full Impl test: input validation, rendering, saving to file, return """

        self.assertEqual('http://example.com', self.getImpl().callback_url)

        for test_item in input_tests:
            with self.assertRaisesRegex(TypeError, test_item['regex']):
                self.getImpl().create_report_from_template({}, test_item['args'])

        for test_item in content_test_content:
            test_args = {
                'template_file': TEST_DATA['template'],
                'output_file': self.scratch + '/temp_file-' + str(uuid4()) + '.txt'
            }

            if (test_item):
                test_args['template_data_json'] = TEST_DATA[test_item + '_json']

            impl_output = self.getImpl().create_report_from_template({}, test_args)
            self.assertEqual(impl_output, [{ 'path': test_args['output_file'] }])

            new_file = impl_output[0]['path']

            with open(new_file, 'r') as f:
                # slurp file content
                all_the_text = f.read()

                if (test_item):
                    self.check_rendering(all_the_text, { test_item: True })
                else:
                    self.check_rendering(all_the_text)


if __name__ == '__main__':
    unittest.main()
