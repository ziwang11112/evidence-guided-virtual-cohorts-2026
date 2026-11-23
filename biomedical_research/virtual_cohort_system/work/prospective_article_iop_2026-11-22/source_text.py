"""Extract study text, table cells and captions from the publisher JATS for the author."""
from pathlib import Path
from lxml import etree as ET

HERE = Path(__file__).resolve().parent


def text(node):
    return " ".join("".join(node.itertext()).split())


def section(node):
    for child in node:
        tag = child.tag
        if tag in {"table-wrap", "fig"}:
            for part in child.xpath("./label|./caption"):
                yield text(part)
            for row in child.xpath(".//tr"):
                yield " | ".join(text(cell) for cell in row)
        elif tag in {"title", "p"}:
            # Captions embedded within prose are emitted separately once.
            if child.xpath(".//table-wrap|.//fig"):
                normal = ET.fromstring(ET.tostring(child, with_tail=False))
                for element in normal.xpath(".//table-wrap|.//fig"):
                    if element.tail:
                        before = element.getprevious()
                        if before is None:
                            element.getparent().text = (element.getparent().text or "") + element.tail
                        else:
                            before.tail = (before.tail or "") + element.tail
                    element.getparent().remove(element)
                yield text(normal)
                yield from section(child)
            else:
                yield text(child)
        elif tag in {"sec", "list", "list-item", "boxed-text"}:
            yield from section(child)
        elif tag == "disp-formula":
            yield text(child) or "[Equation supplied as an image in publisher XML]"


if __name__ == "__main__":
    tree = ET.parse(HERE / "private/source.xml", ET.XMLParser(resolve_entities=False, no_network=True))
    parts = [text(tree.find(".//article-title")), text(tree.find(".//abstract"))]
    parts.extend(section(tree.find(".//body")))
    output = "\n\n".join(part for part in parts if part) + "\n"
    # Guard against silently losing a source table or figure caption.
    for elem in tree.xpath("//body//table-wrap/caption|//body//fig/caption"):
        if text(elem) not in output:
            raise ValueError("Missing caption")
    for tr in tree.xpath("//body//table-wrap//tr"):
        if " | ".join(text(cell) for cell in tr) not in output:
            raise ValueError("Missing table row")
    (HERE / "private/article.txt").write_text(output, encoding="utf8")
