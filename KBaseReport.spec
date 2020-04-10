/*
 *  Module for workspace data object reports, which show the results of running a job in an SDK app.
 */
module KBaseReport {
    /*
     * Workspace ID reference in the format 'workspace_id/object_id/version'
     * @id ws
     */
    typedef string ws_id;

    /*
     * Represents a Workspace object with some brief description text
     * that can be associated with the object.
     * Required arguments:
     *     ws_id ref - workspace ID in the format 'workspace_id/object_id/version'
     * Optional arguments:
     *     string description - A plaintext, human-readable description of the
     *         object created
     */
    typedef structure {
        ws_id ref;
        string description;
    } WorkspaceObject;

    /*
     * A simple report for use in create()
     * Optional arguments:
     *     string text_message - Readable plain-text report message
     *     string direct_html - Simple HTML text that will be rendered within the report widget
     *     list<string> warnings - A list of plain-text warning messages
     *     list<WorkspaceObject> objects_created - List of result workspace objects that this app
     *         has created. They will get linked in the report view
     */
    typedef structure {
        string text_message;
        string direct_html;
        list<string> warnings;
        list<WorkspaceObject> objects_created;
    } SimpleReport;

    /*
     * Parameters for the create() method
     *
     * Pass in *either* workspace_name or workspace_id -- only one is needed.
     * Note that workspace_id is preferred over workspace_name because workspace_id immutable. If
     * both are provided, the workspace_id will be used.
     *
     * Required arguments:
     *     SimpleReport report - See the structure above
     *     string workspace_name - Workspace name of the running app. Required
     *         if workspace_id is absent
     *     int workspace_id - Workspace ID of the running app. Required if
     *         workspace_name is absent
     */
    typedef structure {
        SimpleReport report;
        string workspace_name;
        int workspace_id;
    } CreateParams;

    /*
     * The reference to the saved KBaseReport. This is the return object for
     * both create() and create_extended()
     * Returned data:
     *    ws_id ref - reference to a workspace object in the form of
     *        'workspace_id/object_id/version'. This is a reference to a saved
     *        Report object (see KBaseReportWorkspace.spec)
     *    string name - Plaintext unique name for the report. In
     *        create_extended, this can optionally be set in a parameter
     */
    typedef structure {
        ws_id ref;
        string name;
    } ReportInfo;

    /*
     * Function signature for the create() method -- generate a simple,
     * text-based report for an app run.
     * @deprecated KBaseReport.create_extended_report
     */
    funcdef create(CreateParams params)
        returns (ReportInfo info) authentication required;

    /*
     * A file to be linked in the report. Pass in *either* a shock_id or a
     * path. If a path to a file is given, then the file will be uploaded. If a
     * path to a directory is given, then it will be zipped and uploaded.
     * Required arguments:
     *     string path - Can be a file or directory path. Required if shock_id is absent
     *     string shock_id - Shock node ID. Required if path is absent
     *     string name - Plain-text filename (eg. "results.zip") -- shown to the user
     * Optional arguments:
     *     string label - A short description for the file (eg. "Filter results")
     *     string description - A more detailed, human-readable description of the file
     */
    typedef structure {
        string path;
        string shock_id;
        string name;
        string label;
        string description;
    } File;

    typedef structure {
        string template_file;
        string template_data_json;
    } TemplateParams;

    /*
     * Parameters used to create a more complex report with file and HTML links
     *
     * Pass in *either* workspace_name or workspace_id -- only one is needed.
     * Note that workspace_id is preferred over workspace_name because workspace_id immutable.
     *
     * Note that it is possible to pass both 'html_links'/'direct_html_link_index' and 'direct_html'
     * as parameters for an extended report; in such cases, the file specified by the
     * 'direct_html_link_links' parameter is used for the report and the 'direct_html' is ignored.
     *
     * Required arguments:
     *     string workspace_name - Name of the workspace where the report
     *         should be saved. Required if workspace_id is absent
     *     int workspace_id - ID of workspace where the report should be saved.
     *         Required if workspace_name is absent
     * Optional arguments:
     *     string message - Simple text message to store in the report object
     *     list<WorkspaceObject> objects_created - List of result workspace objects that this app
     *         has created. They will be linked in the report view
     *     list<string> warnings - A list of plain-text warning messages
     *     list<File> html_links - A list of paths or shock IDs pointing to HTML files or directories.
     *         If you pass in paths to directories, they will be zipped and uploaded
     *     int direct_html_link_index - Index in html_links to set the direct/default view in the report.
     *         Set only one of 'direct_html', 'template', and 'html_links'/'direct_html_link_index'.
     *         Setting both 'template' and 'html_links'/'direct_html_link_index' will generate an error.
     *     string direct_html - Simple HTML text content to be rendered within the report widget.
     *         Set only one of 'direct_html', 'template', and 'html_links'/'direct_html_link_index'.
     *         Setting both 'template' and 'direct_html' will generate an error.
     *     TemplateParams template - render a template to produce HTML text content that will be
     *         rendered within the report widget. Setting 'template' and 'direct_html' or
     *         'html_links'/'direct_html_link_index' will generate an error.
     *     list<File> file_links - A list of file paths or shock node IDs. Allows the user to
     *         specify files that the report widget should link for download. If you pass in paths
     *         to directories, they will be zipped
     *     string report_object_name - Name to use for the report object (will
     *         be auto-generated if unspecified)
     *     html_window_height - Fixed height in pixels of the HTML window for the report
     *     summary_window_height - Fixed height in pixels of the summary window for the report
     */
    typedef structure {
        string message;
        list<WorkspaceObject> objects_created;
        list<string> warnings;
        list<File> html_links;
        TemplateParams template;
        string direct_html;
        int direct_html_link_index;
        list<File> file_links;
        string report_object_name;
        float html_window_height;
        float summary_window_height;
        string workspace_name;
        int workspace_id;
    } CreateExtendedReportParams;

    /*
     * Create a report for the results of an app run. This method handles file
     * and HTML zipping, uploading, and linking as well as HTML rendering.
     */
    funcdef create_extended_report(CreateExtendedReportParams params)
        returns (ReportInfo info) authentication required;


    /*
     * Render a template using the supplied data, saving the results to an output
     * file in the scratch directory.
     *
     * Required arguments:
     *     string template_file  -  Path to the template file to be rendered.
     *     string output_file    -  Path to the file where the rendered template
     *                              should be saved. Must be in the scratch directory.
     * Optional:
     *     string template_data_json -  Data for rendering in the template.
     */

    typedef structure {
        string template_file;
        string output_file;
        string template_data_json;
    } RenderTemplateParams;

    /*
     * Render a file from a template. This method takes a template file and
     * a data structure, renders the template, and saves the results to a file.
     * It returns the output file path in the form
     * { 'output_file': { 'path': '/path/to/file' } }
     *
     * To ensure that the template and the output file are accessible to both
     * the KBaseReport service and the app requesting the template rendering, the
     * template file should be copied into the shared `scratch` directory and the
     * output_file location should also be in `scratch`.
     *
     * See https://github.com/kbaseIncubator/kbase_report_templates for sample
     * page templates, standard includes, and instructions on creating your own
     * templates.
     */
    funcdef render_template(RenderTemplateParams params)
        returns (File output_file_path) authentication required;

};
