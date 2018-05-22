#include <KBaseReportWorkspace.spec>
/*
 *  Module for workspace data object reports, which show the results of running a job in an SDK app.
 */
module KBaseReport {
    /*
     * A simple report for use in create()
     * Required arguments:
     *     string text_message - Readable plain-text report message
     * Optional arguments:
     *     list<WorkspaceObject> objects_created - List of result workspace objects that this app
     *         has created. They will get linked in the report view.
     *     list<string> warnings - A list of plain-text warning messages
     *     string direct_html - simple html text that will be rendered within the report widget
     * @optional text_message warnings objects_created
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Message Length
     * @metadata ws length(objects_created) as Objects Created
     */
    typedef structure {
        string text_message;
        list<string> warnings;
        list<KBaseReportWorkspace.WorkspaceObject> objects_created;
    } SimpleReport;

    /*
     * Parameters for the create() method
     * Pass in *either* workspace_name or workspace_id -- only one is needed
     * Required arguments:
     *     SimpleReport report
     *     string workspace_name - needed if workspace_id is blank. Note that this may change.
     *     int workspace_id - needed if workspace_name is blank. Preferred as it is immutable.
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
     *        workspace_id/object_id/version. This is a reference to the saved data
     *        from creating the report.
     *    string name - Plaintext unique name for the report. In
     *        create_extended, this can optionally be set in a parameter.
     */
    typedef structure {
        KBaseReportWorkspace.ws_id ref;
        string name;
    } ReportInfo;

    /*
     * Function signature for the create() method -- generate a report for an app run.
     * create_extended() is the preferred method if you have html_links and
     * file_links, but this is still provided for backwards compatibility.
     * @deprecated KBaseReport.create_extended_report
     */
    funcdef create(CreateParams params)
        returns (ReportInfo info) authentication required;

    /*
     * A file to be linked in the report. Pass in *either* a shock_id or a
     * path. If a path to a file is given, then the file will be uploaded. If a
     * path to a directory is given, then it will be zipped and uploaded.
     * Required arguments:
     *     string path - Can be a file or directory path. Required if shock_id is absent.
     *     string shock_id - Shock node ID. Required if path is absent.
     *     string name - Plain-text file name -- shown to the user.
     * Optional arguments:
     *     string description - A plaintext, human-readable description of the file.
     * @optional description
     */
    typedef structure {
        string path;
        string shock_id;
        string name;
        string description;
    } File;

    /*
     * Parameters used to create a more complex report with file and html links
     *
     * All parameters are optional.
     *
     * string message - Simple text message to store in report object
     * list<WorkspaceObject> objects_created - List of result workspace objects that this app
     *     has created. They will get linked in the report view.
     * list<string> warnings - A list of plain-text warning messages
     * list<File> html_links - A list of paths or shock IDs pointing to html files or directories.
     *     if you pass in paths, they will be zipped and uploaded
     * int direct_html_link_index - Index in html_links to set the direct/default view in the
     *     report (ignored if direct_html is present).
     * string direct_html - simple html text that will be rendered within the report widget
     *     If you pass in both direct_html and html_links, then direct_html will be ignored.
     * list<File> file_links - a list of file paths or shock node IDs. Allows the user to
     *     specify files that the report widget should link for download.
     * string report_object_name - name to use for the report object
     *     (will be auto-generated if unspecified)
     * html_window_height - fixed height in pixels of the html window for the report
     * summary_window_height - fixed height in pixels of the summary window for the report
     * string workspace_name - name of workspace where object should be saved.
     *     Required if workspace_id is not present.
     * int workspace_id - id of workspace where object should be saved.
     *     Required if workspace_name is not present.
     *
     * @optional message objects_created warnings html_links direct_html direct_html_link_index file_links report_object_name html_window_height summary_window_height
     */
    typedef structure {
        string message;
        list<KBaseReportWorkspace.WorkspaceObject> objects_created;
        list<string> warnings;
        list<File> html_links;
        string direct_html;
        int  direct_html_link_index;
        list<File> file_links;
        string report_object_name;
        float html_window_height;
        float summary_window_height;
        string workspace_name;
        int workspace_id;
    } CreateExtendedReportParams;

    /*
     * Create a report for the results of an app run -- handles file and html zipping/uploading
     * If you are using html_links or file_links, this will be more user-friendly than create()
     */
    funcdef create_extended_report(CreateExtendedReportParams params)
        returns (ReportInfo info) authentication required;
};
