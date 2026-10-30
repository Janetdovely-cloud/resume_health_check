"""把手寫字型裁成 index.html 實際用到的字，重新嵌回頁面。每次改完文字後執行：
    python3 -m pip install fonttools brotli
    python3 tools/subset_font.py
"""
import base64, io, pathlib, re
from fontTools import subset

root = pathlib.Path(__file__).resolve().parent.parent
page = root / "index.html"
full = root / "tools" / "ChenYuluoyan-full.woff"
pat = re.compile(r"url\(data:font/woff2?;base64,[A-Za-z0-9+/=]+\)")

html = page.read_text(encoding="utf-8")
text = pat.sub("", html)
chars = {c for c in text if ord(c) >= 32} | {chr(c) for c in range(32, 127)}

opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["*"]
font = subset.load_font(str(full), opts)
sub = subset.Subsetter(opts)
sub.populate(text="".join(chars))
sub.subset(font)
buf = io.BytesIO()
subset.save_font(font, buf, opts)
data = base64.b64encode(buf.getvalue()).decode()

html, n = pat.subn(lambda m: "url(data:font/woff2;base64," + data + ")", html, count=1)
assert n == 1, "找不到嵌入字型"
html = html.replace('format("woff")', 'format("woff2")')
page.write_text(html, encoding="utf-8")
print(f"字數 {len(chars)}，字型 {len(buf.getvalue())//1024} KB，頁面 {len(html.encode())//1024} KB")
