import re

preamble = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OPCODES.LST</title>
    <style>
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
    </style>
</head>
<body>
'''

postamble = '''

</body>
</html>
'''

REGEX_APPENDIX = re.compile(r'APPENDIX\s+([^\s]+)(?:\s+-\s+)?\s*(.*)?')
REGEX_OPCODE = re.compile(r'(?:OPCODE\s+)?(.*?)\s+-?\s+(.*)')

with open('OPCODES.LST', 'rb') as f:
    source = f.read().decode('latin_1')

segments = []
current_segment = []

for line in source.split('\r\n'):
    if line.startswith('------------------'):
        if current_segment:
            segments.append(current_segment)
            current_segment = []
    current_segment.append(line)
if current_segment:
    segments.append(current_segment)
    current_segment = []

header = segments[0]
description = segments[1]
segments = segments[2:]

parsed_segments = []

cnt = 0
for seg in segments:
    if len(seg) < 2: continue
    matchres = REGEX_APPENDIX.match(seg[1])
    if matchres:
        # appendix.
        groups = matchres.groups()
        parsed_segments.append(('APPX', groups[0], groups[1], seg[2:]))
        continue

    matchres = REGEX_OPCODE.match(seg[1])
    if matchres:
        # opcode.
        groups = matchres.groups()
        parsed_segments.append(('OP', groups[0], groups[1], seg[2:]))
        continue

    parsed_segments.append((None, f'__id{cnt}', seg[1], seg[2:]))
    cnt += 1

# collect toc.
alpha_idx = {}
for seg in parsed_segments:
    if seg[0] == 'OP':
        if not alpha_idx.get(seg[1][0]):
            alpha_idx[seg[1][0]] = []
        alpha_idx[seg[1][0]].append(seg[1])

with open('OPCODES.LST.HTML', 'w') as f:
    f.write(preamble)

    # write header.
    f.write('\n<p>\n')
    for line in header:
        f.write(f'\n<b>{line}</b><br />\n')
    f.write('\n</p>\n')

    # write description.
    f.write('\n<pre>\n')
    for line in description:
        f.write(line)
        f.write('\n')
    f.write('\n</pre>\n')

    # write toc.
    f.write('\n<p>\n<a name="__toc"><b>Table of Contents</b></a><br />\n\n')
    for ak in sorted(alpha_idx):
        f.write(f'<b>{ak}</b>&nbsp;&nbsp;')
        for i in alpha_idx[ak]:
            f.write(f'<a href="#{i}">{i}</a>&nbsp;&nbsp; ')
        f.write('<br />\n')
    f.write('\n</p>\n')

    # write toc for appendix.
    f.write('\n<p><b>Appendix</b><br />\n')
    for typ, i, title, body in parsed_segments:
        if typ != 'APPX': continue
        f.write(f'<a href="#_appx{i}"><b>APPENDIX {i}: {title}</b></a><br />\n')
    f.write('\n</p>\n')

    f.write('\n<hr />\n')

    # write body.
    for typ, i, title, body in parsed_segments:
        if typ == 'OP':
            f.write(f'\n<a href="{i}" name="{i}"><b>{i}</b></a> - {title}<br />')
        elif typ == 'APPX':
            f.write(f'\n<a href="{i}" name="_appx{i}"><b>APPENDIX {i}</b></a> - {title}<br />')

        f.write('\n<pre>\n')
        for line in body:
            f.write(line.replace('<', '&lt;').replace('>', '&gt;'))
            f.write('\n')
        f.write('\n</pre>\n')
        f.write('\n<span style="font-size:80%"><a href="#__toc">Top</a></span>\n')
        f.write('\n<hr />\n')

    f.write('\n<div class="bottom-nav"><b><a href="./index.html">Home</a></b> <b>TOC</b>: <a href="#__toc">by Order</a> <b><a href="#top">Top</a></b></div>')
    f.write(postamble)
