from pathlib import Path
import base64
import re

folder = Path(__file__).resolve().parent
page = folder / 'index.html'
text = page.read_text(encoding='utf-8')
svg = (folder / 'architecture.drawio.svg').read_bytes()
text, count = re.subn(r'src="(?:architecture\.drawio\.svg|data:image/svg\+xml;base64,[A-Za-z0-9+/=]+)"', 'src="data:image/svg+xml;base64,' + base64.b64encode(svg).decode('ascii') + '"', text)
if count != 1:
    raise RuntimeError(f'Expected one diagram image, got {count}')
page.write_text(text, encoding='utf-8')
print({'html_bytes': page.stat().st_size, 'embedded_diagram': 'src="data:image/svg+xml;base64,' in text})
