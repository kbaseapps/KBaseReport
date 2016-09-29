/*
    Module for a simple WS data object report type.
*/
module KBaseReport {
    /* @id ws */

    typedef string ws_id;

    /*
        Reference to a handle
        @id handle
    */

    typedef string handle_ref;

    /*
        Represents a Workspace object with some brief description text
        that can be associated with the object.
        @optional description
    */

    typedef structure {
        ws_id ref;
        string description;
    } WorkspaceObject;

    /*
        Represents a file or html archive that the report should like to
        @optional description
    */

    typedef structure {
        handle_ref handle;
        string description;
        string name;
        string URL;
    } LinkedFile;

    /*
        A simple Report of a method run in KBase.
        It only provides for now a way to display a fixed width text output summary message, a
        list of warnings, and a list of objects created (each with descriptions).
        @optional warnings file_links html_links direct_html direct_html_link_index
        @metadata ws length(warnings) as Warnings
        @metadata ws length(text_message) as Size(characters)
        @metadata ws length(objects_created) as Objects Created
    */

    typedef structure {
        string text_message;
        list <string> warnings;
        list <WorkspaceObject> objects_created;
        list<LinkedFile> file_links;
        list<LinkedFile> html_links;
        string direct_html;
        int direct_html_link_index;
    } Report;

    /*
        Provide the report information.  The structure is:
            params = {
                report: {
                    text_message: '',
                    warnings: ['w1'],
                    objects_created: [ {
                        ref: 'ws/objid',
                        description: ''
                    }]
                },
                workspace_name: 'ws'
            }
    */


    typedef structure {
        Report report;
        string workspace_name;
    } CreateParams;

    /*
        The reference to the saved KBaseReport.  The structure is:
            reportInfo = {
                ref: 'ws/objid/ver',
                name: 'myreport.2262323452'
            }
    */

    typedef structure {
        ws_id ref;
        string name;
    } ReportInfo;

    /*
            Create a KBaseReport with a brief summary of an App run.
    */

    funcdef create(CreateParams params) returns (ReportInfo info) authentication required;

    typedef structure {
        string path;
        string shock_id;
        string name;
        string description;
    } File;
    /*
        Parameters used to create a more complex report with file and html links
        The following arguments allow the user to specify the classical data fields in the report object:
        string message - simple text message to store in report object
        list <WorkspaceObject> objects_created;
        list <string> warnings - a list of warning messages in simple text
        The following argument allows the user to specify the location of html files/directories that the report widget will render <or> link to:
        list <fileRef> html_links - a list of paths or shock node IDs pointing to a single flat html file or to the top level directory of a website
        The report widget can render one html view directly. Set one of the following fields to decide which view to render:
        string direct_html - simple html text that will be rendered within the report widget
        int  direct_html_link_index - use this to specify the index of the page in html_links to view directly in the report widget (ignored if html_string is set)
        The following argument allows the user to specify the location of files that the report widget should link for download:
        list <fileRef> file_links - a list of paths or shock node IDs pointing to a single flat file
        The following parameters indicate where the report object should be saved in the workspace:
        string report_object_name - name to use for the report object (job ID is used if left unspecified)
        string workspace_name - name of workspace where object should be saved
    */
    typedef structure {
        string message;
        list <WorkspaceObject> objects_created;
        list <string> warnings;
        list <File> html_links;
        string direct_html;
        int  direct_html_link_index;
        list <File> file_links;
        string report_object_name;
        string workspace_name;
    } CreateExtendedReportParams;
    /*
        A more complex function to create a report that enables the user to specify files and html view that the report should link to
    */
    funcdef create_extended_report(CreateExtendedReportParams params) returns (ReportInfo info) authentication required;
};