# -*- coding: utf-8 -*-
# Copyright (C) 2014 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Directive for Sphinx document system.
"""

import re
from os.path import join

from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.util.osutil import ensuredir

from codeco.processor import Processor


class codeco_node(nodes.General, nodes.Element):

    def __init__(self, codeco_dict=None, **kwargs):
        self.codeco_dict = codeco_dict
        super(codeco_node, self).__init__(**kwargs)


class CodecoDirective(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 0

    # Regex required to split content
    div_regex = \
        r'^<\[===========*\]> *?$'
    div_re = re.compile(div_regex)

    def run(self):

        code = []
        annotations = []

        not_found = True
        bucket = code

        for line in self.content:
            if not_found and CodecoDirective.div_re.match(line):
                not_found = False
                bucket = annotations
                continue
            bucket.append(line)

        proc = Processor()
        codeco_dict = proc.process(
            '\n'.join(code),
            '\n'.join(annotations)
        )

        return [codeco_node(codeco_dict=codeco_dict)]


directive_tpl = """\
<table class="two-columns">
    <tr>
        <td class="left">{annotations}</td>
        <td class="right">{code}</td>
    </tr>
</table>
"""


def visit_codeco_node(self, node):
    # Get variables
    d = node.codeco_dict
    codestyle = getattr(
        self.settings.env.config, 'pygments_style', None
    )

    # Add segment to body
    document = directive_tpl.format(
        annotations='\n'.join(d['annotations']),
        code=d['code'],
        codestyle=codestyle,
    )
    self.body.append(document)

    # Create style and script files
    # XXX This will recreate the file again and again. I accept better ideas :S
    html_static_path = getattr(
        self.settings.env.config, 'html_static_path', ['_static']
    )
    build_dir = join(
        self.builder.outdir, html_static_path[0]  # First index, are you sure?
    )
    ensuredir(build_dir)

    with open(join(build_dir, 'codeco.css'), 'w') as css:
        css.write(d['styles'][-1])  # Only extras, are you sure?
    with open(join(build_dir, 'codeco.js'), 'w') as js:
        js.write(d['script'])

    raise nodes.SkipNode


def depart_codeco_node(self, node):
    pass


def builder_inited(app):
    app.add_stylesheet('codeco.css')
    app.add_javascript('codeco.js')


def setup(app):
    app.add_node(
        codeco_node,
        html=(visit_codeco_node, depart_codeco_node),
        #latex=(visit_codeco_node, depart_codeco_node),
        #text=(visit_codeco_node, depart_codeco_node),
        #man=(visit_codeco_node, depart_codeco_node),
        #texinfo=(visit_codeco_node, depart_codeco_node)
    )

    app.add_directive('annotated-code', CodecoDirective)

    app.connect('builder-inited', builder_inited)
