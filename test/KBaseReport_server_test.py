# -*- coding: utf-8 -*-
import os
import shutil
import time
import unittest
from configparser import ConfigParser  # py3
from uuid import uuid4

from KBaseReport.KBaseReportImpl import KBaseReport
from KBaseReport.KBaseReportServer import MethodContext
from KBaseReport.authclient import KBaseAuth as _KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from test_template_utils import get_test_data

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

    def check_extended_result(self, result, link_name, file_names):
        """
        Test utility: check the file upload results for an extended report
        Args:
          result - result dictionary from running .create_extended_report
          link_name - one of "html_links" or "file_links"
          file_names - names of the files for us to check against
        Returns None
        """
        self.assertEqual(self.getImpl().status(self.getContext())[0]['state'], 'OK')
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        file_links = obj['data'][0]['data'][link_name]
        self.assertEqual(len(file_links), len(file_names))
        # Test that all the filenames listed in the report object map correctly
        saved_names = set([str(f['name']) for f in file_links])
        self.assertEqual(saved_names, set(file_names))

    def test_create(self):
        """ Test the simple report creation with valid data """
        msg = str(uuid4())
        result = self.getImpl().create(self.getContext(), {
            'workspace_name': self.getWsName(),
            'report': {'text_message': msg}
        })
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        self.assertEqual(self.getImpl().status(self.getContext())[0]['state'], 'OK')
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        data = obj['data'][0]['data']
        self.assertEqual(data['text_message'], msg)

    def test_create_with_workspace_id(self):
        """ Test the case where we pass in a workspace ID instead of a name """
        msg = str(uuid4())
        result = self.getImpl().create(self.getContext(), {
            'workspace_id': self.getWsID(),
            'report': {'text_message': msg}
        })
        self.assertTrue(len(result[0]['ref']))
        self.assertTrue(len(result[0]['name']))
        self.assertEqual(self.getImpl().status(self.getContext())[0]['state'], 'OK')
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        data = obj['data'][0]['data']
        self.assertEqual(data['text_message'], msg)

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
        with self.assertRaises(TypeError) as err:
            self.getImpl().create_extended_report(self.getContext(), {})

        with self.assertRaises(TypeError) as err:
            self.getImpl().create_extended_report(self.getContext(), {'workspace_name': 123})
        self.assertTrue(str(err.exception))

        # require both 'html_links' and 'direct_html_link_index'
        with self.assertRaisesRegex(TypeError, "html_links.*?field 'direct_html_link_index' is required"):
            self.getImpl().create_extended_report(self.getContext(), {
                'workspace_id': 12345,
                'html_links': [
                    {
                        'name': 'index.html',
                        'path': self.a_html_path
                    },
                    {
                        'name': 'b',
                        'path': self.b_html_path
                    }
                ],
            })

        with self.assertRaisesRegex(TypeError, "direct_html_link_index.*?field 'html_links' is required"):
            self.getImpl().create_extended_report(self.getContext(), {
                'workspace_id': 12345,
                'direct_html_link_index': 0,
            })


        # type error in the template params
        with self.assertRaisesRegex(TypeError, 'template.*?must be of dict type'):
            self.getImpl().create_extended_report(self.getContext(), {
                'workspace_id': 12345,
                'template': 'my_template_file.txt',
            })

        # too many params
        err_str = 'supply only one of "template", "direct_html", and '
        with self.assertRaisesRegex(ValueError, err_str):
            self.getImpl().create_extended_report(self.getContext(), {
                'workspace_id': 12345,
                'template': {},
                'direct_html': 'This is not valid html',
            })

        with self.assertRaisesRegex(ValueError, err_str):
            self.getImpl().create_extended_report(self.getContext(), {
                'workspace_id': 12345,
                'template': {
                    'this': 'that'
                },
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
                ],
            })


    def test_invalid_file_links(self):
        """ Test a file link path where the file is non-existent """
        file = {
            'name': 'a',
            'description': 'desc',
            'label': 'label',
            'path': 'tmp/no.txt'
        }
        with self.assertRaises(ValueError) as err:
            self.getImpl().create_extended_report(self.getContext(), {
                'workspace_name': self.getWsName(),
                'report_object_name': 'my_report',
                'file_links': [file]
            })
        self.assertTrue(len(str(err.exception)))

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
                {
                    'name': 'b',
                    'description': 'b',
                    'label': 'b',
                    'path': self.b_html_path
                }
            ]
        })
        self.check_extended_result(result, 'html_links', ['index.html', 'b'])

    def test_invalid_extended_report_with_html_paths(self):
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
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        self.assertEqual(obj['data'][0]['data']['direct_html'], direct_html)

    def test_direct_html_none(self):
        """ Test the case where they pass None for the direct_html param """
        params = {
            'workspace_name': self.getWsName(),
            'message': 'hello world',
            'direct_html': None,
        }
        result = self.getImpl().create_extended_report(self.getContext(), params)
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        self.assertEqual(obj['data'][0]['data']['direct_html'], None)

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
            'direct_html': None,
        })
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        direct_html = obj['data'][0]['data']['direct_html']
        self.assertEqual(direct_html.rstrip(), ref_text['abs_path'])

        # relative path to template file
        result = self.getImpl().create_extended_report(self.getContext(), {
            'workspace_id': self.getWsID(),
            'template': {
                'template_file': TEST_DATA['template_file'],
                'template_data_json': TEST_DATA['content_json'],
            },
            'direct_html': None,
        })
        obj = self.dfu.get_objects({'object_refs': [result[0]['ref']]})
        direct_html = obj['data'][0]['data']['direct_html']
        self.assertEqual(direct_html.rstrip(), ref_text['rel_path'])


