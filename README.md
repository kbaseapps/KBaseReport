[![Build Status](https://travis-ci.org/chenry/KBaseReport.svg?branch=master)](https://travis-ci.org/chenry/KBaseReport)

# KBaseReport
---

The KBaseReports module is the preferred way to communicate results to users. The example module contains a minimal use
case where a string is displayed to the user (supplied in the 'text_message' field) along with links to new objects 
created by the app (supplied in the 'objects_created' field). However this module also contains functionality to create 
and display HTML webpages and serve files directly for user download. A more typical and feature rich example can be
found in KBase's implementation of [Ballgown](https://github.com/kbaseapps/kb_ballgown/blob/1b77c87/lib/kb_ballgown/core/ballgown_util.py#L66-L167)

An annotated copy of the master function is copied below:
```python
def _generate_report(self, params, result_directory, diff_expression_matrix_set_ref):
        """
        _generate_report: generate summary report
        """
        print('creating report')
        # Files to be presented directly to the user are copied to a output directory, zipped and returned as a list of paths
        output_files = self._generate_output_file_list(result_directory)
        
        # A folder for the display web page is created(L74 in ballgown repo linked above), reference data (could also be 
        # embedded images) for the page are copied in(L78), custom html is generated(L81-95), template is updated with 
        # custom html(L98-104), the complete web page is saved to SHOCK which will serve the data(L106) and an object with 
        # that reference is returned(L109)
        output_html_files = self._generate_html_report(result_directory, params, diff_expression_matrix_set_ref)

        report_params = {
              'message': '',
              'workspace_name': params.get('workspace_name'),
              'file_links': output_files,
              'html_links': output_html_files,
              'direct_html_link_index': 0,
              'html_window_height': 333,
              'report_object_name': 'kb_ballgown_report_' + str(uuid.uuid4())}
        
        # Make the client, generate the report
        kbase_report_client = KBaseReport(self.callback_url)
        output = kbase_report_client.create_extended_report(report_params)
        # Return references which will allow inline display of the report in the Narrative
        report_output = {'report_name': output['name'], 'report_ref': output['ref']}

        return report_output
```