# -*- coding: utf-8 -*-
import os
import shutil
from uuid import uuid4

from validation_utils import validate_files

"""
Utilities for fetching/uploading files
We use an instance of DataFileUtil here
"""


def fetch_or_upload_file_links(dfu, files):
    """
    Given a list of dictionaries of files for the `file_links` parameter in an extended_report
    Fetch by shock ID or upload the file or zipped directory
    :param dfu: DataFileUtil client instance
    :param files: list of file dictionaries (having the File type from the KIDL spec)
    :return: list of file dictionaries that that can be uploaded to the workspace for the report
    """
    out_files = []
    validate_files(files)  # Assures that every file has either a 'path' or 'shock_id'
    for each_file in files:
        if 'path' in each_file:
            # Only zip if the path is a directory
            isdir = os.path.isdir(each_file['path'])
            shock = dfu.file_to_shock({
                'file_path': each_file['path'],
                'make_handle': 1,
                'pack': 'zip' if isdir else None
            })
        elif 'shock_id' in each_file:
            # Having a 'shock_id' means it is already uploaded
            shock = dfu.own_shock_node({'shock_id': each_file['shock_id'], 'make_handle': 1})
        out_files.append(_create_file_link(each_file, shock))
    return out_files


def fetch_or_upload_html_links(dfu, files):
    """
    Given a list of dictionaries of files that each have either 'path' or 'shock_id'
    Fetch by shock ID or upload a zipped directory
    :param dfu: DataFileUtil client instance
    :param files: list of file dictionaries (having the File type from the KIDL spec)
    :return: list of file dictionaries that that can be uploaded to the workspace for the report
    """
    out_files = []
    validate_files(files)  # Assures that every file has either a 'path' or 'shock_id'
    for each_file in files:
        if 'path' in each_file:
            # Having a 'path' key means we have to upload to shock
            if os.path.isfile(each_file['path']):
                # If it is not a directory, we have to move it into one before zipping
                new_dir = os.path.join(os.path.dirname(each_file['path']), str(uuid4()))
                os.makedirs(new_dir)
                os.chmod(new_dir, 0o775)
                # Move the file to dir/name
                new_path = os.path.join(new_dir, each_file['name'])
                shutil.copy2(each_file['path'], new_path)
                each_file['path'] = new_dir
            shock = dfu.file_to_shock({
                'file_path': each_file['path'],
                'make_handle': 1,
                'pack': 'zip'  # Always zip for HTML
            })
        elif 'shock_id' in each_file:
            # Having a 'shock_id' means it is already uploaded
            shock = dfu.own_shock_node({'shock_id': each_file['shock_id'], 'make_handle': 1})
        out_files.append(_create_file_link(each_file, shock))
    return out_files


def _create_file_link(file_data, shock):
    """ This corresponds to the LinkedFile type in the KIDL spec """
    return {
        'handle': shock['handle']['hid'],
        'description': file_data.get('description'),
        'name': file_data.get('name', ''),
        'label': file_data.get('label', ''),
        'URL': shock['handle']['url'] + '/node/' + shock['handle']['id']
    }
