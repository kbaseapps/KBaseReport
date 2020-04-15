# -*- coding: utf-8 -*-

import os.path
from template import Template
from uuid import uuid4
from .validation_utils import validate_template_params, validate_template_util_config, _format_errors

""" Class for rendering from a template """


class TemplateUtil:

    def __init__(self, config={}):
        """ initialise with the config from KBaseReport """

        # config should have keys 'template_toolkit' and 'scratch'
        validated_config = validate_template_util_config(config)
        self.config = validated_config
        self._template = None

    def template_engine(self):
        if not self._template:
            self._init_template_engine()

        return self._template

    def _init_template_engine(self, tt_config=None):

        if not tt_config:
            tt_config = self.config['template_toolkit']

        # TTP requires the config keys be uppercase
        uc_tt_config = {key.upper(): value for key, value in tt_config.items()}
        self._template = Template(uc_tt_config)

        return self._template

    def render_template_to_direct_html(self, params):
        """ Render a template and save the resulting content as the 'direct_html' key in 'params'

        :param params:  (dict)  dict with keys including

            template: {
                template_file:  # the template file to render
                template_data:  # data to be rendered in the template
            }

        :return:
        params with params['direct_html'] set to the rendered template content

        """

        # validate the params under `template`
        if 'template' not in params:
            raise KeyError(_format_errors({'template': ['required field']}, params))

        validated_params = validate_template_params(params['template'], self.config)
        template_string = self._render_template(validated_params['template_file'],
                                                validated_params['template_data'],)

        params['direct_html'] = template_string
        del params['template']
        return params

    def render_template_to_file(self, params):
        """ Render a template and save the resulting content to a file

        :param params:  (dict)  dict with keys

            template_file:      # the template file to render
            template_data:      # data to be rendered in the template
            output_file:        # path to a file where the output will be written

        :return:
        { 'path': '/path/to/output_file' }

        """

        validated_params = validate_template_params(params, self.config, with_output_file=True)
        template_string = self._render_template(validated_params['template_file'],
                                                validated_params['template_data'],)

        output_file = validated_params['output_file']
        # ensure any subdirs are created
        dir_path = os.path.dirname(output_file)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        with open(output_file, 'w') as f:
            f.write(template_string)

        return {'path': output_file}

    def render_template_to_scratch_file(self, params):
        """ Render a template and save the resulting content to a scratch file

        wrapper around render_template_to_file that generates an output_file parameter

        """
        params['output_file'] = os.path.join(self.config['scratch'], str(uuid4()) + '.txt')
        return self.render_template_to_file(params)

    def _render_template(self, template_file, template_data={}, template_config=None):
        """ Render template_name using template_data

        :param template_file:   (string)  the template file to render
        :param template_data:   (dict)    data to be rendered in the template
        :param template_config: (dict)    Template Toolkit configuration (optional)

        :return:
        template_string (string)   the rendered template

        """
        if template_config and template_config.items() > 0:
            self._init_template_engine(template_config)

        # raises a TemplateException if there is an issue anywhere
        template_string = self.template_engine().process(template_file, template_data)

        return template_string
