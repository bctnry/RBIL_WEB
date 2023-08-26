input_filename = '86BUGS.LST'
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
        h2 { font-size: 1rem; }
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
    <title>{input_filename}</title>
    <style>{style}</style>
</head>
<body>
'''

postamble = '''

</body>
</html>
'''

with open('86BUGS.LST', 'rb') as f:
    source = f.read()

source = source.decode('cp437')
source_lines = source.split('\r\n')
sanitize = lambda x: x.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

last_i = 0
sections = []
for i, line in enumerate(source_lines):
    if line.strip() and not line.strip('─'):
        sections.append(source_lines[last_i:i-1])
        last_i = i-1

# there are empty lines after each segment which doesn't look good
# enough when converted. here we delete those lines.
for section in sections:
    while not section[-1] or not section[-1].strip():
        section.pop()

with open('86BUGS.LST.HTML', 'w') as f:
    f.write(preamble)
    f.write('<b>86BUGS.LST</b><br /><br />\n')

    # toc.
    f.write('<a name="__toc"><b>Table of Contents</b></a><br />\n')
    for i, section in enumerate(sections[1:]):
        f.write(f'<a href="#__sec{i+1}">Section {i+1}: {sanitize(section[0])}</a><br />\n')


    for i, section in enumerate(sections):
        if not section: continue
        print(section)
        f.write(f'<h2><a name="__sec{i}">{sanitize(section[0])}</a></h2>')
        f.write('\n<pre>\n')
        for line in section[2:]:
            f.write(sanitize(line))
            f.write('\n')
        f.write('\n</pre>\n')
        f.write('\n<span style="font-size:80%"><a href="#__toc">Top</a></span>\n')
        f.write('\n<hr />\n')
    f.write('\n<div class="bottom-nav"><b><a href="./index.html">Home</a></b> <b><a href="#__toc">TOC</a></b> <b><a href="#top">Top</a></b></div>')
    f.write(postamble)


