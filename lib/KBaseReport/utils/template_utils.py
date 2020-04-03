# -*- coding: utf-8 -*-

from template import Template

""" Utility for rendering a report from a template """

def render_template_to_file(params):
    """ Render a template and save the resulting content to a file

    :param params:  (dict)  dict with keys

        template_file:  # the template file to render
        template_data:  # data to be rendered in the template
        output_file:    # path to a file where the output will be written

    :return:
    { 'path': '/path/to/output_file' }

    """
    if ('template_file' not in params or 'output_file' not in params or 'template_data' not in params):
        raise TypeError('Missing required parameters: please supply '
            + 'template_data, template_file, and output_file')

    template_string = _render_template(params['template_file'], params['template_data'])

    with open(params['output_file'], 'w') as f:
        f.write(template_string)
        f.close()

    return { 'path': params['output_file'] }


def _render_template(template_file, template_data={}):
    """ Render template_name using template_data

    :param template_file: (string)  the template file to render
    :param template_data: (dict)    data to be rendered in the template

    :return:
    template_string (string)   the rendered template

    Template Toolkit will search for included templates in the directories
    `/kb/module/kbase_report_templates/` and
    `/kb/module/kbase_report_templates/views/`.



    """

    template = Template({
        'TRIM': 1,
        'INCLUDE_PATH': '/kb/module/kbase_report_templates/views/:/kb/module/kbase_report_templates/',
        'ABSOLUTE': 1,
    })

    # raises a TemplateException if there is an issue anywhere
    template_string = template.process(template_file, template_data)

    return template_string
