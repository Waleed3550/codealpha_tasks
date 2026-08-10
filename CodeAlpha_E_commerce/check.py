import io, re
with io.open('output.html', 'r', encoding='utf-16le', errors='ignore') as f:
    content = f.read()
for m in re.findall(r'<strong[^>]*>.*?</strong>', content):
    print(m)
