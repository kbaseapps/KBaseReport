# -*- coding: utf-8 -*-
import os
from cerberus import Validator
import pprint
from json import JSONDecodeError
import json

pp = pprint.PrettyPrinter(indent=4)

"""
Utilities for validating parameters
We use the `cerberus` schema validation library: http://docs.python-cerberus.org
"""


def validate_simple_report_params(params):
    """ Validate all parameters to KBaseReportImpl#create """
    validator = Validator({
        'workspace_name': {'type': 'string', 'minlength': 1},
        'workspace_id': {'type': 'integer', 'min': 0},
        'report': {
            'type': 'dict',
            'required': True,
            'schema': {
                'text_message': {'type': 'string', 'nullable': True},
                'warnings': {
                    'type': 'list',
                    'schema': {'type': 'string'}
                },
                'objects_created': {
                    'type': 'list',
                    'schema': object_created_schema
                },
                'direct_html': {
                    'type': 'string',
                    'nullable': True
                }
            }
        }
    })
    _require_workspace_id_or_name(params)
    if not validator.validate(params):
        raise TypeError(_format_errors(validator.errors, params))
    return params


def validate_extended_report_params(params):
    """ Validate all parameters to KBaseReportImpl#create_extended_report """
    validator = Validator({
        'workspace_name': {'type': 'string', 'minlength': 1},
        'workspace_id': {'type': 'integer', 'min': 0},
        'message': {'type': 'string', 'nullable': True},
        'objects_created': {
            'type': 'list',
            'schema': object_created_schema,
        },
        'warnings': {
            'type': 'list',
            'schema': {'type': 'string'}
        },
        'html_links': {
            'type': 'list',
            'schema': extended_file_schema,
            'dependencies': 'direct_html_link_index',
            'excludes': 'template',
        },
        'file_links': {
            'type': 'list',
            'schema': extended_file_schema
        },
        'report_object_name': {'type': 'string', 'nullable': True},
        'html_window_height': {'type': 'integer', 'min': 1, 'nullable': True},
        'summary_window_height': {'type': 'integer', 'min': 1, 'nullable': True},
        'direct_html_link_index': {
            'type': 'integer',
            'min': 0,
            'nullable': True,
            'dependencies': 'html_links',
            'excludes': 'template',
        },
        'direct_html': {
            'type': 'string',
            'nullable': True,
            'excludes': 'template',
        },
        'template': {
            'type': 'dict',
            'excludes': ['direct_html', 'direct_html_link_index']
        },
    })
    _require_workspace_id_or_name(params)
    _validate_html_index(params.get('html_links', []), params.get('direct_html_link_index'))

    if not validator.validate(params):
        raise TypeError(_format_errors(validator.errors, params))
    return params


def validate_files(files):
    """
    Validate that every entry in `files` contains either a "shock_id" or "path"
    Raise an exception if any `path` value in `files` does not exist on the disk
    """
    def file_or_dir(path):
        return os.path.isfile(path) or os.path.isdir(path)
    for f in files:
        if ('path' not in f) and ('shock_id' not in f):
            err = {'path': ['required without shock_id'], 'shock_id': ['required without path']}
            raise TypeError(_format_errors(err, f))
        if ('path' in f) and (not file_or_dir(f['path'])):
            err = {'path': ['does not exist on filesystem']}
            raise ValueError(_format_errors(err, f))


def valid_dir_path(field, dir_path, error):
    """ ensure a directory exists """
    if (not os.path.isdir(dir_path)):
        error(field, 'does not exist on filesystem')

def valid_file_path(field, file_path, error):
    """ ensure a file exists """
    if (not os.path.isfile(file_path)):
        error(field, 'does not exist on filesystem')


def valid_json(field, string, error):
    try:
        template_data = json.loads(string)
    except JSONDecodeError as err:
        error(field, 'Invalid JSON: ' + err.msg + ' ' + str(err.pos))


def validate_template_params(params, config, with_output_file=False):
    """ Validate all parameters to KBaseReportImpl#render_template

    :param params:  (dict)  input to be validated
    :param config:  (dict)  app config
    :param with_output_file: (bool) whether or not the output_file param should be validated

    :return:
    params (dict) - validated params
    """
    validator = Validator(purge_unknown = True)

    config_validation_schema = {
        'scratch': {
            'type': 'string',
            'minlength': 2,
            'required': True,
            'validator': valid_dir_path,
        },
        'template_toolkit': {
            'type': 'dict',
        }
    }

    if not validator.validate(config, config_validation_schema):
        raise TypeError(_format_errors(validator.errors, config))

    validated_params = {
        'scratch': config['scratch'],
        'template_config': config['template_toolkit'] if 'template_toolkit' in config else {}
    }

    scratch_path = config['scratch']

    def path_contains_scratch(field, file_path, error):

        if file_path.find(scratch_path) != 0:
            error(field, 'is not in the scratch directory')

    tmpl_validation_schema = {
        'template_file': {
            'type': 'string',
            'minlength': 3,
            'required': True,
        },
        'template_data_json': {
            'type': 'string',
            'validator': valid_json,
        },
    }

    if with_output_file:
        tmpl_validation_schema['output_file'] = {
            'type': 'string',
            'minlength': len(scratch_path) + 2,
            'required': True,
            'validator': path_contains_scratch,
        }

    if not validator.validate(params, tmpl_validation_schema):
        raise TypeError(_format_errors(validator.errors, params))

    validated_tmpl_params = validator.document

    if 'template_data_json' in validated_tmpl_params:
        validated_tmpl_params['template_data'] = json.loads(validated_tmpl_params['template_data_json'])
        del validated_tmpl_params['template_data_json']
    else:
        validated_tmpl_params['template_data'] = {}

    # merge the two sets of validated params
    validated_params.update( validated_tmpl_params )

    return validated_params


def _require_workspace_id_or_name(params):
    """
    We need either workspace_id or workspace_name, but we don't need both
    cerberus doesn't have good syntax for that, so we do it manually
    """
    if ('workspace_id' not in params) and ('workspace_name' not in params):
        err = {
            'workspace_name': ['required without workspace_id'],
            'workspace_id': ['required without workspace_name']
        }
        raise TypeError(_format_errors(err, params))

    return params


def _validate_html_index(html_links, index):
    """
    Validate that the main file (html_link['name']) is present inside the html directory
    """
    if (index is None) or (not html_links):
        return
    try:
        html_link = html_links[index]
    except IndexError as err:
        print("".join([
            "direct_html_link_index is out of bounds for html_links. ",
            "The index is " + str(index),
            " while the length of html_links is " + str(len(html_links))
        ]))
        raise err
    if 'path' not in html_link:
        return
    # If they passed in a file, we don't need to validate
    if os.path.isfile(html_link['path']):
        return
    # If they passed a directory, check that the 'name' exists as a file inside that dir
    main_path = os.path.join(html_link['path'], html_link['name'])
    if not os.path.isfile(main_path):
        raise ValueError("".join([
            "For html_links, the 'name' key should be the filename of the ",
            "main HTML file for the report page (eg. 'index.html'). ",
            "The 'name' you provided was not found: ",
            html_link['name']
        ]))


def _format_errors(errors, params):
    """ Make human-readable error messages from a cerberus validation instance """
    # Create a bulleted list of each cerberus error message
    return "".join([
        "KBaseReport parameter validation errors:\n",
        pprint.pformat(errors),
        "\nYour parameters were:\n",
        pprint.pformat(params)
    ])


# Re-used validations

# Workspace object (corresponding to the KIDL spec's WorkspaceObject)
object_created_schema = {
    'type': 'dict',
    'schema': {
        'ref': {'required': True, 'type': 'string', 'minlength': 1},
        'description': {'type': 'string', 'nullable': True}
    }
}

# Type validation for .create's LinkedFile (see KIDL spec)
linked_file_schema = {
    'type': 'dict',
    'schema': {
        'handle': {'type': 'string', 'required': True},
        'description': {'type': 'string', 'nullable': True},
        'name': {'type': 'string', 'nullable': True},
        'label': {'type': 'string', 'nullable': True},
        'URL': {'type': 'string', 'minlength': 1, 'nullable': True}
    }
}

# Type validation for the extended report's File (see KIDL spec)
extended_file_schema = {
    'type': 'dict',
    'schema': {
        'name': {'type': 'string', 'nullable': True},
        'shock_id': {'type': 'string', 'nullable': True},
        'path': {'type': 'string', 'nullable': True},
        'description': {'type': 'string', 'nullable': True},
        'label': {'type': 'string', 'nullable': True}
    }
}
