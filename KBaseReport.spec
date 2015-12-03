

/*
    Module for a simple WS data object report type.
*/
module KBaseReport {
    
    /* @id ws */
    typedef string ws_id;


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
        A simple Report of a method run in KBase.

        It only provides for now a way to display a fixed width text output summary message, a 
        list of warnings, and a list of objects created (each with descriptions).

        @optional warnings
    */
    typedef structure {

        string text_message;

        list <string> warnings;

        list <WorkspaceObject> objects_created;

    } Report;


};