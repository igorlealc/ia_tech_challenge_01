import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent
INPUT_FILE = ROOT / "RELATORIO_EXPLICATIVO_PARTE_6.md"
OUTPUT_FILE = ROOT / "RELATORIO_EXPLICATIVO_PARTE_6.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyJustified",
            parent=styles["BodyText"],
            alignment=TA_JUSTIFY,
            leading=15,
            fontSize=10.5,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#17324d"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2Custom",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#17324d"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            parent=styles["BodyText"],
            leading=14,
            fontSize=10.5,
            leftIndent=14,
            bulletIndent=4,
            spaceAfter=4,
        )
    )
    return styles


def markdown_to_story(text: str):
    styles = build_styles()
    story = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            story.append(Spacer(1, 0.18 * cm))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:].strip(), styles["TitleCustom"]))
            continue

        if line.startswith("## "):
            story.append(Paragraph(line[3:].strip(), styles["H2Custom"]))
            continue

        if line.startswith("- "):
            story.append(Paragraph(line[2:].strip(), styles["BulletCustom"], bulletText="•"))
            continue

        if line.startswith("`") and line.endswith("`") and len(line) > 2:
            story.append(Paragraph(f"<font name='Courier'>{line[1:-1]}</font>", styles["BodyJustified"]))
            continue

        if line.startswith('"') and line.endswith('"') and len(line) > 2:
            story.append(Paragraph(f"<i>{line[1:-1]}</i>", styles["BodyJustified"]))
            continue

        formatted = line.replace("**", "")
        formatted = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", formatted)

        story.append(Paragraph(formatted, styles["BodyJustified"]))

    return story


def main():
    text = INPUT_FILE.read_text(encoding="utf-8")
    story = markdown_to_story(text)

    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Relatorio Explicativo - Parte 6",
        author="OpenAI Codex",
    )
    doc.build(story)
    print(f"PDF gerado em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
