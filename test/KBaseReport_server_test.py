# -*- coding: utf-8 -*-
import os
import shutil
import time
import unittest
from configparser import ConfigParser  # py3
from uuid import uuid4

from template.util import TemplateException
from KBaseReport.KBaseReportImpl import KBaseReport
from KBaseReport.KBaseReportServer import MethodContext
from KBaseReport.authclient import KBaseAuth as _KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from TemplateUtil_test import get_test_data


class KBaseReportTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('KBaseReport'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'KBaseReport',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = KBaseReport(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        # Custom stuff below
        dirname = os.path.dirname(__file__)
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.a_html_path = os.path.join(cls.scratch, 'a_html')
        cls.b_html_path = os.path.join(cls.scratch, 'b_html')
        shutil.copytree(os.path.join(dirname, 'data', 'a_html'), cls.a_html_path)
        shutil.copytree(os.path.join(dirname, 'data', 'b_html'), cls.b_html_path)
        cls.a_file_path = os.path.join(cls.scratch, 'a.txt')
        cls.b_file_path = os.path.join(cls.scratch, 'b.txt')
        shutil.copy2(os.path.join(dirname, 'data/a.txt'), cls.a_file_path)
        shutil.copy2(os.path.join(dirname, 'data/b.txt'), cls.b_file_path)
        # Upload files to shock
        cls.a_file_shock = cls.dfu.file_to_shock({
            'file_path': cls.a_file_path, 'make_handle': 0
        })
        cls.b_file_shock = cls.dfu.file_to_shock({
            'file_path': cls.b_file_path, 'make_handle': 0
        })

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_KBaseReport_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        self.__class__.wsID = ret[0]
        return wsName

    def getWsID(self):
        """
        Return the workspace ID.
        NOTE that this is custom to this SDK app (not auto-generated)
        """
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsID
        self.getWsName()  # Sets the ID
        return self.__class__.wsID

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def check_created_report(self, result):
        """ basic checks on a created report
        Args:
          result: output from report creation call
        Return:
          object data from created report
        """
        self.assertEqual(self.getImpl().status(self.getContext())[0]['state'], 'OK')
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        return obj['data'][0]['data']

    def check_extended_result(self, result, link_name, file_names):
        """
        Test utility: check the file upload results for an extended report
        Args:
          result - result dictionary from running .create_extended_report
          link_name - one of "html_links" or "file_links"
          file_names - names of the files for us to check against
        Returns:
            obj - report object created
        """
        obj = self.check_created_report(result)
        file_links = obj[link_name]
        self.assertEqual(len(file_links), len(file_names))
        # Test that all the filenames listed in the report object map correctly
        saved_names = set([str(f['name']) for f in file_links])
        self.assertEqual(saved_names, set(file_names))
        return obj

    def check_validation_errors(self, params, error_list):
        """
        Check that the appropriate errors are thrown when validating extended report params
        Args:
          params - parameters to create_extended_report
          error_list - set of text regexes to check against the error string
        Returns True
        """
        err_str = 'KBaseReport parameter validation errors'
        with self.assertRaisesRegex(TypeError, err_str) as cm:
            self.getImpl().create_extended_report(self.getContext(), params)

        error_message = str(cm.exception)
        for e in error_list:
            self.assertRegex(error_message, e)

        return True

    def test_create(self):
        """ Test the simple report creation with valid data """
        msg = str(uuid4())
        result = self.getImpl().create(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report': {'text_message': msg}
        })
        data = self.check_created_report(result)
        self.assertEqual(data['text_message'], msg)

    def test_create_with_workspace_id(self):
        """ Test the case where we pass in a workspace ID instead of a name """
        msg = str(uuid4())
        result = self.getImpl().create(self.getContext(), {
            'workspace_id': self.getWsID(),
            'report': {'text_message': msg}
        })
        data = self.check_created_report(result)
        self.assertEqual(data['text_message'], msg)

    def test_create_html_report(self):
        """ Test the case where we pass in HTML instead of text_message """

        html = '<blink><u>Deprecated</u></blink><nobr>'
        result = self.getImpl().create(self.getContext(), {
            'workspace_id': self.getWsID(),
            'report': {'direct_html': html}
        })
        data = self.check_created_report(result)
        self.assertEqual(data['direct_html'], html)

    def test_create_html_report_and_message(self):
        """ Test creation of a message AND an HTML report (!) """
        msg = str(uuid4())
        html = '<blink><u>Deprecated</u></blink><nobr>'
        result = self.getImpl().create(self.getContext(), {
            'workspace_id': self.getWsID(),
            'report': {'direct_html': html, 'text_message': msg}
        })
        data = self.check_created_report(result)
        self.assertEqual(data['direct_html'], html)
        self.assertEqual(data['text_message'], msg)

    def test_create_report_from_template(self):
        """ Test the creation of a simple report using a template to generate data """
        TEST_DATA = get_test_data()
        for test_item in TEST_DATA['render_test'].keys():
            desc = test_item if test_item is not None else 'none'
            ref_text = TEST_DATA['render_test'][test_item]

            with self.subTest('test content: ' + desc):
                test_args = {
                    'template_file': TEST_DATA['template'],
                }
                if test_item:
                    test_args['template_data_json'] = TEST_DATA[test_item + '_json']

                result = self.getImpl().create(self.getContext(), {
                    'workspace_id': self.getWsID(),
                    'report': {
                        'template': test_args
                    },
                })
                data = self.check_created_report(result)
                self.assertMultiLineEqual(data['direct_html'], ref_text['abs_path'])

    def test_create_param_errors(self):
        """
        See lib/KBaseReport/utils/validation_utils
        We aren't testing every validation rule exhaustively here
        """
        # Missing workspace id and name
        with self.assertRaises(TypeError) as err:
            self.getImpl().create(self.getContext(), {'report': {}})
        # Missing report
        with self.assertRaises(TypeError) as err:
            self.getImpl().create(self.getContext(), {'workspace_name': 'x'})
        self.assertTrue(str(err.exception))

    def test_create_extended_param_errors(self):
        """
        See lib/KBaseReport/utils/validation_utils
        We aren't testing every validation rule exhaustively here
        """
        # Missing workspace id and name
        self.check_validation_errors({}, [
            "'workspace_id'.*?'required without workspace_name'",
            "'workspace_name'.*?'required without workspace_id'",
        ])

        # wrong type for workspace_name
        self.check_validation_errors({'workspace_name': 123}, [
            "'workspace_name'.*?'must be of string type'",
        ])

    def test_create_more_extended_param_errors(self):
        """
        See lib/KBaseReport/utils/validation_utils
        We aren't testing every validation rule exhaustively here
        """
        html_links = [
            {
                'name': 'index.html',
                'path': self.a_html_path
            },
            {
                'name': 'b',
                'path': self.b_html_path
            }
        ]

        # require both 'html_links' and 'direct_html_link_index'
        params = {
            'workspace_id': self.getWsID(),
            'html_links': html_links,
        }
        self.check_validation_errors(params, [
            "html_links.*?field 'direct_html_link_index' is required"
        ])

        params = {
            'workspace_id': self.getWsID(),
            'direct_html_link_index': 0,
        }
        self.check_validation_errors(params, [
            "direct_html_link_index.*?field 'html_links' is required"
        ])

        # type error in the template params
        params = {
            'workspace_id': self.getWsID(),
            'template': 'my_template_file.txt',
        }
        self.check_validation_errors(params, ['template.*?must be of dict type'])

        # no template + direct_html
        params = {
            'workspace_id': self.getWsID(),
            'template': {},
            'direct_html': 'This is not valid html',
        }
        self.check_validation_errors(params, [
            "'template' must not be present with 'direct_html'",
            "'template'.*?'direct_html', 'direct_html_link_index' must not be present",
        ])

        # no template + direct_html_link_index
        params = {
            'workspace_id': self.getWsID(),
            'template': {'this': 'that'},
            'direct_html_link_index': 0,
            'html_links': html_links,
        }
        self.check_validation_errors(params, [
            "'direct_html_link_index'.*?'template' must not be present with ",
            "'template'.*?'direct_html', 'direct_html_link_index' must not be present"
        ])

        # missing direct_html_link_index
        # no direct_html + template
        # no template + html_links
        params = {
            'workspace_id': self.getWsID(),
            'template': {'this': 'that'},
            'direct_html': '<marquee>My fave HTML tag</marquee>',
            'html_links': html_links,
        }
        self.check_validation_errors(params, [
            "'template' must not be present with 'html_links'",
            "'direct_html'.*?'template' must not be present with ",
            "template.*?'direct_html', 'direct_html_link_index' must not be present",
            "field 'direct_html_link_index' is required",
        ])

    def test_invalid_file_html_links(self):
        """ Errors connected with file and html links """
        for link_type in ['html_links', 'file_links']:

            err_list = []
            if 'html_links' == link_type:
                err_list = ["html_links.*?field 'direct_html_link_index' is required"]
            # file errors: no name
            params = {
                'workspace_id': self.getWsID(),
                link_type: [
                    {'path': 'does/not/exist'},
                ],
            }
            self.check_validation_errors(params, [
                "'name':.*?'required field'",
                "path.*?does not exist on filesystem"
            ] + err_list)

            # file error: no location
            params = {
                'workspace_id': self.getWsID(),
                link_type: [
                    {'path': self.a_file_path, 'name': 'a'},
                    {'name': 'b'},
                ],
            }
            self.check_validation_errors(params, [
                "'path'.*?'required field'",
                "'shock_id'.*?'required field'",
                "'template'.*?'required field'"
            ] + err_list)

            # invalid path
            file = {
                'name': 'a',
                'description': 'desc',
                'label': 'label',
                'path': 'tmp/no.txt'
            }
            params = {
                'workspace_name': self.getWsName(),
                'report_object_name': 'my_report',
                link_type: [file]
            }
            self.check_validation_errors(params, [
                "'path'.*?'does not exist on filesystem'",
            ] + err_list)

            # template-related errors
            template_error_list = [
                {
                    'desc': 'missing required param',
                    'regex': "required field",
                    'params': {},
                },
                {
                    'desc': 'template file is wrong type',
                    'regex': "must be of string type",
                    'params': {
                        'template_file': {'path': '/does/not/exist'},
                    }
                },
                {
                    'desc': 'invalid JSON',
                    'regex': "Invalid JSON",
                    'params': {
                        'template_data_json': '"this is not valid JSON',
                    }
                },
                {
                    'desc': 'invalid JSON',
                    'regex': "Invalid JSON",
                    'params': {
                        'template_data_json': '["this",{"is":"not"},{"valid":"json"]',
                    }
                },
            ]

            for tpl_err in template_error_list:
                params = {
                    'workspace_id': 12345,
                    'report_object_name': 'my_report',
                    link_type: [
                        {'template': tpl_err['params'], 'name': 'file.txt'},
                        {'path': self.a_file_path, 'name': 'a'},
                    ]
                }
                self.check_validation_errors(params, [tpl_err['regex']] + err_list)

        for path in ['/does/not/exist', 'does/not/exist']:
            with self.assertRaisesRegex(TemplateException, 'file error - ' + path + ': not found'):
                self.getImpl().create_extended_report(self.getContext(), {
                    'template': {
                        'template_file': path,
                    },
                    'workspace_id': 12345,
                })

    def test_create_extended_report_with_file_paths(self):
        """ Valid extended report with file_links """
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'label': 'a',
                    'path': self.a_file_path
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'path': self.b_file_path
                }
            ]
        })
        self.check_extended_result(result, 'file_links', ['a', 'b'])

    def test_create_extended_report_with_uploaded_files(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'label': 'a',
                    'shock_id': self.a_file_shock['shock_id']
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'label': 'b',
                    'shock_id': self.b_file_shock['shock_id']
                }
            ]
        })
        self.check_extended_result(result, 'file_links', ['a', 'b'])

    def test_create_extended_report_with_uploaded_html_files(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'direct_html_link_index': 0,
            'html_links': [
                {
                    'name': 'a',
                    'description': 'a',
                    'label': 'a',
                    'shock_id': self.a_file_shock['shock_id']
                },
                {
                    'name': 'b',
                    'description': 'b',
                    'label': 'b',
                    'shock_id': self.b_file_shock['shock_id']
                }
            ]
        })
        self.check_extended_result(result, 'html_links', ['a', 'b'])

    def test_create_extended_report_with_html_paths(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'direct_html_link_index': 0,
            'html_links': [
                {
                    'name': 'index.html',
                    'path': self.a_html_path
                },
                {
                    'name': 'b',
                    'path': self.b_html_path
                }
            ]
        })
        self.check_extended_result(result, 'html_links', ['index.html', 'b'])

    def test_create_extended_report_with_templates(self):
        """ test the creation of extended reports using `template` directives """
        TEST_DATA = get_test_data()
        tmpl_arr = [
            {
                'name': 'none',
                'template': {
                    'template_file': TEST_DATA['template'],
                },
            },
            {
                'name': 'content',
                'template': {
                    'template_file': TEST_DATA['template'],
                    'template_data_json': TEST_DATA['content_json'],
                },
            },
            {
                'name': 'title',
                'template': {
                    'template_file': TEST_DATA['template'],
                    'template_data_json': TEST_DATA['title_json'],
                },
            }
        ]
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'direct_html_link_index': 0,
            'html_links': tmpl_arr,
        })
        self.check_extended_result(result, 'html_links', ['none', 'content', 'title'])

        # use the same templates to generate files
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'file_links': tmpl_arr,
        })
        self.check_extended_result(result, 'file_links', ['none', 'content', 'title'])

    def test_create_extended_report_with_html_single_file(self):
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report_object_name': 'my_report',
            'direct_html_link_index': 0,
            'html_links': [
                {
                    'name': 'index.html',
                    'description': 'a',
                    'label': 'a',
                    'path': self.a_html_path
                },
            ]
        })
        self.check_extended_result(result, 'html_links', ['index.html'])

    def test_valid_extended_report_with_html_paths(self):
        """ Test the case where they set a single HTML file as their 'path' """
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'direct_html_link_index': 0,
            'html_links': [
                {
                    'name': 'main.html',
                    'path': os.path.join(self.a_html_path, 'index.html')
                }
            ]
        })
        self.check_extended_result(result, 'html_links', ['main.html'])

    def test_html_direct_link_index_out_of_bounds(self):
        """ Test the case where they pass an out of bounds html index """
        params = {
            'workspace_name': self.getWsName(),
            'direct_html_link_index': 1,
            'html_links': [{'name': 'index.html', 'path': self.a_html_path}]
        }
        with self.assertRaises(IndexError):
            self.getImpl().create_extended_report(self.getContext(), params)

    def test_direct_html(self):
        """ Test the case where they pass in direct_html """
        direct_html = '<p>Hello, world.</p>'
        params = {
            'workspace_name': self.getWsName(),
            'direct_html': direct_html
        }

        result = self.getImpl().create_extended_report(self.getContext(), params)
        report_data = self.check_created_report(result)
        self.assertEqual(report_data['direct_html'], direct_html)

    def test_direct_html_none(self):
        """ Test the case where they pass None for the direct_html param """
        params = {
            'workspace_name': self.getWsName(),
            'message': 'hello world',
            'direct_html': None,
        }
        result = self.getImpl().create_extended_report(self.getContext(), params)
        report_data = self.check_created_report(result)
        self.assertEqual(report_data['direct_html'], None)

    def test_template(self):
        """ Test the case where they want to use a template to generate HTML"""
        TEST_DATA = get_test_data()
        ref_text = TEST_DATA['render_test']['content']
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_name': self.getWsName(),
            'workspace_id': self.getWsID(),
            'template': {
                'template_file': TEST_DATA['template'],
                'template_data_json': TEST_DATA['content_json'],
            },
        })
        report_data = self.check_created_report(result)
        direct_html = report_data['direct_html']
        self.assertEqual(direct_html.rstrip(), ref_text['abs_path'])

        # relative path to template file
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_id': self.getWsID(),
            'template': {
                'template_file': TEST_DATA['template_file'],
                'template_data_json': TEST_DATA['content_json'],
            },
        })
        report_data = self.check_created_report(result)
        direct_html = report_data['direct_html']
        self.assertEqual(direct_html.rstrip(), ref_text['rel_path'])
