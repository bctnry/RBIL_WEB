import os
import re
import sys

if len(sys.argv) < 2:
    print('Usage: python combine.py [file_prefix]', file=sys.stderr)
    sys.exit(1)

input_filename_prefix = sys.argv[1]
input_filename_list = []
for i in range(26):
    fn = f'{input_filename_prefix}.{chr(ord("A")+i)}'
    if not os.path.exists(fn): break
    input_filename_list.append(fn)
if len(input_filename_list) <= 0:
    print('Please make sure that you have the files.')
    sys.exit(1)
print('Found the following files:')
for i in input_filename_list:
    print(f'\t{i}')
choice = input('Continue? (y/n): ').lower()
if choice == 'n': sys.exit(1)
elif choice != 'y':
    print('Neither y nor n; abort.')
    sys.exit(1)

REGEX_HEADER = re.compile(r'--------(.)(.+)')
REGEX_TITLE = re.compile(r'.*?-?(.*)')

first_file = input_filename_list[0]
input_filename_list = input_filename_list[1:]
with open(first_file, 'rb') as f:
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
segments_rest = []
for f in input_filename_list:
    with open(f, 'rb') as f:
        source = f.read().decode('latin_1')
    for line in source.split('\r\n'):
        matchres = REGEX_HEADER.match(line)
        if matchres:
            if current_segment:
                segments_rest.append(current_segment)
                current_segment = []
        current_segment.append(line)
    if current_segment:
        segments_rest.append(current_segment)
        current_segment = []
    segments += segments_rest[1:]
    segments_rest = []

with open(f'{input_filename_prefix}.OUT', 'wb') as f:
    for line in header:
        f.write(line.encode('latin_1'))
        f.write(b'\r\n')
    for line in description:
        f.write(line.encode('latin_1'))
        f.write(b'\r\n')
    for seg in segments:
        for line in seg:
            f.write(line.encode('latin_1'))
            f.write(b'\r\n')
