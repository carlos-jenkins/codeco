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
from random import random
from hashlib import sha1

from pygments import lexers, highlight, formatters
from markdown import markdown
from docutils.core import publish_parts
from bs4 import BeautifulSoup, Tag


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
    }}
    #left-col {{
        float: left;
        width: 50%;
    }}
    #right-col {{
        float: left;
        width: 49%;
    }}
    .no-float {{
        clear: both;
    }}
    .annotations {{
        padding: 5px 20px 10px 20px;
        font-family: DejaVu Sans, Verdana, sans-serif;
    }}
    table.highlighttable {{
        width: 100%;
        padding: 0px 10px;
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
            <div class="annotations">
                {annotations}
            </div>
        </div>
        <div id="right-col">
            {code}
        </div>
    </div>
    <div class="no-float"></div>
</div>
</body>
</html>
"""


annotation_tpl = """\
<div class="annotation">
    <span style="display: none;" class="data">{json}</span>
    {body}
</div>
"""


interact_script = """\
$(window).load(function () {

    // Hide annotations non title elements
    $('div.annotation_body').children(':not(.annotation_title)').hide();

    var speed = 150;

    function show_annotation() {
        $(this).toggleClass('hover');
        $(this).children('*:not(.annotation_title)').slideToggle(speed);

        var meta = jQuery.parseJSON($(this).siblings('.data').text());
        if (meta.args != null) {
            for (var i = 0; i < meta.args.length; i++) {
                $('#' + meta.prefix + 'line-' + meta.args[i]).toggleClass(
                    'hll hll-line'
                );
            }
        }
    }

    $('div.annotation_body').hover(show_annotation, show_annotation);
});
"""


class Processor(object):

    ann_regex = r'^<\[annotation\]> *?(?P<args>[0-9\[\] ]+)? *?$'
    ann_re = re.compile(ann_regex)

    def _render_markdown(self, body, **kwargs):
        # Same as Pygments
        kwargs['output_format'] = 'html4'
        return markdown(body, **kwargs)

    def _render_rest(self, body, **kwargs):
        overrides = {
            'doctitle_xform': False,
            'initial_header_level': 1
        }
        overrides.update(kwargs)
        parts = publish_parts(
            source=body,
            writer_name='html',
            settings_overrides=overrides
        )
        return parts['body']

    def _render(self, parsed_anns, ann_format, renderer_opts):
        # Get renderer
        renderers = {
            'markdown' : self._render_markdown,
            'rest'     : self._render_rest,
        }
        renderer = renderers[ann_format]

        def add_class(elem, html_class):
            """
            Helper to safely add a class to a Tag object.
            """
            if not isinstance(elem, Tag):
                return False
            if 'class' in elem:
                elem.attrs['class'] += [html_class]
            else:
                elem.attrs['class'] = html_class
            return True

        # Render annotations
        rendered_anns = []
        for meta, ann_body in parsed_anns:

            html = renderer(ann_body, **renderer_opts).strip()

            # Wrap rendered annotation
            bs = BeautifulSoup(html)
            elements = bs.body.contents
            if len(elements) == 1 and elements[0].name == 'div':
                # Already wrapped
                wrapper = elements[0]
            else:
                # Wrap into a div
                wrapper = bs.new_tag('div')
                for elem in elements:
                    wrapper.append(elem)
            add_class(wrapper, 'annotation_body')

            for child in wrapper.children:
                if add_class(child, 'annotation_title'):
                    break
            html = str(wrapper)

            rendered_anns.append(
                annotation_tpl.format(json=dumps(meta), body=html)
            )

        return rendered_anns

    def _parse_annotations(self, annotations, prefix):
        current = None
        buff = []
        parsed_anns = []

        for line in annotations.splitlines():
            m = Processor.ann_re.match(line)
            if not m:
                buff.append(line)
                continue

            if current is not None:
                parsed_anns.append(
                    (current, '\n'.join(buff))
                )
            current = {
                'args' : None,
                'prefix' : prefix
            }
            args = m.groupdict()['args']
            if args is not None:
                current['args'] = args.strip().split(' ')
            buff = []

        if buff:
            parsed_anns.append(
                (current, '\n'.join(buff))
            )

        return parsed_anns

    def _generate_prefix(self, lenght=10):
        """
        Generates a random hash to be used as prefix.
        """
        the_hash = sha1()
        the_hash.update(str(random()))
        return the_hash.hexdigest()[:lenght]

    def process(
            self, code, annotations,
            codefn=None, ann_format='rest',
            prefix=None, codestyle='monokai',
            renderer_opts=None):

        if renderer_opts is None:
            renderer_opts = {}
        if prefix is None:
            prefix = self._generate_prefix()

        # Guess programming language
        # Warning: might raise pygments.util.ClassNotFound
        if codefn is None:
            lexer = lexers.guess_lexer(code)
        else:
            lexer = lexers.guess_lexer_for_filename(codefn, code)

        # Parse annotations
        parsed_anns = self._parse_annotations(
            annotations, prefix
        )

        # Render annotations
        rendered_anns = self._render(
            parsed_anns, ann_format, renderer_opts
        )

        # Highlight code
        options = {
            'style'    : codestyle,
            'linenos'  : 'table',
            'linespans': prefix + 'line',
        }
        formatter = formatters.HtmlFormatter(**options)
        highlighted = highlight(code, lexer, formatter)
        style = formatter.get_style_defs('table.highlighttable') + \
            '\ntable.highlighttable .hll-line { display: block; }'

        return {
            'style'       : style,
            'script'      : interact_script,
            'annotations' : rendered_anns,
            'code'        : highlighted,
        }

    def process_files(self, codefn, annfn, **kwargs):
        # Warning: might raise IO exceptions
        with open(codefn, 'r') as cf:
            code = cf.read()
        with open(annfn, 'r') as af:
            annotations = af.read()
        return self.process(code, annotations, codefn=codefn, **kwargs)

    def create_document(
            self, codefn, annfn,
            title='', tpl=None, out_file=None, **kwargs):

        processed = self.process_files(codefn, annfn, **kwargs)

        # Add title and join annotations
        processed['title'] = title
        processed['annotations'] = \
            '\n'.join(processed['annotations'])

        if tpl is None:
            tpl = default_tpl
        document = tpl.format(**processed)

        # Warning: might raise IO exceptions
        if out_file is not None:
            with open(out_file, 'w') as of:
                of.write(document)

        return document
