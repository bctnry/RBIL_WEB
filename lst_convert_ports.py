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

preamble = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PORTS</title>
    <style>{style}</style>
</head>
<body>
'''

postamble = '''

</body>
</html>
'''

category = {
    'A': 'applications',
    'a': 'access software (screen readers, etc)',
    'B': 'BIOS',
    'b': 'vendor-specific BIOS extensions,',
    'C': 'CPU-generated',
    'c': 'caches/spoolers,',
    'D': 'DOS kernel',
    'd': 'disk I/O enhancements,',
    'E': 'DOS extenders',
    'e': 'electronic mail',
    'F': 'FAX,',
    'f': 'file manipulation',
    'G': 'debuggers/debugging tools',
    'g': 'games,',
    'H': 'hardware',
    'h': 'vendor-specific hardware,',
    'I': 'IBM workstation/terminal emulators',
    'i': 'system info/monitoring,',
    'J': 'Japanese',
    'j': 'joke programs,',
    'K': 'keyboard enhancers',
    'k': 'file/disk compression,',
    'l': 'shells/command interpreters,',
    'M': 'mouse/pointing device',
    'm': 'memory management,',
    'N': 'network',
    'n': 'non-traditional input devices,',
    'O': 'other operating systems,',
    'P': 'printer enhancements',
    'p': 'power management,',
    'Q': 'DESQview/TopView and Quarterdeck programs,',
    'R': 'remote control/file access',
    'r': 'runtime support,',
    'S': 'serial I/O',
    's': 'sound/speech,',
    'T': 'DOS-based task switchers/multitaskers',
    't': 'TSR libraries',
    'U': 'resident utilities',
    'u': 'emulators,',
    'V': 'video',
    'v': 'virus/antivirus,',
    'W': 'MS Windows,',
    'X': 'expansion bus BIOSes',
    'x': 'non-volatile config storage',
    'y': 'security',
    '*': 'reserved (and not otherwise classified)',
    '!': 'document info',
    '-': 'uncategorized',
}

REGEX_HEADER = re.compile(r'--------(.)(.+)')
REGEX_TITLE = re.compile(r'.*?-?(.*)')

with open('PORTS.A', 'rb') as f:
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

# process PORTS.B and PORTS.C
segments_b = []
with open('PORTS.B', 'rb') as f:
    source = f.read().decode('latin_1')
for line in source.split('\r\n'):
    matchres = REGEX_HEADER.match(line)
    if matchres:
        if current_segment:
            segments_b.append(current_segment)
            current_segment = []
    current_segment.append(line)
if current_segment:
    segments_b.append(current_segment)
    current_segment = []
segments_c = []
with open('PORTS.C', 'rb') as f:
    source = f.read().decode('latin_1')
for line in source.split('\r\n'):
    matchres = REGEX_HEADER.match(line)
    if matchres:
        if current_segment:
            segments_c.append(current_segment)
            current_segment = []
    current_segment.append(line)
if current_segment:
    segments_c.append(current_segment)
    current_segment = []
segments += segments_b[1:]
segments += segments_c[2:]

parsed_segments = []

ids = {}

for seg in segments:
    if len(seg) < 2: continue
    matchres = REGEX_HEADER.match(seg[0])
    typ, i = matchres.groups()
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

# collect category toc.
alpha_idx = {}
for seg in parsed_segments:
    if not alpha_idx.get(seg[0]):
        alpha_idx[seg[0]] = []
    alpha_idx[seg[0]].append((seg[1], seg[2], seg[4]))

with open(f'PORTS.LST.HTML', 'w') as f:
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

    f.write('\n<p><b><a name="__toc">Table of Contents</a></b>: <a href="#__toc_order">by Order</a> <a href="#__toc_cat">by Category</a></p>\n')

    f.write('\n<p>\n<a name="__toc_order"><b>Table of Contents by Order</b></a><br />\n\n')
    for typ, i, title, body, link_id in parsed_segments:
        f.write(f'<a href="#{link_id}"><b>{i}</b> - {title}</a><br />\n')
    f.write('\n<span style="font-size:80%"><a href="#__toc">Top</a></span>\n')


    f.write('\n<h3>\n<a name="__toc_cat"><b>Table of Contents by Category</b></a></h3>\n\n')
    for ak in sorted(alpha_idx):
        f.write(f'<a href="#__cat_{ak}"><b>{ak}</b>')
        if ak in category:
            f.write(f' - {category[ak]}')
        f.write('</a><br />\n')
    f.write('<br />\n')
    for ak in sorted(alpha_idx):
        f.write(f'<h4><a name="__cat_{ak}"><b>{ak}</b></a>')
        if ak in category:
            f.write(f' - {category[ak]}')
        f.write('</h4>\n')
        for i, title, link_id in alpha_idx[ak]:
            f.write(f'<a href="#{link_id}"><b>{i}</b> - {title}</a><br />\n')
        f.write('\n<span style="font-size:80%"><a href="#__toc_cat">Top</a></span>\n')
        f.write('<br />\n')

    f.write('\n<hr />\n')

    # write body.
    for typ, i, title, body, link_id in parsed_segments:
        f.write(f'\n<a href="#{link_id}" name="{link_id}"><b>{i}</b></a> - {title}<br />')

        f.write('\n<pre>\n')
        for line in body:
            f.write(line.replace('&', '&amp;')..replace('<', '&lt;').replace('>', '&gt;'))
            f.write('\n')
        f.write('\n</pre>\n')
        f.write('\n<span style="font-size:80%"><a href="#__toc">Top</a></span>\n')
        f.write('\n<hr />\n')

    f.write('\n<div class="bottom-nav"><b><a href="./index.html">Home</a></b> <b>TOC</b>: <a href="#__toc_order">by Order</a> <a href="#__toc_cat">by Category</a> <b><a href="#top">Top</a></b></div>')
    f.write(postamble)
