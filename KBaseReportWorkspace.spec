/*
 * Behind-the-scenes types for report data that gets uses on the workspace. 
 * These objects are generated in this module from the API types found in KBaseReport
 */
module KBaseReportWorkspace {
    /*
     * Workspace ID reference - eg. 'ws/id/ver'
     * @id ws
     */
    typedef string ws_id;

    /*
     * Reference to a handle ID
     * @id handle
     */
    typedef string handle_ref;

    /*
     * Represents a Workspace object with some brief description text
     * that can be associated with the object.
     * Required arguments:
     *     ws_id ref - workspace ID
     * Optional arguments:
     *     string description - A plaintext, human-readable description of the
     *         object created.
     * @optional description
     */
    typedef structure {
        ws_id ref;
        string description;
    } WorkspaceObject;

    /*
     * Represents a file or html archive that the report links to. Used
     * behind-the-scenes in the workspace.
     * Required arguments:
     *     handle_ref handle - Handle ID
     *     string name - Plain-text name of the file (shown to the user)
     *     string URL - URL of shock node: <shock-url>/node/<shock-handle-id>
     * @optional description label
     */
    typedef structure {
        handle_ref handle;
        string description;
        string name;
        string label;
        string URL;
    } LinkedFile;

    /*
     * A Report of a method run in KBase. This is used behind-the-scenes in the
     * workspace for the simple create() method
     * Required arguments:
     *     string text_message - Readable plain-text report message
     * @optional warnings file_links html_links direct_html direct_html_link_index
     * @metadata ws length(warnings) as Warnings
     * @metadata ws length(text_message) as Message Length
     * @metadata ws length(objects_created) as Objects Created
     */
    typedef structure {
        string text_message;
        list<string> warnings;
        list<WorkspaceObject> objects_created;
        list<LinkedFile> file_links;
        list<LinkedFile> html_links;
        string direct_html;
        int direct_html_link_index;
    } Report;
};
