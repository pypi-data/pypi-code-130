from textwrap import wrap
from tqdm import tqdm

# Load in primary HTML
lines = open('launcher_code.html', 'r').readlines()

# Load CSS file
def load_stylesheet(line):
    file_path  = line.split('href=\"')[1]
    file_path = file_path.split('\"')[0]
    return open(file_path, 'r', encoding='utf-8', errors='ignore').read()

# Load JS file
def load_script(line):
    file_path  = line.split('src=\"')[1]
    file_path = file_path.split('\"')[0]
    return open(file_path, 'r', encoding='utf-8', errors='ignore').read()

# Scan for CSS and JS
out_lines = []
print('Merging Files...')
for line in tqdm(lines):
    if 'rel="stylesheet"' in line:
        out_lines.append('\n<!-- START INSERTION  -->\n')
        stylesheet = "<style>\n" + load_stylesheet(line) + "\n</style>\n"
        out_lines.append(stylesheet)
        out_lines.append('\n<!-- END INSERTION  -->\n')
    elif '<script' in line and 'src' in line:
        out_lines.append('\n<!-- START INSERTION  -->\n')
        out_lines.append('<script>\n' + load_script(line) + '\n</script>\n')
        out_lines.append('\n<!-- END INSERTION  -->\n')
    else:
        out_lines.append(line)

# Write script to file
print("Writing to file...")
with open('launcher_code_archive.html', 'w', encoding='utf-8', errors='ignore') as f:
    for line in out_lines:
        f.write(line)