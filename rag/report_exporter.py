import html
import io
import textwrap
import zipfile


def build_markdown_report(report):
    outputs = report.get("outputs", {})
    lines = [
        "# Agentic AI Research Companion Report",
        "",
        f"Task: {report.get('task', 'research analysis')}",
        f"Confidence Score: {report.get('confidence_score', 0)}",
        "",
        "## Agent Plan",
        "",
    ]
    lines.extend(f"- {agent}" for agent in report.get("plan", []))
    lines.append("")

    for key, value in outputs.items():
        title = key.replace("_", " ").title()
        lines.extend([f"## {title}", ""])
        if isinstance(value, dict):
            if "novelty_score" in value:
                lines.append(f"Novelty Score: {value['novelty_score']}/100")
                lines.append("")
            lines.append(str(value.get("analysis", value)))
        else:
            lines.append(str(value))
        lines.append("")

    lines.extend(["## Evidence", ""])
    for item in report.get("evidence", []):
        score = item.get("similarity_score")
        score_text = f"{score:.2f}" if isinstance(score, float) else "n/a"
        lines.append(f"- Source: {item.get('source')} | Chunk: {item.get('chunk_index')} | Similarity: {score_text}")
        lines.append(f"  {str(item.get('chunk', ''))[:500]}")

    return "\n".join(lines).strip() + "\n"


def build_docx_report(report):
    markdown = build_markdown_report(report)
    body = "".join(f"<w:p><w:r><w:t>{html.escape(line)}</w:t></w:r></w:p>" for line in markdown.splitlines())
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>{body}<w:sectPr/></w:body>
</w:document>"""

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf_report(report):
    text = build_markdown_report(report)
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width=92) or [""])

    objects = []
    content_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    for line in lines[:52]:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"({escaped}) Tj")
        content_lines.append("T*")
    content_lines.append("ET")
    content = "\n".join(content_lines)

    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append("<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>")
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(f"<< /Length {len(content.encode('latin-1', errors='ignore'))} >>\nstream\n{content}\nendstream")

    pdf = ["%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1", errors="ignore")) for part in pdf))
        pdf.append(f"{index} 0 obj\n{obj}\nendobj\n")
    xref_offset = sum(len(part.encode("latin-1", errors="ignore")) for part in pdf)
    pdf.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.append(f"{offset:010d} 00000 n \n")
    pdf.append(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF")
    return "".join(pdf).encode("latin-1", errors="ignore")

