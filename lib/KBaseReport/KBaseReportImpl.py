# -*- coding: utf-8 -*-
#BEGIN_HEADER
from DataFileUtil.DataFileUtilClient import DataFileUtil
import utils.report_utils as report_utils
from utils.validation_utils import validate_simple_report_params, validate_extended_report_params
import os
#END_HEADER


class KBaseReport:
    '''
    Module Name:
    KBaseReport

    Module Description:
    Module for workspace data object reports, which show the results of running a job in an SDK app.
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "3.0.0"
    GIT_URL = "https://github.com/jayrbolton/KBaseReport"
    GIT_COMMIT_HASH = "HEAD"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.dfu = DataFileUtil(self.callback_url)
        #END_CONSTRUCTOR
        pass


    def create(self, ctx, params):
        """
        Function signature for the create() method -- generate a report for an app run.
        create_extended() is the preferred method if you have html_links and
        file_links, but this is still provided for backwards compatibility.
        @deprecated KBaseReport.create_extended_report
        :param params: instance of type "CreateParams" (* Parameters for the
           create() method * Pass in *either* workspace_name or workspace_id
           -- only one is needed * Required arguments: *     SimpleReport
           report *     string workspace_name - needed if workspace_id is
           blank. Note that this may change. *     int workspace_id - needed
           if workspace_name is blank. Preferred as it is immutable.) ->
           structure: parameter "report" of type "SimpleReport" (* A simple
           report for use in create() * Required arguments: *     string
           text_message - Readable plain-text report message * Optional
           arguments: *     list<WorkspaceObject> objects_created - List of
           result workspace objects that this app *         has created. They
           will get linked in the report view. *     list<string> warnings -
           A list of plain-text warning messages *     string direct_html -
           simple html text that will be rendered within the report widget *
           @optional text_message warnings objects_created * @metadata ws
           length(warnings) as Warnings * @metadata ws length(text_message)
           as Message Length * @metadata ws length(objects_created) as
           Objects Created) -> structure: parameter "text_message" of String,
           parameter "warnings" of list of String, parameter
           "objects_created" of list of type "WorkspaceObject" (* Represents
           a Workspace object with some brief description text * that can be
           associated with the object. * Required arguments: *     ws_id ref
           - workspace ID * Optional arguments: *     string description - A
           plaintext, human-readable description of the *         object
           created. * @optional description) -> structure: parameter "ref" of
           type "ws_id" (* Workspace ID reference - eg. 'ws/id/ver' * @id
           ws), parameter "description" of String, parameter "workspace_name"
           of String, parameter "workspace_id" of Long
        :returns: instance of type "ReportInfo" (* The reference to the saved
           KBaseReport. This is the return object for * both create() and
           create_extended() * Returned data: *    ws_id ref - reference to a
           workspace object in the form of *       
           workspace_id/object_id/version. This is a reference to the saved
           data *        from creating the report. *    string name -
           Plaintext unique name for the report. In *        create_extended,
           this can optionally be set in a parameter.) -> structure:
           parameter "ref" of type "ws_id" (* Workspace ID reference - eg.
           'ws/id/ver' * @id ws), parameter "name" of String
        """
        # ctx is the context object
        # return variables are: info
        #BEGIN create
        # Validate params
        params = validate_simple_report_params(params)
        info = report_utils.create_report(params, self.dfu)
        #END create

        # At some point might do deeper type checking...
        if not isinstance(info, dict):
            raise ValueError('Method create return value ' +
                             'info is not type dict as required.')
        # return the results
        return [info]

    def create_extended_report(self, ctx, params):
        """
        Create a report for the results of an app run -- handles file and html zipping/uploading
        If you are using html_links or file_links, this will be more user-friendly than create()
        :param params: instance of type "CreateExtendedReportParams" (*
           Parameters used to create a more complex report with file and html
           links * * All parameters are optional. * * string message - Simple
           text message to store in report object * list<WorkspaceObject>
           objects_created - List of result workspace objects that this app *
           has created. They will get linked in the report view. *
           list<string> warnings - A list of plain-text warning messages *
           list<File> html_links - A list of paths or shock IDs pointing to
           html files or directories. *     if you pass in paths, they will
           be zipped and uploaded * int direct_html_link_index - Index in
           html_links to set the direct/default view in the *     report
           (ignored if direct_html is present). * string direct_html - simple
           html text that will be rendered within the report widget *     If
           you pass in both direct_html and html_links, then direct_html will
           be ignored. * list<File> file_links - a list of file paths or
           shock node IDs. Allows the user to *     specify files that the
           report widget should link for download. * string
           report_object_name - name to use for the report object *     (will
           be auto-generated if unspecified) * html_window_height - fixed
           height in pixels of the html window for the report *
           summary_window_height - fixed height in pixels of the summary
           window for the report * string workspace_name - name of workspace
           where object should be saved. *     Required if workspace_id is
           not present. * int workspace_id - id of workspace where object
           should be saved. *     Required if workspace_name is not present.
           * * @optional message objects_created warnings html_links
           direct_html direct_html_link_index file_links report_object_name
           html_window_height summary_window_height) -> structure: parameter
           "message" of String, parameter "objects_created" of list of type
           "WorkspaceObject" (* Represents a Workspace object with some brief
           description text * that can be associated with the object. *
           Required arguments: *     ws_id ref - workspace ID * Optional
           arguments: *     string description - A plaintext, human-readable
           description of the *         object created. * @optional
           description) -> structure: parameter "ref" of type "ws_id" (*
           Workspace ID reference - eg. 'ws/id/ver' * @id ws), parameter
           "description" of String, parameter "warnings" of list of String,
           parameter "html_links" of list of type "File" (* A file to be
           linked in the report. Pass in *either* a shock_id or a * path. If
           a path to a file is given, then the file will be uploaded. If a *
           path to a directory is given, then it will be zipped and uploaded.
           * Required arguments: *     string path - Can be a file or
           directory path. Required if shock_id is absent. *     string
           shock_id - Shock node ID. Required if path is absent. *     string
           name - Plain-text file name -- shown to the user. * Optional
           arguments: *     string description - A plaintext, human-readable
           description of the file. * @optional description) -> structure:
           parameter "path" of String, parameter "shock_id" of String,
           parameter "name" of String, parameter "description" of String,
           parameter "direct_html" of String, parameter
           "direct_html_link_index" of Long, parameter "file_links" of list
           of type "File" (* A file to be linked in the report. Pass in
           *either* a shock_id or a * path. If a path to a file is given,
           then the file will be uploaded. If a * path to a directory is
           given, then it will be zipped and uploaded. * Required arguments:
           *     string path - Can be a file or directory path. Required if
           shock_id is absent. *     string shock_id - Shock node ID.
           Required if path is absent. *     string name - Plain-text file
           name -- shown to the user. * Optional arguments: *     string
           description - A plaintext, human-readable description of the file.
           * @optional description) -> structure: parameter "path" of String,
           parameter "shock_id" of String, parameter "name" of String,
           parameter "description" of String, parameter "report_object_name"
           of String, parameter "html_window_height" of Double, parameter
           "summary_window_height" of Double, parameter "workspace_name" of
           String, parameter "workspace_id" of Long
        :returns: instance of type "ReportInfo" (* The reference to the saved
           KBaseReport. This is the return object for * both create() and
           create_extended() * Returned data: *    ws_id ref - reference to a
           workspace object in the form of *       
           workspace_id/object_id/version. This is a reference to the saved
           data *        from creating the report. *    string name -
           Plaintext unique name for the report. In *        create_extended,
           this can optionally be set in a parameter.) -> structure:
           parameter "ref" of type "ws_id" (* Workspace ID reference - eg.
           'ws/id/ver' * @id ws), parameter "name" of String
        """
        # ctx is the context object
        # return variables are: info
        #BEGIN create_extended_report
        params = validate_extended_report_params(params)
        info = report_utils.create_extended(params, self.dfu)
        #END create_extended_report

        # At some point might do deeper type checking...
        if not isinstance(info, dict):
            raise ValueError('Method create_extended_report return value ' +
                             'info is not type dict as required.')
        # return the results
        return [info]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
