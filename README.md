
# KBaseReport

This is a [KBase SDK](https://github.com/kbase/kb_sdk) app that can be used within other apps to generate output reports that describe the results of running an app.

[How to create a KBaseReport](https://kbase.github.io/kb_sdk_docs/howtos/create_a_report.html)

# API

Install in your own KBase SDK app with:

```sh
$ kb-sdk install KBaseReport
```

## Initialization

Initialize the client using the `callback_url` from your `MyModuleImpl.py` class:

```py
from KBaseReport.KBaseReportClient import KBaseReport
...
report_client = KBaseReport(self.callback_url)
```

## Creating a report

Use the method **`report_client.create_extended_report(params)`** to create a report object along with the following parameters, passed as a dictionary:

* `message`: (optional string) basic result message to show in the report
* `report_object_name`: (optional string) a name to give the workspace object that stores the report.
* `workspace_id`: (optional integer) id of your workspace. Preferred over `workspace_name` as it's immutable. Required if `workspace_name` is absent.
* `workspace_name`: (optional string) string name of your workspace. Requried if `workspace_id` is absent.
* `direct_html`: (optional string) raw HTML to show in the report
* `template`: (optional dictionary) a dictionary in the form `{'template_file': '/path/to/tmpl', 'template_data_json': "json_data_structure"}` specifying the location of a template file and the data to be rendered in the template. For more information, please see the [KBase Templates Repo](https://github.com/kbaseIncubator/kbase_report_templates).
* `objects_created`: (optional list of WorkspaceObject) data objects that were created as a result of running your app, such as assemblies or genomes
* `warnings`: (optional list of strings) any warnings messages generated from running the app
* `file_links`: (optional list of dicts) files to attach to the report (see the valid key/vals below)
* `html_links`: (optional list of dicts) HTML files to attach and display in the report (see the additional information below)
* `direct_html_link_index`: (optional integer) index in `html_links` that you want to use as the main/default report view
* `html_window_height`: (optional float) fixed pixel height of your report view
* `summary_window_height`: (optional float) fixed pixel height of the summary within your report

_Example usage:_

```py
report = report_client.create_extended_report({
    'direct_html_link_index': 0,
    'html_links': [html_file],
    'report_object_name': report_name,
    'workspace_name': workspace_name
})
```

### File links and HTML links

The `file_links` and `html_links` params can have the following keys:

* `shock_id`: (required string) Shock ID for a file. Not required if `path` is present.
* `path`: (required string) Full file path for a file (in scratch). Not required if `shock_id` is present.
* `name`: (required string) name of the file
* `description`: (optional string) Readable description of the file
* `template`: (optional dictionary) A dictionary with keys `template_file` (required) and `template_data_json` (optional), specifying a template and accompanying data to be rendered to generate an output file.

For the `path` parameter, this can either point to a single file or a directory. If it points to a directory, then it will be zipped and uploaded for you.

If you pass in a directory as your `path` for HTML reports, you can include additional files in that directory, such as images or PDFs. You can link to those files from your main HTML page by using relative links.

For more information on using templates, please see the [KBase Templates Repo](https://github.com/kbaseIncubator/kbase_report_templates).

> Important: Be sure to set the name of your main HTML file (eg. `index.html`) to the `'name'` key in your `html_links` dictionary.

For example, to generate an HTML report:

```
html_dir = {
    'path': html_dir_path,
    'name': 'index.html',  # MUST match the filename of your main html page
    'description': 'My HTML report'
}
report = report_client.create_extended_report({
    'html_links': [html_dir],
    'direct_html_link_index': 0,
    'report_object_name': report_name,
    'workspace_name': workspace_name
})
```
