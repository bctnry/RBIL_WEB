import os
import re
import sys

style = '''
        body {
            font-variant-ligatures: none;
        }
        pre {
            font-family: 'Courier New', Courier, monospace;
        }
        a {
            color: black;
        }
        .bottom-nav {
            position: sticky;
            bottom: 0px;
            background-color: white;
            text-align: right;
        }
        h3, h4 {
            margin: 0;
        }
'''

preamble = lambda title: f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{style}</style>
</head>
<body>
'''

postamble = '''

</body>
</html>
'''

input_filename_prefix = 'INTERRUP'
input_filename_list = []
for i in range(26):
    fn = f'{input_filename_prefix}.{chr(ord("A")+i)}'
    if not os.path.exists(fn): break
    input_filename_list.append(fn)
if len(input_filename_list) <= 0:
    print('Please make sure that you have the files.')
    sys.exit(1)

REGEX_HEADER = re.compile(r'--------(.)(.+)')
REGEX_TITLE = re.compile(r'.*?-?(.*)')

def read_file(filename):
    with open(filename, 'rb') as f:
        source = f.read().decode('latin_1')

    segments = []
    current_segment = []

    for line in source.split('\r\n'):
        matchres = REGEX_HEADER.match(line)
        if matchres:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
        current_segment.append(line)
    if current_segment:
        segments.append(current_segment)
        current_segment = []

    header = segments[0][:2]
    description = segments[0][2:]
    segments = segments[1:]
    return (header, description, segments)

def parse_segment_list(segments, ids={}):
    parsed_segments = []

    for seg in segments:
        if len(seg) < 2: continue
        matchres = REGEX_HEADER.match(seg[0])
        typ, i = matchres.groups()
        if typ == '!': continue
        i = i.strip('-')
        if i in ids:
            link_id = f'{i}_{ids[i]}'
            ids[i] += 1
        else:
            link_id = i
            ids[i] = 0

        matchres = REGEX_TITLE.match(seg[1])
        title = matchres.groups()[0].strip()
        parsed_segments.append((typ, i, title, seg[1:], link_id))
    return ids, parsed_segments

ids = {}
alpha_idx = {}
for f in input_filename_list:
    header, description, segments = read_file(f)
    ids, parsed_segments = parse_segment_list(segments, ids=ids)

    for seg in parsed_segments:
        num = seg[1][:2]
        if not alpha_idx.get(num):
            alpha_idx[num] = []
        alpha_idx[num].append(seg)

with open('INTERRUP.NUM.HTML', 'w') as f:
    f.write(preamble(f'INTERRUP.NUM'))
    # write header.
    f.write('''
<b>Interrupt List Release 61 Last change 16jul00</b><br />
<b>Copyright (c) 1989-1999,2000 Ralf Brown</b><br />
<pre>
''')
    f.write(f'Index by Interrupt Number')
    f.write('''
</pre>
''')

    f.write('\n<p>\n<a name="__toc_order"><b>Table of Contents by Order</b></a><br />\n\n')
    cnt = 0
    for ai in sorted(alpha_idx):
        path_ai = ai
        f.write(f'<a href="./INTERRUP.{path_ai}.HTML">{ai}</a>&nbsp;&nbsp; \n')
        cnt += 1
        if cnt >= 8:
            f.write('<br />\n')
            cnt = 0

    f.write('\n<div class="bottom-nav"><b><a href="./index.html">Home</a></b> <b>TOC</b>: <a href="#__toc_order">by Order</a> <b><a href="#top">Top</a></b></div>')

for ai in alpha_idx:
    path_ai = ai if ai != '!' else '_'
    with open(f'INTERRUP.{path_ai}.HTML', 'w') as f:
        f.write(preamble(f'INTERRUP._{path_ai}'))

        # write header.
        f.write('''
<b>Interrupt List Release 61 Last change 16jul00</b><br />
<b>Copyright (c) 1989-1999,2000 Ralf Brown</b><br />
<pre>
''')
        f.write(f'Index for interrupt INT {ai}')
        f.write('''
</pre>
''')

        f.write('\n<p>\n<a name="__toc"><b>Table of Contents by Order</b></a><br />\n\n')
        for typ, i, title, body, link_id in alpha_idx[ai]:
            f.write(f'<a href="#{link_id}"><b>{i}</b> - {title}</a><br />\n')

        f.write('\n<hr />\n')

        # write body.
        for typ, i, title, body, link_id in alpha_idx[ai]:
            f.write(f'\n<a href="#{link_id}" name="{link_id}"><b>{i}</b></a> - {title}<br />')

            f.write('\n<pre>\n')
            for line in body:
                f.write(line.replace('<', '&lt;').replace('>', '&gt;'))
                f.write('\n')
            f.write('\n</pre>\n')
            f.write('\n<span style="font-size:80%"><a href="#__toc">Top</a></span>\n')
            f.write('\n<hr />\n')

        f.write('\n<div class="bottom-nav"><b><a href="./index.html">Home</a></b> <b>Interrupt Index</b>: <a href="./INTERRUP.CAT.HTML">by Category</a> <a href="./INTERRUP.NUM.HTML">by Number</a> <b>TOC</b>: <a href="#__toc">by Order</a> <b><a href="#top">Top</a></b></div>')
        f.write(postamble)

