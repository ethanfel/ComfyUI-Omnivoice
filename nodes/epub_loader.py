import re
import zipfile
import io
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

_BLOCK_TAGS = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'br', 'tr'}


def _local(tag):
    """Strip XML namespace prefix, return local tag name."""
    return tag.split('}')[-1]


def _extract_chapters(epub_path):
    """Parse EPUB and return list of {"title": str|None, "text": str}."""
    chapters = []
    with zipfile.ZipFile(epub_path, 'r') as zf:
        # 1. Find OPF path from container.xml
        container = ET.fromstring(zf.read('META-INF/container.xml'))
        rootfile = next(
            el for el in container.iter()
            if _local(el.tag) == 'rootfile'
        )
        opf_path = rootfile.attrib['full-path']
        opf_dir = opf_path.rsplit('/', 1)[0] + '/' if '/' in opf_path else ''

        # 2. Parse OPF: build manifest and spine
        opf = ET.fromstring(zf.read(opf_path))
        manifest = {
            el.attrib['id']: el.attrib['href']
            for el in opf.iter()
            if _local(el.tag) == 'item'
            and 'xhtml' in el.attrib.get('media-type', '')
        }
        spine = [
            el.attrib['idref']
            for el in opf.iter()
            if _local(el.tag) == 'itemref'
        ]

        # 3. Extract text from each chapter XHTML
        for idref in spine:
            href = manifest.get(idref)
            if href is None:
                continue
            xhtml = zf.read(opf_dir + href).decode('utf-8', errors='replace')
            soup = BeautifulSoup(xhtml, 'html.parser')
            for tag in soup(['script', 'style']):
                tag.decompose()
            # Title: <title> → <h1/h2/h3> → None
            title = None
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            if not title:
                for hn in ['h1', 'h2', 'h3']:
                    tag = soup.find(hn)
                    if tag:
                        title = tag.get_text(strip=True)
                        break
            for tag in soup.find_all(_BLOCK_TAGS):
                tag.append(soup.new_string('\n\n'))
            text = soup.get_text(separator='')
            text = re.sub(r'[^\S\n]+', ' ', text)   # collapse inline whitespace
            text = re.sub(r' *\n *', '\n', text)     # trim spaces around newlines
            text = re.sub(r'\n{3,}', '\n\n', text)  # max one blank line
            text = text.strip()
            chapters.append({"title": title, "text": text})

    return chapters


class OmniVoiceEpubLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "epub_path": ("STRING", {
                    "default": "",
                    "tooltip": "Absolute path to the .epub file to load.",
                }),
                "chapter_start": ("INT", {
                    "default": 1, "min": 1, "max": 9999, "step": 1,
                    "tooltip": "First chapter to include (1-indexed). Clamped to valid range automatically.",
                }),
                "chapter_end": ("INT", {
                    "default": 1, "min": 1, "max": 9999, "step": 1,
                    "tooltip": "Last chapter to include (1-indexed, inclusive). Clamped automatically. If less than chapter_start, set to chapter_start.",
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("text", "chapter_title", "chapter_list")
    FUNCTION = "load_epub"
    CATEGORY = "OmniVoice"

    def load_epub(self, epub_path, chapter_start, chapter_end):
        chapters = _extract_chapters(epub_path)
        n = len(chapters)

        if n == 0:
            return ("", "", "")

        start = max(1, min(chapter_start, n))
        end   = max(start, min(chapter_end, n))

        # chapter_list: all chapters regardless of selection
        chapter_list = "\n".join(
            f"{i}. {ch['title'] if ch['title'] else f'Chapter {i}'}"
            for i, ch in enumerate(chapters, 1)
        )

        # chapter_title: title of the first selected chapter (useful for file naming)
        first = chapters[start - 1]
        chapter_title = first["title"] if first["title"] else f"Chapter {start}"

        # text: selected range joined by delimiter
        selected = chapters[start - 1 : end]
        text = "\n\n---\n\n".join(ch["text"] for ch in selected)

        return (text, chapter_title, chapter_list)
