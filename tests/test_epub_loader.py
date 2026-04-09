import io
import zipfile
from unittest.mock import patch
import pytest
from nodes.epub_loader import OmniVoiceEpubLoader

# Capture the real ZipFile class BEFORE any patching so epub_opener can use it
# without hitting the patch and causing infinite recursion.
_RealZipFile = zipfile.ZipFile

_CONTAINER_XML = """<?xml version="1.0"?>
<container xmlns="urn:oasis:schemas:container" version="1.0">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""


def make_fake_epub(chapters):
    """chapters: list of (title, body_html). Returns EPUB bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip')
        z.writestr('META-INF/container.xml', _CONTAINER_XML)
        items = "\n".join(
            f'<item id="ch{i}" href="ch{i}.xhtml" media-type="application/xhtml+xml"/>'
            for i in range(len(chapters))
        )
        spine = "\n".join(f'<itemref idref="ch{i}"/>' for i in range(len(chapters)))
        opf = f"""<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf">
  <manifest>{items}</manifest>
  <spine>{spine}</spine>
</package>"""
        z.writestr('OEBPS/content.opf', opf)
        for i, (title, body) in enumerate(chapters):
            z.writestr(f'OEBPS/ch{i}.xhtml',
                f'<html><head><title>{title}</title></head><body><h1>{title}</h1>{body}</body></html>')
    buf.seek(0)
    return buf.read()


def epub_opener(epub_bytes):
    def _open(path, mode='r'):
        return _RealZipFile(io.BytesIO(epub_bytes), mode)
    return _open


def test_input_types_structure():
    inputs = OmniVoiceEpubLoader.INPUT_TYPES()
    req = inputs["required"]
    assert "epub_path" in req
    assert req["epub_path"][0] == "STRING"
    assert "chapter_start" in req
    assert req["chapter_start"][0] == "INT"
    assert "chapter_end" in req
    assert req["chapter_end"][0] == "INT"


def test_return_types():
    assert OmniVoiceEpubLoader.RETURN_TYPES == ("STRING", "STRING", "STRING")
    assert OmniVoiceEpubLoader.RETURN_NAMES == ("text", "chapter_title", "chapter_list")


def test_chapter_extraction_basic():
    epub = make_fake_epub([("Intro", "<p>Hello world</p>"), ("Chapter One", "<p>Body here</p>")])
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(epub)):
        text, chapter_title, chapter_list = OmniVoiceEpubLoader().load_epub('/fake.epub', 1, 2)
    assert "Hello world" in text
    assert "Body here" in text
    assert "---" in text
    assert len(chapter_list.strip().splitlines()) == 2


def test_chapter_range_single():
    epub = make_fake_epub([("One", "<p>First</p>"), ("Two", "<p>Second</p>"), ("Three", "<p>Third</p>")])
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(epub)):
        text, _, _ = OmniVoiceEpubLoader().load_epub('/fake.epub', 2, 2)
    assert "Second" in text
    assert "First" not in text
    assert "Third" not in text


def test_chapter_list_contains_all():
    epub = make_fake_epub([("A", ""), ("B", ""), ("C", "")])
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(epub)):
        _, _, chapter_list = OmniVoiceEpubLoader().load_epub('/fake.epub', 2, 2)
    lines = chapter_list.strip().splitlines()
    assert len(lines) == 3
    assert lines[0].startswith("1.")
    assert lines[2].startswith("3.")


def test_range_clamping_high():
    epub = make_fake_epub([("A", "<p>aaa</p>"), ("B", "<p>bbb</p>")])
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(epub)):
        text, _, _ = OmniVoiceEpubLoader().load_epub('/fake.epub', 1, 99)
    assert "aaa" in text and "bbb" in text


def test_range_clamping_end_below_start():
    epub = make_fake_epub([("A", "<p>aaa</p>"), ("B", "<p>bbb</p>")])
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(epub)):
        text, _, _ = OmniVoiceEpubLoader().load_epub('/fake.epub', 2, 1)
    assert "bbb" in text
    assert "aaa" not in text


def test_missing_title_fallback():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip')
        z.writestr('META-INF/container.xml', _CONTAINER_XML)
        z.writestr('OEBPS/content.opf', """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf">
  <manifest><item id="ch0" href="ch0.xhtml" media-type="application/xhtml+xml"/></manifest>
  <spine><itemref idref="ch0"/></spine>
</package>""")
        z.writestr('OEBPS/ch0.xhtml', '<html><body><p>No title here</p></body></html>')
    buf.seek(0)
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(buf.read())):
        _, _, chapter_list = OmniVoiceEpubLoader().load_epub('/fake.epub', 1, 1)
    assert "1. Chapter 1" in chapter_list


def test_script_style_stripped():
    epub = make_fake_epub([("Test", '<script>alert("xss")</script><style>color:red</style><p>clean</p>')])
    with patch('nodes.epub_loader.zipfile.ZipFile', side_effect=epub_opener(epub)):
        text, _, _ = OmniVoiceEpubLoader().load_epub('/fake.epub', 1, 1)
    assert "alert" not in text
    assert "color" not in text
    assert "clean" in text
