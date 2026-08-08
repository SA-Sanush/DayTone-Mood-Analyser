import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total page count and draw
    professional running headers and footers on all pages except the cover.
    """
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
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            
            primary_color = colors.HexColor("#0F766E")  # Teal Accent
            muted_color = colors.HexColor("#64748B")    # Slate Gray
            border_color = colors.HexColor("#E2E8F0")   # Light Gray border
            
            # --- RUNNING HEADER ---
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(primary_color)
            self.drawString(54, 750, "DAYTONE MOOD ANALYSER  |  ACADEMIC THESIS REPORT")
            
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(muted_color)
            self.drawRightString(558, 750, "Advanced Python Certification Submission")
            
            # Header Line
            self.setStrokeColor(border_color)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # --- RUNNING FOOTER ---
            self.setFont("Helvetica", 8)
            self.setFillColor(muted_color)
            self.drawString(54, 40, "Confidential  •  MCA Semester 3 Mini Project  •  S A Sanush")
            self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
            
            # Footer Line
            self.line(54, 50, 558, 50)
            
            self.restoreState()

def create_screenshot_placeholder(name, width=504, height=180):
    placeholder_style = ParagraphStyle(
        'PlaceholderText',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B")
    )
    text = f"<br/><br/><br/>[ SCREENSHOT PLACEHOLDER ]<br/>{name}<br/>(Insert User Interface Screen Here)"
    p = Paragraph(text, placeholder_style)
    
    t = Table([[p]], colWidths=[width], rowHeights=[height])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def build_pdf():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(base_dir, "DayTone_Project_Report.pdf")
    
    margin = 54
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0F766E")    # Teal Accent
    c_secondary = colors.HexColor("#1E293B")  # Deep Slate Dark
    c_dark = colors.HexColor("#1F2937")       # Charcoal Body Text
    c_muted = colors.HexColor("#4B5563")      # Soft Gray Text
    c_bg_light = colors.HexColor("#F8FAFC")   # Soft Slate background
    c_code_bg = colors.HexColor("#0F172A")    # Code block background
    c_code_text = colors.HexColor("#38BDF8")  # Code block text
    
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=c_secondary,
        spaceAfter=15
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=c_primary,
        spaceAfter=30
    )
    
    style_cover_meta_label = ParagraphStyle(
        'CoverMetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_secondary
    )
    
    style_cover_meta_val = ParagraphStyle(
        'CoverMetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_dark
    )
    
    style_h1 = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13.5,
        alignment=TA_LEFT,
        textColor=c_dark,
        spaceAfter=5
    )
    
    style_body_justify = ParagraphStyle(
        'BodyDarkJustify',
        parent=style_body,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    style_bullet_item = ParagraphStyle(
        'BulletItem',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )
    
    style_fig_caption = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=c_muted,
        spaceBefore=4,
        spaceAfter=8
    )
    
    style_table_header = ParagraphStyle(
        'TableHeaderText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
        textColor=colors.white
    )
    
    style_table_cell = ParagraphStyle(
        'TableCellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        alignment=TA_LEFT,
        textColor=c_dark
    )
    
    style_table_cell_bold = ParagraphStyle(
        'TableCellTextBold',
        parent=style_table_cell,
        fontName='Helvetica-Bold',
        textColor=c_primary
    )
    
    style_code_block = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=c_code_text,
        spaceAfter=6,
        leftIndent=10
    )

    story = []
    pages = {i: [] for i in range(1, 53)}
    
    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    pages[1].append(Spacer(1, 40))
    pages[1].append(Paragraph("TALENT ACQUISITION & MOOD TRACKING SYSTEM", style_cover_subtitle))
    pages[1].append(Spacer(1, 20))
    pages[1].append(HRFlowable(width="100%", thickness=4, color=c_primary, spaceBefore=0, spaceAfter=20))
    pages[1].append(Paragraph("DAYTONE MOOD ANALYSER", style_cover_title))
    pages[1].append(Paragraph("A comprehensive mental wellness tracking platform utilizing local NLP sentiment analysis and machine learning-based burnout classification.", style_cover_subtitle))
    pages[1].append(HRFlowable(width="40%", thickness=1, color=c_secondary, spaceBefore=0, spaceAfter=30, hAlign='CENTER'))
    pages[1].append(Spacer(1, 100))
    
    meta_data = [
        [Paragraph("Candidate Name:", style_cover_meta_label), Paragraph("S A SANUSH", style_cover_meta_val)],
        [Paragraph("Academic Project:", style_cover_meta_label), Paragraph("Semester 3 Mini Project", style_cover_meta_val)],
        [Paragraph("Course Program:", style_cover_meta_label), Paragraph("Master of Computer Applications (MCA)", style_cover_meta_val)],
        [Paragraph("Sponsoring Body:", style_cover_meta_label), Paragraph("ICT Academy of Kerala", style_cover_meta_val)],
        [Paragraph("Submission Date:", style_cover_meta_label), Paragraph("May / October 2026", style_cover_meta_val)],
        [Paragraph("Core Stack:", style_cover_meta_label), Paragraph("Python, Flask, SQLite, Scikit-learn, VADER NLP, Three.js WebGL", style_cover_meta_val)],
    ]
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    pages[1].append(meta_table)

    # =========================================================================
    # PAGE 2: LIST OF FIGURES
    # =========================================================================
    pages[2].append(Paragraph("LIST OF FIGURES", style_h1))
    pages[2].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    fig_data = [
        [Paragraph("Figure No.", style_table_header), Paragraph("Title / Description", style_table_header)],
        [Paragraph("<b>Figure 1</b>", style_table_cell), Paragraph("Home page of the DayTone Mood Analyser web application", style_table_cell)],
        [Paragraph("<b>Figure 2</b>", style_table_cell), Paragraph("Proposed system architecture of DayTone platform", style_table_cell)],
        [Paragraph("<b>Figure 3</b>", style_table_cell), Paragraph("Relational SQLite database schema diagram", style_table_cell)],
        [Paragraph("<b>Figure 4</b>", style_table_cell), Paragraph("User registration and secure login screen layout", style_table_cell)],
        [Paragraph("<b>Figure 5</b>", style_table_cell), Paragraph("Daily check-in and encrypted journal submission form", style_table_cell)],
        [Paragraph("<b>Figure 6</b>", style_table_cell), Paragraph("User dashboard showing mood trends and WebGL 3D orb", style_table_cell)],
        [Paragraph("<b>Figure 7</b>", style_table_cell), Paragraph("Administrative interface displaying user catalogs and audit logs", style_table_cell)],
        [Paragraph("<b>Figure 8</b>", style_table_cell), Paragraph("Criteria-wise wellness score breakdown and suggested tips", style_table_cell)],
        [Paragraph("<b>Figure 9</b>", style_table_cell), Paragraph("Model diagnostics, bias reports and Kolmogorov-Smirnov drift charts", style_table_cell)],
    ]
    fig_table = Table(fig_data, colWidths=[100, 404])
    fig_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    pages[2].append(fig_table)

    # =========================================================================
    # PAGE 3: TABLE OF CONTENTS
    # =========================================================================
    pages[3].append(Paragraph("TABLE OF CONTENTS", style_h1))
    pages[3].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    toc_data = [
        [Paragraph("Chapter", style_table_header), Paragraph("Description", style_table_header), Paragraph("Page No.", style_table_header)],
        [Paragraph("<b>1</b>", style_table_cell), Paragraph("Problem Definition (Overview & Problem Statement)", style_table_cell), Paragraph("6", style_table_cell)],
        [Paragraph("<b>2</b>", style_table_cell), Paragraph("Introduction (Background, Objectives & Scope)", style_table_cell), Paragraph("9", style_table_cell)],
        [Paragraph("<b>3</b>", style_table_cell), Paragraph("Literature Survey (Review of Techniques & Pipelines)", style_table_cell), Paragraph("12", style_table_cell)],
        [Paragraph("<b>4</b>", style_table_cell), Paragraph("System Analysis (Existing, Proposed, Requirements)", style_table_cell), Paragraph("15", style_table_cell)],
        [Paragraph("<b>5</b>", style_table_cell), Paragraph("System Design (Architecture, DB & Modules)", style_table_cell), Paragraph("19", style_table_cell)],
        [Paragraph("<b>6</b>", style_table_cell), Paragraph("Implementation (Tech Stack, Shaders, ML/NLP)", style_table_cell), Paragraph("24", style_table_cell)],
        [Paragraph("<b>7</b>", style_table_cell), Paragraph("Result & Discussion (Outputs, Drift & Diagnostics)", style_table_cell), Paragraph("36", style_table_cell)],
        [Paragraph("<b>8</b>", style_table_cell), Paragraph("Conclusion & Future Enhancements", style_table_cell), Paragraph("39", style_table_cell)],
        [Paragraph("<b>App A</b>", style_table_cell), Paragraph("Appendix A: Project File Structure", style_table_cell), Paragraph("40", style_table_cell)],
        [Paragraph("<b>App B</b>", style_table_cell), Paragraph("Appendix B: Important Routes", style_table_cell), Paragraph("41", style_table_cell)],
        [Paragraph("<b>App C</b>", style_table_cell), Paragraph("Appendix C: Important Functions", style_table_cell), Paragraph("42", style_table_cell)],
        [Paragraph("<b>App D</b>", style_table_cell), Paragraph("Appendix D: Requirements", style_table_cell), Paragraph("43", style_table_cell)],
        [Paragraph("<b>App E</b>", style_table_cell), Paragraph("Appendix E: Important Code Snippets", style_table_cell), Paragraph("44", style_table_cell)],
        [Paragraph("<b>Ref</b>", style_table_cell), Paragraph("References & Bibliography", style_table_cell), Paragraph("51", style_table_cell)],
    ]
    toc_table = Table(toc_data, colWidths=[60, 384, 60])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    pages[3].append(toc_table)

    # =========================================================================
    # PAGE 4: LIST OF ABBREVIATIONS
    # =========================================================================
    pages[4].append(Paragraph("LIST OF ABBREVIATIONS", style_h1))
    pages[4].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    abbr_data = [
        [Paragraph("Abbreviation", style_table_header), Paragraph("Expansion / Full Form", style_table_header)],
        [Paragraph("<b>AI</b>", style_table_cell_bold), Paragraph("Artificial Intelligence", style_table_cell)],
        [Paragraph("<b>NLP</b>", style_table_cell_bold), Paragraph("Natural Language Processing", style_table_cell)],
        [Paragraph("<b>ML</b>", style_table_cell_bold), Paragraph("Machine Learning", style_table_cell)],
        [Paragraph("<b>PWA</b>", style_table_cell_bold), Paragraph("Progressive Web Application", style_table_cell)],
        [Paragraph("<b>CSRF</b>", style_table_cell_bold), Paragraph("Cross-Site Request Forgery", style_table_cell)],
        [Paragraph("<b>AES</b>", style_table_cell_bold), Paragraph("Advanced Encryption Standard", style_table_cell)],
        [Paragraph("<b>SOC</b>", style_table_cell_bold), Paragraph("System and Organization Controls", style_table_cell)],
        [Paragraph("<b>GDPR</b>", style_table_cell_bold), Paragraph("General Data Protection Regulation", style_table_cell)],
        [Paragraph("<b>CSP</b>", style_table_cell_bold), Paragraph("Content Security Policy", style_table_cell)],
        [Paragraph("<b>XAI</b>", style_table_cell_bold), Paragraph("Explainable Artificial Intelligence", style_table_cell)],
    ]
    abbr_table = Table(abbr_data, colWidths=[100, 404])
    abbr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    pages[4].append(abbr_table)

    # -------------------------------------------------------------------------
    # PAGE 5: ABSTRACT
    # -------------------------------------------------------------------------
    pages[5].append(Paragraph("ABSTRACT", style_h1))
    pages[5].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[5].append(Paragraph(
        "The <b>DayTone Mood Analyser (DMA)</b> is a self-hosted, privacy-first, and GDPR-compliant web "
        "application developed using Python, Flask, SQLAlchemy, and Scikit-learn. The system acts as a secure "
        "personal logging tracker and analytics engine, enabling users to register their daily wellness "
        "indicators (mood score, sleep hours, stress level, activity completion, and social interaction metrics) "
        "alongside reflective journal entries. The objective of the platform is to leverage local Natural Language "
        "Processing (NLP) and Machine Learning (ML) techniques to evaluate mental fatigue, assess cumulative "
        "burnout risks, and output explainable wellness recommendations without compromising sensitive user data.",
        style_body_justify
    ))
    pages[5].append(Paragraph(
        "To protect data at rest, DayTone implements hybrid column-level symmetric encryption (AES-256 Fernet) "
        "for raw text reflection notes. Textual analyses are run locally using the NLTK VADER sentiment lexicon "
        "with an optional transformer-based DistilBERT pipeline fallback. Burnout risks are evaluated through a "
        "12-feature mathematical matrix processed by a Decision Tree or Random Forest classifier. Diagnostic utilities, "
        "including model bias audits and prediction drift monitors, are integrated directly into the administrative console. "
        "Additionally, the platform functions as a Progressive Web Application (PWA) supporting offline fallbacks, "
        "multi-tab synchronization, query caching, and WCAG 2.1 motion accessibility guidelines (Calm Mode).",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 6: CHAPTER 1 - OVERVIEW (Significance of Wellness Trackers)
    # -------------------------------------------------------------------------
    pages[6].append(Paragraph("1. PROBLEM DEFINITION", style_h1))
    pages[6].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[6].append(Paragraph("1.1 OVERVIEW", style_h2))
    pages[6].append(Paragraph(
        "In modern professional and academic settings, chronic stress, mental fatigue, and clinical burnout "
        "have become widespread. Under the pressure of corporate deliverables, university placement exams, "
        "and long working hours, individuals often experience progressive declines in physical and emotional "
        "well-being without clear warnings. Traditional healthcare systems operate reactively, treating "
        "clinical exhaustion only after severe symptoms manifest. Preventive systems—specifically self-tracking "
        "wellness platforms—provide a proactive solution, allowing users to log behavioral patterns and identify "
        "early signs of burnout before they escalate.",
        style_body_justify
    ))
    pages[6].append(Paragraph(
        "However, current wellness applications present structural drawbacks. Most commercial trackers require "
        "users to upload highly sensitive, personal journal logs to proprietary third-party clouds where data "
        "is processed by black-box algorithms. This practice raises privacy concerns and exposes user data to "
        "unauthorized leaks or advertising profiles. In high-performance developer environments and academic "
        "institutions, there is a clear need for a self-hosted, local-first alternative that processes data "
        "privately while maintaining the analytical depth of modern machine learning pipelines.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 7: CHAPTER 1 - OVERVIEW (Security & Offline Challenges)
    # -------------------------------------------------------------------------
    pages[7].append(Paragraph("1.1 OVERVIEW (CONTINUED)", style_h2))
    pages[7].append(Paragraph(
        "Beyond standard data security, mental wellness trackers must also address technical and operational "
        "challenges. Relational database backends must store journals securely, preventing unauthorized read access "
        "even if the database file is compromised. Furthermore, applications must be resilient to connectivity "
        "failures. Under high-latency network conditions, or when users travel, web-dependent platforms fail. "
        "This requires offline-first support using local client-side caches and service workers.",
        style_body_justify
    ))
    pages[7].append(Paragraph(
        "Additionally, algorithmic transparency (Explainable AI or XAI) is critical in mental health tracking. "
        "If a platform flags a user as having a 'High' risk of burnout, it must explain the specific factors "
        "driving that prediction (such as a drop in sleep hours or a spike in stress levels). Providing a single, "
        "unexplained risk level can cause user anxiety. DayTone addresses these requirements by building a secure, "
        "local-first, and explainable wellness tracking platform.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 8: CHAPTER 1 - PROBLEM STATEMENT (FIG 1)
    # -------------------------------------------------------------------------
    pages[8].append(Paragraph("1.2 PROBLEM STATEMENT", style_h2))
    pages[8].append(Paragraph(
        "The objective of this project is to design and implement a self-hosted, secure, and transparent wellness "
        "tracker that evaluates daily physical and mental metrics locally. The system must accept user inputs "
        "(mood, sleep, stress, activity, and social indicators), extract textual features from journal notes "
        "privately (using local sentiment libraries), and evaluate cumulative burnout risks (Low, Medium, High) "
        "via an explainable machine learning model. To comply with privacy standards (GDPR), the system must "
        "encrypt reflections at rest, provide account purge mechanisms (Right to be Forgotten), protect interfaces "
        "against brute-force requests, and operate offline as a Progressive Web App.",
        style_body_justify
    ))
    pages[8].append(Spacer(1, 10))
    pages[8].append(create_screenshot_placeholder("Figure 1: Home Page of DayTone Mood Analyser UI"))
    pages[8].append(Paragraph("Figure 1: Home page of the DayTone Mood Analyser", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 9: CHAPTER 2 - BACKGROUND (Evolution of Tracking)
    # -------------------------------------------------------------------------
    pages[9].append(Paragraph("2. INTRODUCTION", style_h1))
    pages[9].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[9].append(Paragraph("2.1 BACKGROUND OF THE PROJECT", style_h2))
    pages[9].append(Paragraph(
        "Mental health tracking systems have historically transitioned from physical paper journals to digital databases. "
        "However, raw logging is rarely sufficient to trigger user self-awareness. Incorporating data science and "
        "machine learning allows trackers to detect trends, predict risks, and make recommendations. "
        "The background of this project lies in creating a student-friendly, free-tier deployable system that "
        "implements security (AES-256), data compliance (GDPR), accessibility (WCAG), and AI modeling "
        "comparisons (Decision Tree vs. Random Forest). This approach provides a practical tool for academic and "
        "personal use.",
        style_body_justify
    ))
    pages[9].append(Paragraph(
        "Furthermore, by structuring this as a self-contained Python Flask project, we establish a template for "
        "local-first mental health software. The project highlights that advanced NLP and machine learning tasks "
        "do not require expensive cloud infrastructure. Lightweight model payloads (such as joblib-serialized scikit-learn "
        "classifiers and rule-based lexicons) can run directly on CPU-constrained servers, making secure AI analytics "
        "more accessible.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 10: CHAPTER 2 - OBJECTIVES
    # -------------------------------------------------------------------------
    pages[10].append(Paragraph("2.2 OBJECTIVES OF THE PROJECT", style_h2))
    pages[10].append(Paragraph(
        "The primary design, implementation, and deployment objectives of DayTone are:",
        style_body
    ))
    pages[10].append(Paragraph("• <b>Local NLP Processing</b>: Use VADER or DistilBERT models locally in Flask memory to compute journal sentiment score indexes without cloud network dependence.", style_bullet_item))
    pages[10].append(Paragraph("• <b>ML Risk Classification</b>: Implement a 12-feature scikit-learn classifier model to predict burnout risk levels, comparing Decision Tree and Random Forest algorithms.", style_bullet_item))
    pages[10].append(Paragraph("• <b>Data Confidentiality</b>: Secure database columns using cryptography Fernet structures (AES-256) to ensure sensitive notes are encrypted at rest.", style_bullet_item))
    pages[10].append(Paragraph("• <b>GDPR Compliance</b>: Establish data portability exports (CSV/PDF) and user purging cascades (Right to be Forgotten).", style_bullet_item))
    pages[10].append(Paragraph("• <b>PWA Implementations</b>: Precache core assets to allow offline use, sync multi-tab page states via BroadcastChannels, and support motion accessibility (Calm Mode).", style_bullet_item))

    # -------------------------------------------------------------------------
    # PAGE 11: CHAPTER 2 - SCOPE & METHODOLOGY
    # -------------------------------------------------------------------------
    pages[11].append(Paragraph("2.3 SCOPE OF THE PROJECT", style_h2))
    pages[11].append(Paragraph(
        "The project scope focuses on preliminary screening, sentiment analysis, and wellness recommendations. "
        "It does not serve as a clinical diagnostic tool, make medical decisions, or replace professional therapy. "
        "It is an educational and self-monitoring dashboard meant to identify mental fatigue trends.",
        style_body_justify
    ))
    pages[11].append(Paragraph("2.4 METHODOLOGY", style_h2))
    pages[11].append(Paragraph(
        "The software development methodology follows an iterative, component-driven approach. First, database schemas "
        "and SQLAlchemy models are defined. Second, user log routes, validation, and encryption decorators are implemented. "
        "Third, the local sentiment parser and ML inference functions are integrated into check-in forms. "
        "Fourth, the dashboard charts (Chart.js) and 3D WebGL orb (Three.js) are built. Finally, drift detection, "
        "bias auditing, and rate limit protections are implemented for production deployment.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 12: CHAPTER 3 - LITERATURE SURVEY (MIND TRACKERS)
    # -------------------------------------------------------------------------
    pages[12].append(Paragraph("3. LITERATURE SURVEY", style_h1))
    pages[12].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[12].append(Paragraph("3.1 REVIEW OF WELL-BEING TRACKING TECHNIQUES", style_h2))
    pages[12].append(Paragraph(
        "Early digital mood trackers recorded inputs in relational tables and presented simple line charts. "
        "These designs were limited because they relied solely on manual inputs and ignored the qualitative "
        "insights within text journals. Literature reviews show that text reflections contain emotional signals "
        "that may contradict simple quantitative scores. Modern trackers use hybrid architectures that combine "
        "quantitative check-ins with natural language processing of qualitative journals.",
        style_body_justify
    ))
    pages[12].append(Paragraph(
        "Additionally, early designs lacked structured database encryption at rest. If the backend SQL engine "
        "was compromised, sensitive personal records were exposed. This vulnerability highlights the importance of "
        "implementing transparent column-level encryption on text fields. Modern designs also emphasize "
        "local processing to minimize data transmission risks.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 13: CHAPTER 3 - LITERATURE SURVEY (NLP MECHANISMS)
    # -------------------------------------------------------------------------
    pages[13].append(Paragraph("3.2 REVIEW OF NLP IN SENTIMENT ANALYSIS", style_h2))
    pages[13].append(Paragraph(
        "Sentiment analysis generally utilizes rule-based lexicons (e.g. NLTK VADER) or deep learning transformer models "
        "(e.g. BERT variants). VADER is lightweight and computationally efficient on standard CPUs, making it suitable "
        "for self-hosted platforms. However, it lacks context-awareness and struggles with sarcasm. Transformer models, "
        "such as DistilBERT, evaluate semantic relationships and multi-word negations but require additional memory "
        "and execution overhead. A hybrid fallback model balances execution speed with contextual accuracy.",
        style_body_justify
    ))
    pages[13].append(Paragraph(
        "In addition, clinical research indicates that VADER may miss domain-specific distress terms. "
        "While BERT models provide better accuracy, their resource footprints make them difficult to run on "
        "free-tier servers. DayTone implements a fallback mechanism, prioritizing VADER for speed and low memory "
        "while supporting DistilBERT when hardware resources are available.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 14: CHAPTER 3 - LITERATURE SURVEY (ML CLASSIFIERS)
    # -------------------------------------------------------------------------
    pages[14].append(Paragraph("3.3 REVIEW OF MACHINE LEARNING IN BURNOUT CLASSIFICATION", style_h2))
    pages[14].append(Paragraph(
        "Burnout and fatigue classification research highlights the importance of historical context. Evaluating a "
        "single log entry lacks temporal depth. Modern classifiers (such as Decision Trees or Random Forests) construct "
        "features that capture averages, standard deviations, and consecutive indicators over a rolling time window "
        "(e.g. 7 days). This allows models to identify progressive changes in sleep, stress, and mood, leading to "
        "higher classification accuracy.",
        style_body_justify
    ))
    pages[14].append(Paragraph(
        "Additionally, studies show that simple Decision Trees are prone to overfitting on synthetic training data. "
        "Random Forest classifiers mitigate this by building ensembles of decision trees, which reduces variance "
        "and improves generalization. To maintain transparency, models must be combined with explainable AI (XAI) "
        "features that display the specific drivers behind predictions.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 15: CHAPTER 4 - SYSTEM ANALYSIS (EXISTING)
    # -------------------------------------------------------------------------
    pages[15].append(Paragraph("4. SYSTEM ANALYSIS", style_h1))
    pages[15].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[15].append(Paragraph("4.1 EXISTING SYSTEM", style_h2))
    pages[15].append(Paragraph(
        "The existing system in many academic institutions and high-performance environments is either non-existent or "
        "reliant on manual Excel logging. Where web-based trackers are used, they typically upload raw data directly "
        "to remote cloud services. These commercial cloud applications do not process data locally. This results in "
        "high network dependence and exposes user data to cloud breaches or tracking by advertisers.",
        style_body_justify
    ))
    pages[15].append(Paragraph(
        "Counselors and managers who review these logs must manually check entries, which is slow, inconsistent, and "
        "subjective. There is no automated, transparent system to identify trends, check keywords, or flag high-risk "
        "users. This lack of automation delay feedback and limits the effectiveness of preventive mental health support.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 16: CHAPTER 4 - SYSTEM ANALYSIS (LIMITATIONS)
    # -------------------------------------------------------------------------
    pages[16].append(Paragraph("4.2 LIMITATIONS OF EXISTING SYSTEM", style_h2))
    pages[16].append(Paragraph(
        "Key limitations identified in cloud-dependent mood trackers include:",
        style_body
    ))
    pages[16].append(Paragraph("• <b>Lack of Privacy</b>: Personal journals are processed by external third-party models, violating user confidentiality.", style_bullet_item))
    pages[16].append(Paragraph("• <b>Vulnerable Storage</b>: Databases store notes in plaintext, leaving them open to exposure during data breaches.", style_bullet_item))
    pages[16].append(Paragraph("• <b>Poor Accessibility</b>: Missing features like motion controls for users with visual or motion sensitivities.", style_bullet_item))
    pages[16].append(Paragraph("• <b>No Trend Assessment</b>: Systems evaluate single check-ins in isolation, failing to assess historical trends.", style_bullet_item))
    pages[16].append(Paragraph("• <b>High Overhead Costs</b>: Operating complex server stacks incurs continuous subscription fees.", style_bullet_item))

    # -------------------------------------------------------------------------
    # PAGE 17: CHAPTER 4 - SYSTEM ANALYSIS (PROPOSED)
    # -------------------------------------------------------------------------
    pages[17].append(Paragraph("4.3 PROPOSED SYSTEM", style_h2))
    pages[17].append(Paragraph(
        "The proposed system, DayTone, addresses these issues through local execution, hybrid encryption, "
        "and offline capabilities. By utilizing local NLP sentiment scoring (VADER) and a local ML classifier, "
        "it evaluates user burnout risk locally. All journal entries are encrypted using AES-256 at rest, "
        "protecting user privacy in the SQLite database. Additional safety reveals shield high-risk warnings "
        "to manage user anxiety, and a Calm Mode setting accommodates users with motion sensitivities.",
        style_body_justify
    ))
    pages[17].append(Paragraph(
        "For administrators and counselors, DayTone provides an admin dashboard. Admins can review platform-wide "
        "metrics, track model performance, verify accuracy, and check for bias or drift. This design provides "
        "an explainable and repeatable self-monitoring dashboard.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 18: CHAPTER 4 - SYSTEM ANALYSIS (FEASIBILITY)
    # -------------------------------------------------------------------------
    pages[18].append(Paragraph("4.4 FEASIBILITY STUDY", style_h2))
    pages[18].append(Paragraph(
        "• <b>Technical Feasibility</b>: Strong. Stable open-source Python libraries (scikit-learn, VADER) "
        "ensure core logic is highly responsive and runs locally on standard CPU hosts.", style_bullet_item
    ))
    pages[18].append(Paragraph(
        "• <b>Operational Feasibility</b>: High. Browser-based client requires no local setup, providing "
        "intuitive dark-themed inputs and charts for students.", style_bullet_item
    ))
    pages[18].append(Paragraph(
        "• <b>Economic Feasibility</b>: Excellent. Open-source stacks eliminate licensing fees, allowing "
        "easy deployment on student-friendly free-tier hosting.", style_bullet_item
    ))

    # -------------------------------------------------------------------------
    # PAGE 19: CHAPTER 4 - SYSTEM ANALYSIS (REQUIREMENTS)
    # -------------------------------------------------------------------------
    pages[19].append(Paragraph("4.5 FUNCTIONAL REQUIREMENTS", style_h2))
    pages[19].append(Paragraph(
        "The platform must support user authentication, daily log entry forms, local sentiment scoring, "
        "burnout predictions, goal progression, PDF/CSV downloads, and administrative bias/drift diagnostics.",
        style_body_justify
    ))
    pages[19].append(Paragraph("4.6 NON-FUNCTIONAL REQUIREMENTS", style_h2))
    pages[19].append(Paragraph(
        "Must achieve low response latencies (<1s), strict security (AES-256 column encryption, Talisman CSP headers), "
        "robust brute-force protection (Redis-backed rate limiting), and offline reliability (PWA cached assets).",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 20: CHAPTER 5 - SYSTEM DESIGN (ARCHITECTURE & FIG 2)
    # -------------------------------------------------------------------------
    pages[20].append(Paragraph("5. SYSTEM DESIGN", style_h1))
    pages[20].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[20].append(Paragraph("5.1 SYSTEM ARCHITECTURE", style_h2))
    pages[20].append(Paragraph(
        "The platform architecture is designed around a three-tier model, separating the browser front-end, "
        "Flask web controllers, and SQLite/PostgreSQL/Redis databases.",
        style_body_justify
    ))
    pages[20].append(Spacer(1, 10))
    pages[20].append(create_screenshot_placeholder("Figure 2: Proposed System Architecture of DayTone"))
    pages[20].append(Paragraph("Figure 2: Proposed system architecture of the DayTone Mood Analyser", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 21: CHAPTER 5 - DFD DESCRIPTION
    # -------------------------------------------------------------------------
    pages[21].append(Paragraph("5.2 DATA FLOW DIAGRAM DESCRIPTION", style_h2))
    pages[21].append(Paragraph(
        "The data flow in DayTone follows a defined, secure path: "
        "The user browser submits check-in metrics and journal text over HTTPS. "
        "The Flask validation layer sanitizes the inputs and computes the VADER sentiment score index locally. "
        "The system then builds the 12-feature matrix (incorporating rolling averages from SQLite history) "
        "and runs the machine learning predictor. The journal note is encrypted via AES-256 before the complete "
        "MoodLog record is written to the SQLite database, returning rendered JSON/HTML and updating the dashboard.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 22: CHAPTER 5 - DATABASE DESIGN (FIG 3)
    # -------------------------------------------------------------------------
    pages[22].append(Paragraph("5.3 DATABASE DESIGN", style_h2))
    pages[22].append(Paragraph(
        "The SQLite schema contains tables for users, profiles, logs, burnout history, suggestions, and audit logs. "
        "Foreign key constraints enforce referential integrity and support cascading purges.",
        style_body_justify
    ))
    pages[22].append(Spacer(1, 10))
    pages[22].append(create_screenshot_placeholder("Figure 3: SQLite Database Schema used for DayTone"))
    pages[22].append(Paragraph("Figure 3: Relational SQLite database schema diagram", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 23: CHAPTER 5 - UI & MODULE DESIGN
    # -------------------------------------------------------------------------
    pages[23].append(Paragraph("5.4 USER INTERFACE DESIGN", style_h2))
    pages[23].append(Paragraph(
        "The interface design prioritizes accessibility, using a clean dark theme, clear tab-focus rings, "
        "and motion control toggles. It uses custom CSS grids and standard Bootstrap templates.",
        style_body_justify
    ))
    pages[23].append(Paragraph("5.5 SECURITY DESIGN", style_h2))
    pages[23].append(Paragraph(
        "Security protections include password hashing, Talisman CSP headers, Werkzeug hashing, and Redis-backed "
        "rate limiting to secure forms and prevent brute-force attacks.",
        style_body_justify
    ))
    pages[23].append(Paragraph("5.6 MODULE DESIGN", style_h2))
    pages[23].append(Paragraph(
        "The app is divided into distinct, logically separated blueprints: Auth Blueprint, Mood Blueprint, "
        "Admin Blueprint, ML Pipeline module, and NLP Sentiment analyzer.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 24: CHAPTER 6 - IMPLEMENTATION (TECH STACK)
    # -------------------------------------------------------------------------
    pages[24].append(Paragraph("6. IMPLEMENTATION", style_h1))
    pages[24].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[24].append(Paragraph("6.1 TECHNOLOGY STACK AND PROJECT STRUCTURE", style_h2))
    pages[24].append(Paragraph(
        "The technology stack is carefully selected to support local data processing and hosting on student-friendly setups:",
        style_body
    ))
    tech_data_1 = [
        [Paragraph("Technology", style_table_header), Paragraph("Description", style_table_header), Paragraph("Role inside DayTone", style_table_header)],
        [Paragraph("<b>Python</b>", style_table_cell_bold), Paragraph("Programming Language", style_table_cell), Paragraph("Backend controllers, data modeling, ML, and NLP logic.", style_table_cell)],
        [Paragraph("<b>Flask</b>", style_table_cell_bold), Paragraph("Web Framework", style_table_cell), Paragraph("Routing, template rendering, and application factory creation.", style_table_cell)],
        [Paragraph("<b>PostgreSQL</b>", style_table_cell_bold), Paragraph("Relational Database", style_table_cell), Paragraph("Persistent storage in production environments.", style_table_cell)],
        [Paragraph("<b>SQLite</b>", style_table_cell_bold), Paragraph("Relational Database", style_table_cell), Paragraph("Local development database.", style_table_cell)],
    ]
    tech_table_1 = Table(tech_data_1, colWidths=[100, 154, 250])
    tech_table_1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    pages[24].append(tech_table_1)

    # -------------------------------------------------------------------------
    # PAGE 25: CHAPTER 6 - TECH STACK (CONTINUED)
    # -------------------------------------------------------------------------
    pages[25].append(Paragraph("6.1 TECHNOLOGY STACK AND PROJECT STRUCTURE (CONTINUED)", style_h2))
    tech_data_2 = [
        [Paragraph("Technology", style_table_header), Paragraph("Description", style_table_header), Paragraph("Role inside DayTone", style_table_header)],
        [Paragraph("<b>Redis</b>", style_table_cell_bold), Paragraph("In-memory Cache Store", style_table_cell), Paragraph("Limiter registry, query caching, and token storage.", style_table_cell)],
        [Paragraph("<b>scikit-learn</b>", style_table_cell_bold), Paragraph("ML Framework", style_table_cell), Paragraph("Decision Tree / Random Forest models, feature calculation, and pipeline retraining.", style_table_cell)],
        [Paragraph("<b>NLTK VADER</b>", style_table_cell_bold), Paragraph("NLP Lexicon Library", style_table_cell), Paragraph("Local sentiment parsing of journal text.", style_table_cell)],
        [Paragraph("<b>Three.js WebGL</b>", style_table_cell_bold), Paragraph("Graphics Library", style_table_cell), Paragraph("Renders the interactive 3D orb using custom shaders.", style_table_cell)],
        [Paragraph("<b>Chart.js</b>", style_table_cell_bold), Paragraph("Visualizations Library", style_table_cell), Paragraph("Renders the analytics dashboards and goal milestones.", style_table_cell)],
    ]
    tech_table_2 = Table(tech_data_2, colWidths=[100, 154, 250])
    tech_table_2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    pages[25].append(tech_table_2)

    # -------------------------------------------------------------------------
    # PAGE 26: CHAPTER 6 - AUTHENTICATION MODULE (FIG 4)
    # -------------------------------------------------------------------------
    pages[26].append(Paragraph("6.2 USER REGISTRATION AND LOGIN", style_h2))
    pages[26].append(Paragraph(
        "User accounts are protected through password hashing (Werkzeug scrypt) and CSRF protection. "
        "Admin registrations use secure invite tokens generated in the database.",
        style_body_justify
    ))
    pages[26].append(Spacer(1, 10))
    pages[26].append(create_screenshot_placeholder("Figure 4: User Registration and Login Screens"))
    pages[26].append(Paragraph("Figure 4: User registration and secure login screen layout", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 27: CHAPTER 6 - DAILY LOGGING MODULE (FIG 5)
    # -------------------------------------------------------------------------
    pages[27].append(Paragraph("6.3 DAILY LOGGING AND JOURNAL INTAKE", style_h2))
    pages[27].append(Paragraph(
        "Users log their daily metrics (mood, sleep, stress, activity, and social indicators) alongside journal notes, "
        "which are encrypted using AES-256 before being written to the database.",
        style_body_justify
    ))
    pages[27].append(Spacer(1, 10))
    pages[27].append(create_screenshot_placeholder("Figure 5: Daily Check-in Form and Journal Inputs"))
    pages[27].append(Paragraph("Figure 5: Daily check-in and encrypted journal submission form", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 28: CHAPTER 6 - WEBGL SHADER ORB (FIG 6)
    # -------------------------------------------------------------------------
    pages[28].append(Paragraph("6.4 WEBGL SHADER ORB RENDERING", style_h2))
    pages[28].append(Paragraph(
        "The dashboard renders an interactive 3D orb using Three.js and custom vertex/fragment shaders. "
        "The orb deforms and changes color dynamically based on user metrics.",
        style_body_justify
    ))
    pages[28].append(Spacer(1, 10))
    pages[28].append(create_screenshot_placeholder("Figure 6: Dashboard showing WebGL 3D Orb"))
    pages[28].append(Paragraph("Figure 6: User dashboard showing mood trends and WebGL 3D orb", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 29: CHAPTER 6 - NLP PIPELINE
    # -------------------------------------------------------------------------
    pages[29].append(Paragraph("6.5 LOCAL SENTIMENT PARSING PIPELINE", style_h2))
    pages[29].append(Paragraph(
        "To protect user privacy, DayTone processes sensitive journal text locally. "
        "By default, the platform initializes the NLTK VADER sentiment intensity analyzer. "
        "VADER evaluates the emotional valence of word tokens, outputting compound sentiment scores in `[-1.0, 1.0]`. "
        "If the server has sufficient hardware resources and the `transformers` library is detected, "
        "the application loads a lightweight DistilBERT pipeline. "
        "If both NLP pipelines fail (e.g. during initialization errors), the system falls back to a safe "
        "neutral score of 0.0, maintaining application availability.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 30: CHAPTER 6 - ML INFERENCE
    # -------------------------------------------------------------------------
    pages[30].append(Paragraph("6.6 MACHINE LEARNING BURNOUT MODEL INFERENCE", style_h2))
    pages[30].append(Paragraph(
        "The machine learning system predicts burnout risk (Low, Medium, High) using a 12-feature matrix. "
        "This matrix captures both daily inputs and rolling 7-day averages. "
        "The predictor loads the scikit-learn Random Forest model from `model.pkl`. "
        "To prevent server downtime if the model file is missing or scikit-learn fails, "
        "the inference route falls back to a deterministic rule-based scoring engine.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 31: CHAPTER 6 - SUGGESTIONS & PDF REPORTS
    # -------------------------------------------------------------------------
    pages[31].append(Paragraph("6.7 WELLNESS RECOMMENDATION TIPS GENERATOR", style_h2))
    pages[31].append(Paragraph(
        "A rule-based wellness engine checks daily metrics and displays customized suggestions. "
        "If a High burnout risk is predicted, emergency helpline contacts are displayed on the dashboard.",
        style_body_justify
    ))
    pages[31].append(Paragraph("6.8 REPORT GENERATION AND EXPORT", style_h2))
    pages[31].append(Paragraph(
        "Users can export their complete logging history as a CSV file or download a formatted PDF report "
        "generated using ReportLab. The PDF includes user information, daily logs, and trend charts.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 32: CHAPTER 6 - ADMIN CONSOLE (FIG 7)
    # -------------------------------------------------------------------------
    pages[32].append(Paragraph("6.9 ADMINISTRATIVE CONSOLE", style_h2))
    pages[32].append(Paragraph(
        "Admins can manage the recommendation catalog, audit logs, and user accounts. "
        "All administrative actions are logged to ensure compliance and accountability.",
        style_body_justify
    ))
    pages[32].append(Spacer(1, 10))
    pages[32].append(create_screenshot_placeholder("Figure 7: Administrative Panel Screen"))
    pages[32].append(Paragraph("Figure 7: Administrative interface displaying user catalogs and audit logs", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 33: CHAPTER 6 - SCORE BREAKDOWN (FIG 8)
    # -------------------------------------------------------------------------
    pages[33].append(Paragraph("6.10 WELLNESS SCORE BREAKDOWN", style_h2))
    pages[33].append(Paragraph(
        "The platform breaks down the user's score across different criteria (sleep, mood, stress) "
        "and suggests specific tips to improve the score.",
        style_body_justify
    ))
    pages[33].append(Spacer(1, 10))
    pages[33].append(create_screenshot_placeholder("Figure 8: Criteria-wise Score Breakdown"))
    pages[33].append(Paragraph("Figure 8: Criteria-wise wellness score breakdown and suggested tips", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 34: CHAPTER 6 - DIAGNOSTICS (FIG 9)
    # -------------------------------------------------------------------------
    pages[34].append(Paragraph("6.11 MODEL DIAGNOSTICS & RETRAINING", style_h2))
    pages[34].append(Paragraph(
        "The administrative panel displays diagnostic charts tracking model performance. "
        "It includes bias audits and drift monitors to detect changes in accuracy.",
        style_body_justify
    ))
    pages[34].append(Spacer(1, 10))
    pages[34].append(create_screenshot_placeholder("Figure 9: MLOps Diagnostics Reports"))
    pages[34].append(Paragraph("Figure 9: Model diagnostics, bias reports and Kolmogorov-Smirnov drift charts", style_fig_caption))

    # -------------------------------------------------------------------------
    # PAGE 35: CHAPTER 6 - TESTING STRATEGY
    # -------------------------------------------------------------------------
    pages[35].append(Paragraph("6.12 TESTING STRATEGY AND TEST CASE SUMMARY", style_h2))
    pages[35].append(Paragraph(
        "Testing is performed using Pytest. Automated tests cover user registration, login, "
        "check-in, database encryption, model drift calculations, and admin catalog modifications.",
        style_body_justify
    ))
    test_data = [
        [Paragraph("Test Case ID", style_table_header), Paragraph("Component Verified", style_table_header), Paragraph("Expected Result", style_table_header)],
        [Paragraph("TC_01", style_table_cell), Paragraph("User Registration & Auth", style_table_cell), Paragraph("Creates account, hashes passwords, rejects duplicates.", style_table_cell)],
        [Paragraph("TC_02", style_table_cell), Paragraph("Daily Log Submission", style_table_cell), Paragraph("Saves daily metrics, validates input ranges.", style_table_cell)],
        [Paragraph("TC_03", style_table_cell), Paragraph("Symmetric Note Encryption", style_table_cell), Paragraph("Decrypts column value in memory, stores ciphertext.", style_table_cell)],
        [Paragraph("TC_04", style_table_cell), Paragraph("Local NLP Sentiment Parsing", style_table_cell), Paragraph("Outputs sentiment score in standard range [-1, 1].", style_table_cell)],
        [Paragraph("TC_05", style_table_cell), Paragraph("ML Burnout Classification", style_table_cell), Paragraph("Outputs Low/Medium/High, runs explainable AI drivers.", style_table_cell)],
        [Paragraph("TC_06", style_table_cell), Paragraph("Model Drift Calculations", style_table_cell), Paragraph("Computes KS-test, raises warning if drift > 0.05.", style_table_cell)],
    ]
    test_table = Table(test_data, colWidths=[90, 164, 250])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    pages[35].append(test_table)

    # -------------------------------------------------------------------------
    # PAGE 36: CHAPTER 7 - RESULT (OUTPUTS)
    # -------------------------------------------------------------------------
    pages[36].append(Paragraph("7. RESULT & DISCUSSION", style_h1))
    pages[36].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[36].append(Paragraph("7.1 SAMPLE OUTPUT DESCRIPTION", style_h2))
    pages[36].append(Paragraph(
        "The completed system successfully provides a browser-based wellness logging and predictive analysis workflow. "
        "Users can log daily metrics, review mood/sleep trends, check their burnout risk level, and view personalized "
        "wellness suggestions. High-risk predictions trigger crisis resources, which are hidden behind an opt-in "
        "reveal shield to manage user anxiety. The administrative panel displays diagnostic charts tracking model "
        "performance, bias reports, and Kolmogorov-Smirnov drift charts.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 37: CHAPTER 7 - DISCUSSION (PERFORMANCE & ADVANTAGES)
    # -------------------------------------------------------------------------
    pages[37].append(Paragraph("7.2 PERFORMANCE OBSERVATION", style_h2))
    pages[37].append(Paragraph(
        "The system runs efficiently on standard hosts. Local sentiment scoring (VADER) and machine learning inference "
        "complete in under 100ms. If transformers are enabled, response latency increases slightly but remains "
        "under 1 second.",
        style_body_justify
    ))
    pages[37].append(Paragraph("7.3 ADVANTAGES OF THE SYSTEM", style_h2))
    pages[37].append(Paragraph(
        "DayTone provides a private, secure, and transparent mental wellness tracker. "
        "By implementing local NLP/ML engines, AES-256 column encryption, and PWA capabilities, the platform provides "
        "actionable wellness insights while keeping data secure in local memory.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 38: CHAPTER 7 - DISCUSSION (LIMITATIONS & FUTURE ENHANCEMENTS)
    # -------------------------------------------------------------------------
    pages[38].append(Paragraph("7.4 LIMITATIONS", style_h2))
    pages[38].append(Paragraph(
        "Key limitations include: VADER sentiment scoring is rule-based and lacks semantic understanding, "
        "and the scikit-learn classifier requires clean user logs to maintain prediction accuracy.",
        style_body_justify
    ))
    pages[38].append(Paragraph("7.5 FUTURE ENHANCEMENTS", style_h2))
    pages[38].append(Paragraph(
        "Future enhancements could include implementing semantic similarity using transformer-based embeddings, "
        "providing localized recommendations based on specific user profiles, and expanding multi-tenant organization features.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 39: CHAPTER 8 - CONCLUSION
    # -------------------------------------------------------------------------
    pages[39].append(Paragraph("8. CONCLUSION", style_h1))
    pages[39].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[39].append(Paragraph("8.1 SUMMARY OF WORK COMPLETED", style_h2))
    pages[39].append(Paragraph(
        "The DayTone Mood Analyser meets its goals of building a private, secure, and transparent mental wellness tracker. "
        "By implementing local NLP/ML engines, AES-256 column encryption, and PWA capabilities, the platform provides "
        "actionable wellness insights while keeping data secure in local memory.",
        style_body_justify
    ))
    pages[39].append(Paragraph("8.2 LEARNING OUTCOMES", style_h2))
    pages[39].append(Paragraph(
        "Key learning outcomes include implementing custom SQLAlchemy decorators, comparisons between Decision Tree "
        "and Random Forest classifiers, Three.js vertex shader programming, and GDPR-compliant cascading deletes.",
        style_body_justify
    ))

    # -------------------------------------------------------------------------
    # PAGE 40: APPENDIX A
    # -------------------------------------------------------------------------
    pages[40].append(Paragraph("APPENDIX A: PROJECT FILE STRUCTURE", style_h1))
    pages[40].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[40].append(Paragraph(
        "Below is the listing of the DayTone codebase directory structure:",
        style_body
    ))
    struct_code = (
        "DayTone/\n"
        "├── app/                     # Flask Application Package\n"
        "│   ├── admin/               # Administrative operations (auditing, user list)\n"
        "│   ├── auth/                # Sign-in/signup & GDPR purge views\n"
        "│   ├── mood/                # Check-in forms, dashboard & exports\n"
        "│   ├── ml/                  # ML model, training, and predictor\n"
        "│   ├── nlp/                 # Sentiment parsing (VADER / DistilBERT)\n"
        "│   ├── utils/               # PDF reports, SOC-2 logs, & recommendations\n"
        "│   ├── templates/           # Jinja2 layout templates\n"
        "│   ├── static/              # CSS/JS, WebGL orb, manifest, and service worker\n"
        "│   ├── models.py            # Database tables & Encryption properties\n"
        "│   └── __init__.py          # App factory initialization\n"
        "├── docs/                    # Operations guides & runbooks\n"
        "├── migrations/              # Alembic database migration files\n"
        "├── scripts/                 # Diagnostics (bias audit, drift check, CSS minifier)\n"
        "├── tests/                   # Pytest automation suite\n"
        "├── Dockerfile               # Production container definition\n"
        "└── requirements.txt         # Package dependencies"
    )
    pages[40].append(Table([[Paragraph(struct_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 8),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 41: APPENDIX B
    # -------------------------------------------------------------------------
    pages[41].append(Paragraph("APPENDIX B: IMPORTANT ROUTES", style_h1))
    pages[41].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[41].append(Paragraph(
        "Below are the primary Flask routes mapped across blueprints:",
        style_body
    ))
    routes_data = [
        [Paragraph("HTTP Route", style_table_header), Paragraph("Blueprint", style_table_header), Paragraph("Purpose / Description", style_table_header)],
        [Paragraph("<code>/</code>", style_table_cell), Paragraph("auth_bp", style_table_cell), Paragraph("Root URL. Serves the landing page or redirects to dashboard.", style_table_cell)],
        [Paragraph("<code>/login</code>", style_table_cell), Paragraph("auth_bp", style_table_cell), Paragraph("Authenticates user sessions, redirects to dashboard.", style_table_cell)],
        [Paragraph("<code>/register</code>", style_table_cell), Paragraph("auth_bp", style_table_cell), Paragraph("Creates user account, initializes profile fields.", style_table_cell)],
        [Paragraph("<code>/dashboard</code>", style_table_cell), Paragraph("mood_bp", style_table_cell), Paragraph("Displays mood history, goal progress, and 3D orb UI.", style_table_cell)],
        [Paragraph("<code>/log</code>", style_table_cell), Paragraph("mood_bp", style_table_cell), Paragraph("Accepts daily check-in forms and processes journals.", style_table_cell)],
        [Paragraph("<code>/export/pdf</code>", style_table_cell), Paragraph("mood_bp", style_table_cell), Paragraph("Generates and downloads ReportLab PDF reports.", style_table_cell)],
        [Paragraph("<code>/admin/users</code>", style_table_cell), Paragraph("admin_bp", style_table_cell), Paragraph("Admin user dashboard and profile control views.", style_table_cell)],
    ]
    routes_table = Table(routes_data, colWidths=[110, 80, 314])
    routes_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    pages[41].append(routes_table)

    # -------------------------------------------------------------------------
    # PAGE 42: APPENDIX C
    # -------------------------------------------------------------------------
    pages[42].append(Paragraph("APPENDIX C: IMPORTANT FUNCTIONS", style_h1))
    pages[42].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[42].append(Paragraph(
        "Below are key backend function declarations and descriptions:",
        style_body
    ))
    func_data = [
        [Paragraph("Function name", style_table_header), Paragraph("Module location", style_table_header), Paragraph("Objective", style_table_header)],
        [Paragraph("<code>create_app()</code>", style_table_cell), Paragraph("app/__init__.py", style_table_cell), Paragraph("Application factory method initializing extensions.", style_table_cell)],
        [Paragraph("<code>encrypt_text()</code>", style_table_cell), Paragraph("app/models.py", style_table_cell), Paragraph("Encrypts text using Fernet AES-256 algorithm.", style_table_cell)],
        [Paragraph("<code>decrypt_text()</code>", style_table_cell), Paragraph("app/models.py", style_table_cell), Paragraph("Decrypts Fernet encrypted strings in memory.", style_table_cell)],
        [Paragraph("<code>get_sentiment_score()</code>", style_table_cell), Paragraph("app/nlp/sentiment.py", style_table_cell), Paragraph("Evaluates sentiment polarity using VADER / DistilBERT.", style_table_cell)],
        [Paragraph("<code>predict_burnout()</code>", style_table_cell), Paragraph("app/ml/predictor.py", style_table_cell), Paragraph("Evaluates burnout risk utilizing Random Forest.", style_table_cell)],
        [Paragraph("<code>generate_pdf_report()</code>", style_table_cell), Paragraph("app/utils/pdf_report.py", style_table_cell), Paragraph("Compiles PDF wellness report exports.", style_table_cell)],
    ]
    func_table = Table(func_data, colWidths=[150, 114, 240])
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    pages[42].append(func_table)

    # -------------------------------------------------------------------------
    # PAGE 43: APPENDIX D
    # -------------------------------------------------------------------------
    pages[43].append(Paragraph("APPENDIX D: REQUIREMENTS", style_h1))
    pages[43].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[43].append(Paragraph(
        "Below are the contents of the requirements.txt configuration file:",
        style_body
    ))
    reqs_code = (
        "Flask>=3.0.0\n"
        "Flask-SQLAlchemy>=3.1.0\n"
        "Flask-Login>=0.6.3\n"
        "Flask-WTF>=1.2.1\n"
        "Flask-Talisman>=1.1.0\n"
        "Flask-Limiter>=3.5.0\n"
        "Flask-Caching>=2.1.0\n"
        "cryptography>=41.0.0\n"
        "scikit-learn>=1.3.0\n"
        "joblib>=1.3.0\n"
        "pandas>=2.0.0\n"
        "numpy>=1.24.0\n"
        "nltk>=3.8.0\n"
        "reportlab>=4.0.0\n"
        "python-dotenv>=1.0.0\n"
        "python-json-logger>=2.0.7\n"
        "gunicorn>=21.2.0"
    )
    pages[43].append(Table([[Paragraph(reqs_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 10),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 44: APPENDIX E - CODE SNIPPET 1 (MODELS)
    # -------------------------------------------------------------------------
    pages[44].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS", style_h1))
    pages[44].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[44].append(Paragraph("A. SQLAlchemy Models & Column mapping definitions in models.py", style_h2))
    snippet_1 = (
        "class User(UserMixin, db.Model):\n"
        "    id = db.Column(db.Integer, primary_key=True)\n"
        "    name = db.Column(db.String(100), nullable=False)\n"
        "    email = db.Column(db.String(120), unique=True, nullable=False, index=True)\n"
        "    password_hash = db.Column(db.String(256), nullable=False)\n"
        "    role = db.Column(db.String(20), nullable=False, default='user')\n"
        "    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)\n"
        "    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='SET NULL'))\n"
        "    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)\n\n"
        "class UserProfile(db.Model):\n"
        "    id = db.Column(db.Integer, primary_key=True)\n"
        "    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)\n"
        "    preferred_activity = db.Column(db.String(50), nullable=False, default='Walk')\n"
        "    calm_mode = db.Column(db.Boolean, default=False, nullable=False)\n"
        "    predict_burnout = db.Column(db.Boolean, default=True, nullable=False)"
    )
    pages[44].append(Table([[Paragraph(snippet_1.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 8),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 45: APPENDIX E - CODE SNIPPET 2 (ENCRYPTION)
    # -------------------------------------------------------------------------
    pages[45].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS (CONTINUED)", style_h1))
    pages[45].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[45].append(Paragraph("B. Column-Level AES-256 Symmetric Encryption in models.py", style_h2))
    snippet_2 = (
        "def encrypt_text(value: str | None) -> str | None:\n"
        "    if not value or _fernet is None:\n"
        "        return value\n"
        "    try:\n"
        "        return _fernet.encrypt(value.encode('utf-8')).decode('ascii')\n"
        "    except Exception:\n"
        "        return value\n\n"
        "def decrypt_text(value: str | None) -> str | None:\n"
        "    if not value or _fernet is None:\n"
        "        return value\n"
        "    try:\n"
        "        return _fernet.decrypt(value.encode('ascii')).decode('utf-8')\n"
        "    except Exception:\n"
        "        return value"
    )
    pages[45].append(Table([[Paragraph(snippet_2.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 8),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 46: APPENDIX E - CODE SNIPPET 3 (PREDICTOR)
    # -------------------------------------------------------------------------
    pages[46].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS (CONTINUED)", style_h1))
    pages[46].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[46].append(Paragraph("C. Burnout Predictor & Rule Fallback in predictor.py", style_h2))
    snippet_3 = (
        "def predict_burnout(features: dict[str, float | int]) -> dict[str, str | float]:\n"
        "    try:\n"
        "        payload = _model_payload()\n"
        "    except Exception as exc:\n"
        "        payload = None\n\n"
        "    if payload is None:\n"
        "        prediction, confidence = _rule_prediction(features)\n"
        "        return {\n"
        "            \"prediction\": prediction,\n"
        "            \"confidence\": confidence,\n"
        "            \"algorithm\": \"Rules\",\n"
        "            \"drivers\": explain_prediction(features, prediction)\n"
        "        }\n"
        "    model = payload[\"model\"]\n"
        "    values = pd.DataFrame([[features[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)\n"
        "    prediction = model.predict(values)[0]\n"
        "    return {\n"
        "        \"prediction\": prediction,\n"
        "        \"confidence\": float(max(model.predict_proba(values)[0])),\n"
        "        \"algorithm\": \"RandomForest\"\n"
        "    }"
    )
    pages[46].append(Table([[Paragraph(snippet_3.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 6),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 47: APPENDIX E - CODE SNIPPET 4 (TRAIN)
    # -------------------------------------------------------------------------
    pages[47].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS (CONTINUED)", style_h1))
    pages[47].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[47].append(Paragraph("D. Model Training & Pipeline in train.py", style_h2))
    snippet_4 = (
        "def train_model():\n"
        "    data = pd.read_csv(TRAINING_DATA_PATH)\n"
        "    X = data[FEATURE_NAMES]\n"
        "    y = data['burnout_risk']\n"
        "    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n"
        "    models = {\n"
        "        'DecisionTree': DecisionTreeClassifier(max_depth=5, random_state=42),\n"
        "        'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)\n"
        "    }\n"
        "    best_acc = 0.0\n"
        "    best_model = None\n"
        "    for name, model in models.items():\n"
        "        model.fit(X_train, y_train)\n"
        "        acc = accuracy_score(y_test, model.predict(X_test))\n"
        "        if acc > best_acc:\n"
        "            best_acc = acc\n"
        "            best_model = model\n\n"
        "    joblib.dump({'model': best_model, 'features': FEATURE_NAMES}, MODEL_PATH)"
    )
    pages[47].append(Table([[Paragraph(snippet_4.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 6),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 48: APPENDIX E - CODE SNIPPET 5 (NLP)
    # -------------------------------------------------------------------------
    pages[48].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS (CONTINUED)", style_h1))
    pages[48].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[48].append(Paragraph("E. Local Sentiment Score parsing in sentiment.py", style_h2))
    snippet_5 = (
        "def get_sentiment_score(text: str) -> float:\n"
        "    if not text or not text.strip():\n"
        "        return 0.0\n"
        "    if _USE_HF and _hf_model is not None:\n"
        "        try:\n"
        "            result = _hf_model(text[:512])[0]\n"
        "            return _hf_score_to_compound(result)\n"
        "        except Exception:\n"
        "            pass\n\n"
        "    analyzer = _get_analyzer()\n"
        "    if analyzer is None:\n"
        "        return 0.0\n"
        "    return float(analyzer.polarity_scores(text)['compound'])"
    )
    pages[48].append(Table([[Paragraph(snippet_5.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 8),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 49: APPENDIX E - CODE SNIPPET 6 (COMPILER)
    # -------------------------------------------------------------------------
    pages[49].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS (CONTINUED)", style_h1))
    pages[49].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[49].append(Paragraph("F. Database Log Compiler in export_db_to_training.py", style_h2))
    snippet_6 = (
        "def compile_db_features(user_id):\n"
        "    logs = MoodLog.query.filter_by(user_id=user_id).order_by(MoodLog.log_date.asc()).all()\n"
        "    rows = []\n"
        "    for log in logs:\n"
        "        features = build_features(\n"
        "            user_id=log.user_id,\n"
        "            log_date=log.log_date,\n"
        "            mood_score=log.mood_score,\n"
        "            sleep_hours=log.sleep_hours,\n"
        "            stress_level=log.stress_level,\n"
        "            activity_done=log.activity_done,\n"
        "            social_interaction=log.social_interaction,\n"
        "            sentiment_score=log.sentiment_score\n"
        "        )\n"
        "        features['burnout_risk'] = log.burnout_risk\n"
        "        rows.append(features)\n"
        "    return pd.DataFrame(rows)"
    )
    pages[49].append(Table([[Paragraph(snippet_6.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 8),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 50: APPENDIX E - CODE SNIPPET 7 (TESTS)
    # -------------------------------------------------------------------------
    pages[50].append(Paragraph("APPENDIX E: IMPORTANT CODE SNIPPETS (CONTINUED)", style_h1))
    pages[50].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    pages[50].append(Paragraph("G. PyTest test cases in test_app.py", style_h2))
    snippet_7 = (
        "def test_mood_logging_flow(client, auth_headers):\n"
        "    # 1. Post daily metrics check-in\n"
        "    resp = client.post('/log', data={\n"
        "        'mood_score': 4,\n"
        "        'sleep_hours': 7.5,\n"
        "        'stress_level': 2,\n"
        "        'activity_done': 'y',\n"
        "        'social_interaction': 3,\n"
        "        'notes': 'Had a highly productive day, sleep was refreshing.'\n"
        "    }, headers=auth_headers)\n"
        "    assert resp.status_code == 302\n\n"
        "    # 2. Verify encrypted field values and classification\n"
        "    log = MoodLog.query.order_by(MoodLog.created_at.desc()).first()\n"
        "    assert log.mood_score == 4\n"
        "    assert log.notes == 'Had a highly productive day, sleep was refreshing.'\n"
        "    assert log.burnout_risk == 'Low'"
    )
    pages[50].append(Table([[Paragraph(snippet_7.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 6),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))

    # -------------------------------------------------------------------------
    # PAGE 51: REFERENCES
    # -------------------------------------------------------------------------
    pages[51].append(Paragraph("REFERENCES & BIBLIOGRAPHY", style_h1))
    pages[51].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    refs_1 = (
        "1. Flask Documentation, Pallets Projects, https://flask.palletsprojects.com/<br/>"
        "2. Python Software Foundation Documentation, https://docs.python.org/<br/>"
        "3. SQLite Consortium, File-based DB Engine, https://www.sqlite.org/docs.html<br/>"
        "4. pandas Documentation, Data Handling structures, https://pandas.pydata.org/docs/<br/>"
        "5. NumPy Developers, Numeric calculations, https://numpy.org/doc/<br/>"
        "6. scikit-learn Machine Learning Library in Python, https://scikit-learn.org/stable/<br/>"
        "7. NLTK Sentiment intensity, VADER Lexicon, https://www.nltk.org/api/nltk.sentiment.html<br/>"
        "8. Three.js WebGL rendering engine, Three.js documentation, https://threejs.org/docs/<br/>"
        "9. Chart.js visual graphics charting, https://www.chartjs.org/docs/latest/<br/>"
        "10. ReportLab PDF Generation software, https://www.reportlab.com/docs/"
    )
    pages[51].append(Paragraph(refs_1, style_body_justify))

    # -------------------------------------------------------------------------
    # PAGE 52: REFERENCES (CONTINUED)
    # -------------------------------------------------------------------------
    pages[52].append(Paragraph("REFERENCES & BIBLIOGRAPHY (CONTINUED)", style_h1))
    pages[52].append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    refs_2 = (
        "11. PyTest testing framework automation, https://docs.pytest.org/en/stable/<br/>"
        "12. Werkzeug Security & Utility helper, Pallets, https://werkzeug.palletsprojects.com/<br/>"
        "13. Flask-Login session management, https://flask-login.readthedocs.io/en/latest/<br/>"
        "14. Flask-WTF CSRF validation, https://flask-wtf.readthedocs.io/en/latest/<br/>"
        "15. Flask-Talisman HTTP security headers, https://github.com/GoogleCloudPlatform/flask-talisman<br/>"
        "16. Flask-Limiter token bucket rate logging, https://flask-limiter.readthedocs.io/en/stable/<br/>"
        "17. Cryptography Fernet symmetric encryption, PyCA, https://cryptography.io/en/latest/<br/>"
        "18. Evidently AI model drift calculations (KS-test), https://docs.evidentlyai.com/<br/>"
        "19. Hugging Face Transformers pipeline (DistilBERT), https://huggingface.co/docs/transformers/<br/>"
        "20. WCAG 2.1 Web Accessibility Guidelines, W3C Recommendation, https://www.w3.org/TR/WCAG21/"
    )
    pages[52].append(Paragraph(refs_2, style_body_justify))

    # Construct the final story. Every page gets extended, followed by a PageBreak (except page 52)
    for i in range(1, 52):
        story.extend(pages[i])
        story.append(PageBreak())
    
    # Page 52 has no trailing PageBreak
    story.extend(pages[52])
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Technical Document PDF generated successfully at: {pdf_path}")

if __name__ == '__main__':
    build_pdf()
