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
    }}
    div#wrapper {{
        width: 80%;
        margin: auto;
        padding: 10px 20px;
        background-color: white;
    }}
    div.annotations {{
        padding: 5px 20px 10px 20px;
        font-family: DejaVu Sans, Verdana, sans-serif;
    }}
    table.two-columns {{
        width: 100%;
        margin: 0 auto;
    }}
    table.two-columns td.left {{
        width: 50%;
    }}
    table.two-columns td.right {{
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

    <table class="two-columns">
        <tr>
            <td class="left">{annotations}</td>
            <td class="right">{code}</td>
        </tr>
    </table>

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

    var speed = 300;

    // Hide non title elements for annotations that require it.
    $('div.annotation_body').each(function () {
        var meta = jQuery.parseJSON($(this).siblings('.data').text());
        if (meta.hide) {
            $(this).children('*:not(.annotation_title)').hide();
        }
    });

    function show_annotation(ann_body, adding) {

        ann_body.toggleClass('hover');

        // Display line if required.
        var meta = jQuery.parseJSON(ann_body.siblings('.data').text());
        if (meta.hide) {
            ann_body.children('*:not(.annotation_title)').slideToggle(speed);
        }

        if (meta.args == null) {
            return;
        }

        for (var i = 0; i < meta.args.length; i++) {

            var arg = meta.args[i];
            var line = $('#' + meta.prefix + 'line-' + arg.line);

            // Highlight line
            if (arg.beg == null || arg.end == null) {
                line.toggleClass('hll hll-line');
                continue;
            }

            // Highlight characters
            if (!adding) {
                line.find('.hll-char').contents().unwrap();
                continue;
            }

            var html = line.html();
            var in_tag = false;
            var buff = [];
            var codej = 0;

            for (var j = 0; j < html.length; j++) {

                var char = html.charAt(j);

                if (in_tag) {
                    if (char == '>') {
                        in_tag = false;
                    }
                    buff.push(char);
                    continue;
                }

                if (!in_tag && char == '<') {
                    in_tag = true;
                    buff.push(char);
                    continue;
                }

                if (codej >= arg.beg && codej <= arg.end) {
                    buff.push(
                        '<span class="hll hll-char">' +
                        char +
                        '</span>'
                    );
                } else {
                    buff.push(char);
                }
                codej++;
            }
            line.html(buff.join(''));
            line.addClass('hll-chars');
        }

    }

    $('div.annotation_body').hover(
        function () {
            show_annotation($(this), true);
        },
        function () {
            show_annotation($(this), false);
        }
    );
});
"""


class Processor(object):

    """
    Regular expression used to find annotations.
    """
    ann_regex = \
        r'^<\[(?P<hidden>hidden-)?annotation\]>(?P<args>[0-9, \[\]]+)? *?$'
    ann_re = re.compile(ann_regex)

    args_regex = \
        r'^(?P<line>[0-9]+)(\[(?P<beg>[0-9]+),(?P<end>[0-9]+)\])?$'
    args_re = re.compile(args_regex)

    def _parse_args(self, args, num):
        """
        Parse a string with line arguments to a list of dictionaries. Returns
        a list of dictionaries of the type:
        ```
        [
            {'line': '1', 'end': None, 'beg': None},
            {'line': '10', 'end': '20', 'beg': '0'},
            {'line': '20', 'end': '10', 'beg': '5'},
        ]
        ```

        :param str args: A string with line arguments of the type:
         ``1 10[0,20] 20[5,10]``.
        :param str num: Line number, useful for warning messages when the
         parsing fails.
        """
        parsed = []
        for token in args.strip().split():

            m = Processor.args_re.match(token)
            if not m:
                print(
                    '** WARNING: Unable to parse token "{}" '
                    'in line #{}.'.format(
                        token, num
                    )
                )
                continue

            # Map datatypes
            mapped = {
                k: (v if v is None else int(v))
                for k, v in m.groupdict().items()
            }
            parsed.append(mapped)

        return parsed

    def _parse_annotations(self, annotations, prefix):
        """
        Parse annotations from a string.

        This method allows to split a large string containing annotations and
        returns a list of tuples with (dictionary, annotation).

        :param str annotations: String with annotations.
        :param str prefix: Prefix to be used for this annotated code.
        """

        current = None
        buff = []
        parsed_anns = []

        for num, line in enumerate(annotations.splitlines(), 1):
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
                'prefix' : prefix,
                'hide' : False,
            }
            groups = m.groupdict()

            args = groups['args']
            if args is not None:
                current['args'] = self._parse_args(args, num)

            hidden = groups['hidden']
            if hidden is not None:
                current['hide'] = True

            # Reset buffer
            buff = []

        if buff:
            parsed_anns.append(
                (current, '\n'.join(buff))
            )

        return parsed_anns

    def _render_markdown(self, body, **kwargs):
        """
        Render given Markdown formatted body to HTML.

        :param str body: String with Markdown.
        """

        kwargs['output_format'] = 'html4'  # Same as Pygments
        return markdown(body, **kwargs)

    def _render_rest(self, body, **kwargs):
        """
        Render given reStructuredText formatted body to HTML.

        :param str body: String with reStructuredText.
        """

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
        """
        Render to the specified format the given parsed annotations.

        :param list parsed_anns: A list of parsed annotations in the format
         given by :meth:`Processor._parse_annotations`.
        :param str ann_format: Format to render the annotations. Supported
         formats are 'rest' and 'markdown'.
        :param dict renderer_opts: Options to be passed to the renderer.
        """

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
            if 'class' in elem.attrs:
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
            if meta['hide']:
                add_class(wrapper, 'annotation_hidden')

            for child in wrapper.children:
                if add_class(child, 'annotation_title'):
                    break
            body = str(wrapper)

            rendered_anns.append(
                annotation_tpl.format(json=dumps(meta), body=body)
            )

        return rendered_anns

    def _generate_prefix(self, length=10):
        """
        Generates a random hash to be used as prefix.

        :param int length: Size to cut the hash.
        """

        the_hash = sha1()
        the_hash.update(str(random()))
        return the_hash.hexdigest()[:length]

    def process(
            self, code, annotations,
            codefn=None, ann_format='rest',
            prefix=None, codestyle='monokai',
            renderer_opts=None):
        """
        Main processing function.

        :param str code: Code to be highlighted.
        :param str annotations: Text with annotations.
        :param str codefn: Optional "CodeFileName" that can be used to better
         detect the programming language in code.
        :param str ann_format: Format of the annotations. Supported formats are
         ``'rest'`` and ``'markdown'``.
        :param str prefix: Prefix to be used to identify this block
         (code - annotations pair). The prefix allows multiples blocks to be
         included in the same web page without interfering with each other. If
         ``None`` is given, a random prefix will be generated.
        :param str codestyle: Pygments style to be used for syntax highlight.
         See http://pygments.org/docs/styles/
        :param dict renderer_opts: Dictionary with keyword options to be passed
         to the renderer. For Markdown, this dictionary is passed to the
         ``markdown.markdown`` function as ``**kwargs``. For reStructuredText
         this dictionary is passed to the ``settings_overrides`` argument of
         the ``docutils.code.publish_parts`` function.
        """

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
        """
        Process and interpret given code file name and annotations file name.

        :param str codefn: Path to the code file.
        :param str annfn: Path to the annotations file.
        :param dict kwargs: Except for ``codefn`` (with is automatically set),
         this method supports all the other arguments
         :meth:`Processor.process`` supports.
        """

        # Warning: might raise IO exceptions
        with open(codefn, 'r') as cf:
            code = cf.read()
        with open(annfn, 'r') as af:
            annotations = af.read()
        return self.process(code, annotations, codefn=codefn, **kwargs)

    def create_document(
            self, codefn, annfn,
            title='', tpl=None, out_file=None, **kwargs):
        """

        The full content of the document is always returned.

        :param str codefn: Path to the code file.
        :param str annfn: Path to the annotations file.
        :param str title: Title of the document.
        :param str tpl: Python template string to be used a template for the
         document. See ``codeco.processor.default_tpl`` for an example. If
         ``None`` is given, the ``default_tpl`` will be used.
        :param str out_file: Optional path for the output file. If given, the
         file will be created or overriden with the content of the document.
        :param dict kwargs: Except for ``codefn`` (with is automatically set),
         this method supports all the other arguments
         :meth:`Processor.process`` supports.
        """

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
