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
Main processing module.
"""

import re
from json import dumps

from pygments import lexers, highlight, formatters
from markdown import markdown
from docutils.core import publish_parts


default_tpl = """\
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{title}</title>

    <style type="text/css">
    body {{
        margin: 0;
        padding: 10px;
        background-color: lightsteelblue;
    }}
    #wrapper {{
        border: 1px solid lightgray;
        width: 80%;
        margin: auto;
        padding: 10px 20px;
        background-color: white;
    }}
    #two-columns {{
        width: 80%;
        margin: 0 auto;
    }}
    #left-col {{
        float: left;
    }}
    #right-col {{
        float: left;
    }}
    .no-float {{
        clear: both;
    }}
    </style>

    <style type="text/css">
    {style}
    </style>

    <script src="http://code.jquery.com/jquery-2.1.0.min.js"></script>
    <script type="text/javascript">
    {script}
    </script>
</head>
<body>
<div id="wrapper">
    <div id="two-columns">
        <div id="left-col">
            {code}
        </div>
        <div id="right-col">
            {annotations}
        </div>
    </div>
    <div class="no-float"></div>
</div>
</body>
</html>
"""

interact_script = """\
$(window).load(function () {

    // Hide annotations non title elements
    $('.annotation_body > *:lt(2)').addClass('ann_title');
    $('.annotation_body > *:gt(1)').hide();

    var speed = 150;

    function show_annotation() {
        $(this).toggleClass('hover');
        $(this).children('*:not(.ann_title)').slideToggle(speed);

        var meta = jQuery.parseJSON($(this).siblings('.data').text());
        if (meta.args != null) {
            $('#' + meta.prefix + 'line-' + meta.args).toggleClass('hll');
        }

    }

    $('div.annotation_body').hover(show_annotation, show_annotation);
});
"""


class Processor(object):

    ann_regex = \
        r'^<\[annotation\]> *?' \
        r'((?P<option>(line|chars))? *?(?P<args>[0-9,]+)?)? *?$'
    ann_re = re.compile(ann_regex)

    def render_markdown(self, body):
        return markdown(body, output_format='html4')  # Same as Pygments

    def render_rest(self, body):
        overrides = {
            'doctitle_xform': False,
            'initial_header_level': 1
        }
        parts = publish_parts(
            source=body,
            writer_name='html',
            settings_overrides=overrides
        )
        return parts['body']

    def create_document(
            self, codefn, annfn,
            title='', tpl=None, out_file=None, **kwargs):

        processed = self.process_files(codefn, annfn, **kwargs)
        processed['title'] = title

        if tpl is None:
            tpl = default_tpl
        document = tpl.format(**processed)

        # Warning: might raise IO exceptions
        if out_file is not None:
            with open(out_file, 'w') as of:
                of.write(document)

        return document

    def process_files(self, codefn, annfn, **kwargs):
        # Warning: might raise IO exceptions
        with open(codefn, 'r') as cf:
            code = cf.read()
        with open(annfn, 'r') as af:
            annotations = af.read()
        return self.process(code, annotations, codefn=codefn, **kwargs)

    def process(
            self, code, annotations,
            codefn=None, ann_format='rest', prefix=''):

        # Guess programming language
        # Warning: might raise pygments.util.ClassNotFound
        if codefn is None:
            lexer = lexers.guess_lexer(code)
        else:
            lexer = lexers.guess_lexer_for_filename(codefn, code)

        # Parse annotations
        current = None
        buff = []
        parsed_anns = []

        for line in annotations.splitlines():
            m = Processor.ann_re.match(line)
            if not m:
                buff.append(line)
                continue

            if current is not None:
                parsed_anns.append((current, buff))
            current = m.groupdict()
            buff = []

        if buff:
            parsed_anns.append((current, buff))

        # Render annotations
        renderers = {
            'markdown' : self.render_markdown,
            'rest'     : self.render_rest,
        }
        renderer = renderers[ann_format]

        rendered_anns = ['<div class="annotations">']
        for meta, lines in parsed_anns:
            meta['prefix'] = prefix
            body = '\n'.join(lines)
            render = '\n'.join([
                '<div class="annotation">',
                '<span style="display: none;" class="data">{}</span>'.format(
                    dumps(meta)
                ),
                '<div class="annotation_body">',
                renderer(body),
                '</div>',
                '</div>',
            ])
            rendered_anns.append(render)
        rendered_anns.append('</div>')

        # Highlight code
        options = {
            'linenos'  : 'table',
            'linespans': prefix + 'line',
        }
        formatter = formatters.HtmlFormatter(**options)
        highlighted = highlight(code, lexer, formatter)

        return {
            'style'       : formatter.get_style_defs('table.highlighttable'),
            'script'      : interact_script,
            'annotations' : '\n'.join(rendered_anns),
            'code'        : highlighted,
        }
