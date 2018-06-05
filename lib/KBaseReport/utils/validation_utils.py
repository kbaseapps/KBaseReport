# -*- coding: utf-8 -*-
import os
from cerberus import Validator
import pprint

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
                'text_message': {'type': 'string'},
                'warnings': {
                    'type': 'list',
                    'schema': {'type': 'string'}
                },
                'objects_created': {
                    'type': 'list',
                    'schema': object_created_schema
                },
                'direct_html': {
                    'type': 'string'
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
        'message': {'type': 'string'},
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
            'schema': extended_file_schema
        },
        'file_links': {
            'type': 'list',
            'schema': extended_file_schema
        },
        'report_object_name': {'type': 'string'},
        'html_window_height': {'type': 'integer', 'min': 1},
        'summary_window_height': {'type': 'integer', 'min': 1},
        'direct_html_link_index': {'type': 'integer', 'min': 0},
        'direct_html': {'type': 'string'}
    })
    _validate_html_index(params.get('html_links', []), params.get('direct_html_link_index'))
    _require_workspace_id_or_name(params)
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
        "You parameters were:\n",
        pprint.pformat(params)
    ])

# Re-used validations

# Workspace object (corresponding to the KIDL spec's WorkspaceObject)
object_created_schema = {
    'type': 'dict',
    'schema': {
        'ref': {'required': True, 'type': 'string', 'minlength': 1},
        'description': {'type': 'string'}
    }
}

# Type validation for .create's LinkedFile (see KIDL spec)
linked_file_schema = {
    'type': 'dict',
    'schema': {
        'handle': {'type': 'string'},
        'description': {'type': 'string'},
        'name': {'type': 'string'},
        'label': {'type': 'string'},
        'URL': {'type': 'string', 'minlength': 1}
    }
}

# Type validation for the extended report's File (see KIDL spec)
extended_file_schema = {
    'type': 'dict',
    'schema': {
        'name': {'type': 'string'},
        'shock_id': {'type': 'string'},
        'path': {'type': 'string'},
        'description': {'type': 'string'}
    }
}
