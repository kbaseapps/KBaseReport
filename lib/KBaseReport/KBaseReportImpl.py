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
    GIT_COMMIT_HASH = "863d208f13988489eb539c475694da1bf1abea76"

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
        Function signature for the create() method -- generate a simple,
        text-based report for an app run.
        @deprecated KBaseReport.create_extended_report
        :param params: instance of type "CreateParams" (* Parameters for the
           create() method * * Pass in *either* workspace_name or
           workspace_id -- only one is needed. * Note that workspace_id is
           preferred over workspace_name because workspace_id immutable. * *
           Required arguments: *     SimpleReport report - See the structure
           above *     string workspace_name - Workspace name of the running
           app. Required *         if workspace_id is absent *     int
           workspace_id - Workspace ID of the running app. Required if *     
           workspace_name is absent) -> structure: parameter "report" of type
           "SimpleReport" (* A simple report for use in create() * Optional
           arguments: *     string text_message - Readable plain-text report
           message *     string direct_html - Simple HTML text that will be
           rendered within the report widget *     list<string> warnings - A
           list of plain-text warning messages *     list<WorkspaceObject>
           objects_created - List of result workspace objects that this app *
           has created. They will get linked in the report view) ->
           structure: parameter "text_message" of String, parameter
           "direct_html" of String, parameter "warnings" of list of String,
           parameter "objects_created" of list of type "WorkspaceObject" (*
           Represents a Workspace object with some brief description text *
           that can be associated with the object. * Required arguments: *   
           ws_id ref - workspace ID in the format
           'workspace_id/object_id/version' * Optional arguments: *    
           string description - A plaintext, human-readable description of
           the *         object created) -> structure: parameter "ref" of
           type "ws_id" (* Workspace ID reference in the format
           'workspace_id/object_id/version' * @id ws), parameter
           "description" of String, parameter "workspace_name" of String,
           parameter "workspace_id" of Long
        :returns: instance of type "ReportInfo" (* The reference to the saved
           KBaseReport. This is the return object for * both create() and
           create_extended() * Returned data: *    ws_id ref - reference to a
           workspace object in the form of *       
           'workspace_id/object_id/version'. This is a reference to a saved *
           Report object (see KBaseReportWorkspace.spec) *    string name -
           Plaintext unique name for the report. In *        create_extended,
           this can optionally be set in a parameter) -> structure: parameter
           "ref" of type "ws_id" (* Workspace ID reference in the format
           'workspace_id/object_id/version' * @id ws), parameter "name" of
           String
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
        Create a report for the results of an app run. This method handles file
        and HTML zipping, uploading, and linking as well as HTML rendering.
        :param params: instance of type "CreateExtendedReportParams" (*
           Parameters used to create a more complex report with file and HTML
           links * * Pass in *either* workspace_name or workspace_id -- only
           one is needed. * Note that workspace_id is preferred over
           workspace_name because workspace_id immutable. * * Required
           arguments: *     string workspace_name - Name of the workspace
           where the report *         should be saved. Required if
           workspace_id is absent *     int workspace_id - ID of workspace
           where the report should be saved. *         Required if
           workspace_name is absent * Optional arguments: *     string
           message - Simple text message to store in the report object *    
           list<WorkspaceObject> objects_created - List of result workspace
           objects that this app *         has created. They will be linked
           in the report view *     list<string> warnings - A list of
           plain-text warning messages *     list<File> html_links - A list
           of paths or shock IDs pointing to HTML files or directories. *    
           If you pass in paths to directories, they will be zipped and
           uploaded *     int direct_html_link_index - Index in html_links to
           set the direct/default view in the *         report. Set either
           direct_html_link_index or direct_html, but not both *     string
           direct_html - Simple HTML text content that will be rendered
           within the report *         widget. Set either direct_html or
           direct_html_link_index, but not both *     list<File> file_links -
           A list of file paths or shock node IDs. Allows the user to *      
           specify files that the report widget should link for download. If
           you pass in paths *         to directories, they will be zipped * 
           string report_object_name - Name to use for the report object
           (will *         be auto-generated if unspecified) *    
           html_window_height - Fixed height in pixels of the HTML window for
           the report *     summary_window_height - Fixed height in pixels of
           the summary window for the report) -> structure: parameter
           "message" of String, parameter "objects_created" of list of type
           "WorkspaceObject" (* Represents a Workspace object with some brief
           description text * that can be associated with the object. *
           Required arguments: *     ws_id ref - workspace ID in the format
           'workspace_id/object_id/version' * Optional arguments: *    
           string description - A plaintext, human-readable description of
           the *         object created) -> structure: parameter "ref" of
           type "ws_id" (* Workspace ID reference in the format
           'workspace_id/object_id/version' * @id ws), parameter
           "description" of String, parameter "warnings" of list of String,
           parameter "html_links" of list of type "File" (* A file to be
           linked in the report. Pass in *either* a shock_id or a * path. If
           a path to a file is given, then the file will be uploaded. If a *
           path to a directory is given, then it will be zipped and uploaded.
           * Required arguments: *     string path - Can be a file or
           directory path. Required if shock_id is absent *     string
           shock_id - Shock node ID. Required if path is absent *     string
           name - Plain-text filename (eg. "results.zip") -- shown to the
           user * Optional arguments: *     string label - A short
           description for the file (eg. "Filter results") *     string
           description - A more detailed, human-readable description of the
           file) -> structure: parameter "path" of String, parameter
           "shock_id" of String, parameter "name" of String, parameter
           "label" of String, parameter "description" of String, parameter
           "direct_html" of String, parameter "direct_html_link_index" of
           Long, parameter "file_links" of list of type "File" (* A file to
           be linked in the report. Pass in *either* a shock_id or a * path.
           If a path to a file is given, then the file will be uploaded. If a
           * path to a directory is given, then it will be zipped and
           uploaded. * Required arguments: *     string path - Can be a file
           or directory path. Required if shock_id is absent *     string
           shock_id - Shock node ID. Required if path is absent *     string
           name - Plain-text filename (eg. "results.zip") -- shown to the
           user * Optional arguments: *     string label - A short
           description for the file (eg. "Filter results") *     string
           description - A more detailed, human-readable description of the
           file) -> structure: parameter "path" of String, parameter
           "shock_id" of String, parameter "name" of String, parameter
           "label" of String, parameter "description" of String, parameter
           "report_object_name" of String, parameter "html_window_height" of
           Double, parameter "summary_window_height" of Double, parameter
           "workspace_name" of String, parameter "workspace_id" of Long
        :returns: instance of type "ReportInfo" (* The reference to the saved
           KBaseReport. This is the return object for * both create() and
           create_extended() * Returned data: *    ws_id ref - reference to a
           workspace object in the form of *       
           'workspace_id/object_id/version'. This is a reference to a saved *
           Report object (see KBaseReportWorkspace.spec) *    string name -
           Plaintext unique name for the report. In *        create_extended,
           this can optionally be set in a parameter) -> structure: parameter
           "ref" of type "ws_id" (* Workspace ID reference in the format
           'workspace_id/object_id/version' * @id ws), parameter "name" of
           String
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
