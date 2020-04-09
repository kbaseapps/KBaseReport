# -*- coding: utf-8 -*-

from template import Template
from .validation_utils import validate_template_params, _format_errors
import os.path

""" Utility for rendering a report from a template """


def render_template_to_direct_html(params, config):
    """ Render a template and save the resulting content as the 'direct_html' key in 'params'

    :param params:  (dict)  dict with keys including

        template: {
            template_file:  # the template file to render
            template_data:  # data to be rendered in the template
        }

    :param config:  (dict)  application config, which may include keys

        scratch:            # location of the scratch directory
        template_toolkit:   # configuration options for Template Toolkit

    :return:
    params with params['direct_html'] set to the rendered template content

    """

    # validate the params under `template`
    if 'template' not in params:
        raise KeyError(_format_errors({'template': ['required field']}, params))

    validated_params = validate_template_params(params['template'], config)

    template_string = _render_template(validated_params['template_file'],
                                       validated_params['template_data'],
                                       validated_params['template_config'])

    params['direct_html'] = template_string
    del params['template']
    return params


def render_template_to_file(params, config):
    """ Render a template and save the resulting content to a file

    :param params:  (dict)  dict with keys

        template_file:      # the template file to render
        template_data:      # data to be rendered in the template
        output_file:        # path to a file where the output will be written

    :param config:  (dict)  application config, which may include keys

        scratch:            # location of the scratch directory
        template_toolkit:   # configuration options for Template Toolkit

    :return:
    { 'path': '/path/to/output_file' }

    """

    validated_params = validate_template_params(params, config, with_output_file=True)
    template_string = _render_template(validated_params['template_file'],
                                       validated_params['template_data'],
                                       validated_params['template_config'])

    # ensure any subdirs are created
    output_file = params['output_file']
    dir_path = os.path.dirname(output_file)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    with open(output_file, 'w') as f:
        f.write(template_string)

    return {'path': output_file}


def _render_template(template_file, template_data={}, template_config={}):
    """ Render template_name using template_data

    :param template_file:   (string)  the template file to render
    :param template_data:   (dict)    data to be rendered in the template
    :param template_config: (dict)    Template Toolkit configuration

    :return:
    template_string (string)   the rendered template

    """
    # make sure that the config is uppercased, per TTP requirements
    uc_template_config = {key.upper(): value for key, value in template_config.items()}

    template = Template(uc_template_config)

    # raises a TemplateException if there is an issue anywhere
    template_string = template.process(template_file, template_data)

    return template_string
