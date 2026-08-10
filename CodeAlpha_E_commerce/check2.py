import io, re
with io.open('output.html', 'r', encoding='utf-16le', errors='ignore') as f:
    content = f.read()
print('Labels:', re.findall(r'<script id="monthly-labels"[^>]*>(.*?)</script>', content, re.DOTALL))
print('Revenue:', re.findall(r'<script id="monthly-revenue"[^>]*>(.*?)</script>', content, re.DOTALL))
