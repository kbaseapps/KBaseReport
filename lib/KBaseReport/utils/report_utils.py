# -*- coding: utf-8 -*-
from file_utils import fetch_or_upload_file_links, fetch_or_upload_html_links
import time as _time
from DataFileUtil.baseclient import ServerError as _DFUError
from uuid import uuid4

""" Utilities for creating reports using DataFileUtil """


def create_report(params, dfu):
    """
    Create a simple report
    :param params: see the KIDL spec for the create() parameters
    :param dfu: instance of DataFileUtil
    :return: report data
    """
    report_name = "report_" + str(uuid4())
    workspace_id = _get_workspace_id(dfu, params)
    # Empty defaults for merging
    report_data = {
        'objects_created': []
    }
    report_data.update(params['report'])
    save_object_params = {
        'id': workspace_id,
        'objects': [{
            'type': 'KBaseReport.Report',
            'data': report_data,
            'name': report_name,
            'meta': {},
            'hidden': 1
        }]
    }
    obj = _save_object(dfu, save_object_params)
    ref = _get_object_ref(obj)
    return {'ref': ref, 'name': report_name}


def create_extended(params, dfu):
    """
    Create an extended report
    This will upload files to shock if you provide scratch paths instead of shock_ids
    :param params: see the KIDL spec for create_extended_report() parameters
    :param dfu: instance of DataFileUtil
    :return: uploaded report data - {'ref': r, 'name': n}
    """
    file_links = params.get('file_links', [])
    html_links = params.get('html_links', [])
    files = fetch_or_upload_file_links(dfu, file_links)  # see ./file_utils.py
    html_files = fetch_or_upload_html_links(dfu, html_links)
    report_data = {
        'text_message': params.get('message'),
        'file_links': files,
        'html_links': html_files,
        'warnings': params.get('warnings'),
        'direct_html': params.get('direct_html'),
        'direct_html_link_index': params.get('direct_html_link_index'),
        'objects_created': params.get('objects_created', []),
        'html_window_height': params.get('html_window_height'),
        'summary_window_height': params.get('summary_window_height')
    }
    report_name = params.get('report_object_name', 'report_' + str(uuid4()))
    workspace_id = _get_workspace_id(dfu, params)
    save_object_params = {
        'id': workspace_id,
        'objects': [{
            'type': 'KBaseReport.Report',
            'data': report_data,
            'name': report_name,
            'meta': {},
            'hidden': 1
        }]
    }
    obj = _save_object(dfu, save_object_params)
    ref = _get_object_ref(obj)
    return {'ref': ref, 'name': report_name}


def _get_workspace_id(dfu, params):
    """
    Get the workspace ID from the params, which may either have 'workspace_id'
    or 'workspace_name'
    """
    if 'workspace_name' in params:
        return dfu.ws_name_to_id(params['workspace_name'])
    else:
        return params.get('workspace_id')


def _get_object_ref(obj):
    """ Get the reference string from an uploaded dfu object """
    return str(obj[6]) + '/' + str(obj[0]) + '/' + str(obj[4])


def _save_object(dfu, params):
    """ Save an object with DFU using error handling """
    try:
        return dfu.save_objects(params)[0]
    except _DFUError as err:
        print(str(_time.time()) + ' DataFileUtil exception: ' + str(err))
        raise err
    except Exception as err:
        print(str(_time.time()) + ' Unexpected DataFileUtil exception: ' + str(err))
        raise err
