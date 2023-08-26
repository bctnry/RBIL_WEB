import os
import sys

if len(sys.argv) < 2:
    print('Usage: python convert_raw.py [file]', file=sys.stderr)
    sys.exit(1)

if not os.path.exists(sys.argv[1]):
    print('Please make sure that you have the file.')
    sys.exit(1)

input_filename = sys.argv[1]

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
    <title>{input_filename}</title>
    <style>{style}</style>
</head>
<body>
'''

postamble = '''

</body>
</html>
'''

with open(input_filename, 'rb') as f:
    source = f.read().decode('cp437')

with open(f'{input_filename}.HTML', 'w') as f:
    f.write(preamble)
    f.write('\n<pre>\n')
    for line in source.split('\r\n'):
        f.write(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        f.write('\n')
    f.write('\n</pre>\n')

    f.write('\n<div class="bottom-nav"><b><a href="./index.html">Home</a></b> <b><a href="#top">Top</a></b></div>')
    f.write(postamble)

