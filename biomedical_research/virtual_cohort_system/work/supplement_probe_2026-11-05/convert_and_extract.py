"""Local conversion of verified source only; visible-text admission, not model feedback."""
from pathlib import Path
import json
import subprocess
import time
import zipfile
import xml.etree.ElementTree as ET
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader
from probe import ROOT, FILENAME, sha, require, write_json, frozen_hashes, screen_text

OFFICE = Path('D:/Codex/home/Documents/Codex/2026-09-07/word-tab-2/work/lo-render/program/soffice.com')
POPPLER = Path('C:/Users/ziwan/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')

def main():
    acquired = json.loads((ROOT / 'ACQUISITION_RECEIPT.json').read_text(encoding='utf-8'))
    require(acquired['status'] == 'verified_download_only', 'Acquisition not verified')
    original = ROOT / 'local_source' / FILENAME
    require(sha(original.read_bytes()) == acquired['sha256'], 'Original file changed')
    converted = ROOT / 'local_converted'
    converted.mkdir(exist_ok=True)
    profile = ROOT / 'local_lo_profile'
    (profile / 'user').mkdir(parents=True, exist_ok=True)
    (profile / 'user/registrymodifications.xcu').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry">
<item oor:path="/org.openoffice.Office.Common/Security/Scripting"><prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop></item>
<item oor:path="/org.openoffice.Office.Writer/Content/Update"><prop oor:name="Link" oor:op="fuse"><value>0</value></prop></item>
</oor:items>''', encoding='utf-8')
    receipt = {'status': 'converting', 'network_requests': 0, 'original_sha256': acquired['sha256'],
               'office_binary': str(OFFICE), 'office_binary_sha256': sha(OFFICE.read_bytes()),
               'profile_settings': {'MacroSecurityLevel': 3, 'WriterLinkUpdate': 0}, 'steps': []}
    log = ROOT / 'CONVERSION_RECEIPT.json'
    require(not log.exists(), 'Conversion already attempted; inspect existing receipt first')
    write_json(log, receipt)
    try:
        receipt['office_version'] = subprocess.check_output([str(OFFICE), '--version'], timeout=30, text=True).strip()
        for fmt in ['docx:Office Open XML Text', 'pdf:writer_pdf_Export']:
            command = [str(OFFICE), '-env:UserInstallation=' + profile.as_uri(), '--headless',
                       '--nologo', '--nodefault', '--norestore', '--convert-to', fmt,
                       '--outdir', str(converted), str(original)]
            started = time.monotonic()
            result = subprocess.run(command, capture_output=True, timeout=60, text=True)
            receipt['steps'].append({'format': fmt, 'returncode': result.returncode,
                                     'stdout': result.stdout, 'stderr': result.stderr,
                                     'seconds': round(time.monotonic()-started, 3)})
            require(result.returncode == 0, 'Conversion process failed')
        docx = converted / (original.stem + '.docx')
        pdf = converted / (original.stem + '.pdf')
        require(docx.is_file() and pdf.is_file(), 'Missing converted output')
        document = Document(docx)
        paragraphs, tables, blocks = [], [], []
        for element in document.element.body:
            tag = element.tag.rsplit('}', 1)[-1]
            if tag == 'p':
                text = Paragraph(element, document).text
                paragraphs.append(text)
                blocks.append(text)
            elif tag == 'tbl':
                t = Table(element, document)
                rows = [[cell.text for cell in row.cells] for row in t.rows]
                tables.append({'table_index': len(tables)+1, 'rows': rows})
                blocks.append('TABLE ' + str(len(tables)) + '\n' + '\n'.join('\t'.join(r) for r in rows))
        # Screen all OOXML text including metadata, footnotes, headers and hidden XML text.
        xml_texts = []
        with zipfile.ZipFile(docx) as z:
            for name in z.namelist():
                if name.endswith('.xml'):
                    raw = z.read(name).decode('utf-8')
                    screen_text(raw)
                    text = '\n'.join(ET.fromstring(raw).itertext())
                    xml_texts.append(text)
                    screen_text(text)
        reader = PdfReader(pdf)
        page_texts = [p.extract_text() or '' for p in reader.pages]
        require(all(t.strip() for t in page_texts), 'Empty rendered page extraction')
        text = '\n\n'.join(blocks)
        screen_text(text)
        screen_text('\n'.join(page_texts))
        screen_text(str(reader.metadata))
        require(len(tables) > 0 and 'Table S1' in text and 'Table S2' in text,
                'Expected source table labels missing')
        (converted / 'VISIBLE_TEXT.txt').write_text(text, encoding='utf-8')
        write_json(converted / 'TABLES.json', tables)
        (converted / 'PDF_TEXT.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(page_texts)), encoding='utf-8')
        images = converted / 'pages'
        images.mkdir(exist_ok=True)
        render = subprocess.run([str(POPPLER), '-r', '140', '-png', str(pdf), str(images/'page')],
                                capture_output=True, text=True, timeout=60)
        require(render.returncode == 0, 'Rendering failed')
        receipt.update(status='visible_text_admitted_pending_visual_scientific_review',
                       table_count=len(tables), paragraph_count=len(paragraphs), pdf_pages=len(reader.pages),
                       extraction_scope='Converted body/tables, all OOXML text/metadata and rendered PDF text. Not all binary or embedded objects certified.',
                       generated_files={str(p.relative_to(ROOT)): {'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
                                        for p in converted.rglob('*') if p.is_file()},
                       frozen_unchanged=frozen_hashes()==acquired['frozen_before'])
    except Exception as e:
        receipt.update(status='failed', error_type=type(e).__name__, error=str(e))
        raise
    finally:
        write_json(log, receipt)
    print(json.dumps({k:receipt[k] for k in ('status','table_count','pdf_pages','frozen_unchanged')}))

if __name__ == '__main__':
    main()
