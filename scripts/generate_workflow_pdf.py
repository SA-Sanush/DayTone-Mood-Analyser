import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas class to generate 'Page X of Y' page numbers dynamically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header (Top)
        self.drawString(54, 750, "DayTone System Architecture & Product Workflow")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer (Bottom)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential - DayTone AI Wellness Platform")
        self.line(54, 52, 558, 52)
        
        self.restoreState()


def parse_markdown_to_pdf_story(md_path, styles):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    story = []
    
    # Custom styles
    title_style = styles["AppTitle"]
    h2_style = styles["ModuleHeader"]
    h3_style = styles["SectionHeader"]
    body_style = styles["CustomBody"]
    bullet_style = styles["CustomBullet"]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse H1
        if line.startswith("# "):
            text = line[2:]
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 15))
            
        # Parse H2 (e.g. ## Module 1...)
        elif line.startswith("## "):
            text = line[3:]
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Spacer(1, 12))
            story.append(Paragraph(text, h2_style))
            story.append(Spacer(1, 8))
            
        # Parse H3 (e.g. ### Key Functionalities)
        elif line.startswith("### "):
            text = line[4:]
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Spacer(1, 8))
            story.append(Paragraph(text, h3_style))
            story.append(Spacer(1, 6))
            
        # Parse Bullets (e.g. * **Platform Telemetry**: ...)
        elif line.startswith("* ") or line.startswith("- "):
            text = line[2:]
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(text, bullet_style))
            story.append(Spacer(1, 4))
            
        # Parse Horizontal rules
        elif line == "---":
            story.append(Spacer(1, 15))
            
        # Normal body paragraph
        else:
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 8))
            
    return story


def build_pdf(md_path, pdf_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1E3A8A")  # Deep Blue
    neutral_dark = colors.HexColor("#1E293B")   # Charcoal
    
    styles.add(ParagraphStyle(
        name="AppTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=primary_color,
        alignment=0,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name="ModuleHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0F766E"), # Teal
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name="CustomBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=neutral_dark,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name="CustomBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=neutral_dark,
        leftIndent=20,
        firstLineIndent=-12,
        spaceAfter=5
    ))
    
    story = parse_markdown_to_pdf_story(md_path, styles)
    doc.build(story, canvasmaker=NumberedCanvas)


if __name__ == "__main__":
    md_file = "/home/crystal/.gemini/antigravity/brain/5f4b1d7e-c025-4056-a3ba-72fd3d6bf1eb/daytone_workflow.md"
    pdf_file = "/home/crystal/.gemini/antigravity/brain/5f4b1d7e-c025-4056-a3ba-72fd3d6bf1eb/daytone_workflow.pdf"
    
    build_pdf(md_file, pdf_file)
    print(f"Successfully generated PDF at: {pdf_file}")
