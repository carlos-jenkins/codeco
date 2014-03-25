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

from docutils import nodes
from sphinx.util.compat import Directive

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
    p = node.codeco_dict
    document = directive_tpl.format(
        annotations='\n'.join(p['annotations']),
        code=p['code']
    )
    self.body.append(document)
    raise nodes.SkipNode


def depart_codeco_node(self, node):
    pass


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
