import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

class StrategyCanvas(canvas.Canvas):
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
            
            # Colors
            primary_color = colors.HexColor("#0F766E")  # Teal Accent
            muted_color = colors.HexColor("#64748B")    # Slate Gray
            border_color = colors.HexColor("#CBD5E1")   # Light Gray border
            
            # --- RUNNING HEADER ---
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(primary_color)
            self.drawString(54, 750, "DAYTONE  |  COMPLETED PROJECT PRESENTATION STRATEGY")
            
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(muted_color)
            self.drawRightString(558, 750, "Incremental Reveal & Re-engineering Guide")
            
            # Header Line
            self.setStrokeColor(border_color)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # --- RUNNING FOOTER ---
            self.setFont("Helvetica", 8)
            self.setFillColor(muted_color)
            self.drawString(54, 40, "Academic Guide  •  Prepared for S A Sanush (S3 MCA)  •  DayTone Mood Analyser")
            self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
            
            # Footer Line
            self.line(54, 50, 558, 50)
            
            self.restoreState()

def build_pdf():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(base_dir, "DayTone_Completed_Project_Strategy.pdf")
    
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
    
    # Palette
    c_primary = colors.HexColor("#0F766E")    # Deep Teal
    c_secondary = colors.HexColor("#0D9488")  # Teal
    c_dark = colors.HexColor("#1F2937")       # Charcoal
    c_danger = colors.HexColor("#B91C1C")     # Crimson
    c_navy = colors.HexColor("#1B365D")       # Deep Navy
    c_bg_light = colors.HexColor("#F8FAFC")   # Slate 50
    
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=c_navy,
        spaceAfter=15
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=c_primary,
        spaceAfter=30
    )
    
    style_h1 = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=6
    )
    
    style_body_justify = ParagraphStyle(
        'BodyJustify',
        parent=style_body,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    style_list_item = ParagraphStyle(
        'ListItem',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    style_q_text = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_navy,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )
    
    style_a_text = ParagraphStyle(
        'AnswerText',
        parent=style_body,
        leftIndent=15,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    story = []
    
    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 80))
    story.append(HRFlowable(width="100%", thickness=4, color=c_primary, spaceBefore=0, spaceAfter=20))
    
    story.append(Paragraph("STRATEGY FOR DELIVERING A COMPLETED PROJECT", style_cover_title))
    story.append(Paragraph("How to Structure, Slow-Walk, and Present DayTone in Weekly & Monthly Reviews", style_cover_subtitle))
    
    story.append(HRFlowable(width="30%", thickness=1, color=c_navy, spaceBefore=0, spaceAfter=25, hAlign='CENTER'))
    
    intro_box_text = (
        "<b>Academic Strategy Note:</b> Having your Semester 3 MCA project fully complete in June is a massive "
        "advantage, but it presents a unique challenge. If you present a fully finished application in your first review, "
        "the evaluation panel will have nothing to evaluate in the following months and may suspect the project was copied. "
        "This guide outlines the 'Progressive Reveal' strategy: simulating week-by-week development, re-engineering Git "
        "commits, temporarily hiding finished modules, and framing ongoing work as advanced refactoring, testing, and "
        "security hardening."
    )
    
    intro_table = Table([[Paragraph(intro_box_text, style_body_justify)]], colWidths=[504])
    intro_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(intro_table)
    
    story.append(Spacer(1, 100))
    
    meta_data = [
        [Paragraph("Candidate Name:", ParagraphStyle('BLabel', parent=style_body, fontName='Helvetica-Bold')), Paragraph("S A Sanush", style_body)],
        [Paragraph("Academic Year:", ParagraphStyle('BLabel', parent=style_body, fontName='Helvetica-Bold')), Paragraph("2026 (Semester 3)", style_body)],
        [Paragraph("Project Name:", ParagraphStyle('BLabel', parent=style_body, fontName='Helvetica-Bold')), Paragraph("DayTone Mood Analyser", style_body)],
        [Paragraph("Evaluation Window:", ParagraphStyle('BLabel', parent=style_body, fontName='Helvetica-Bold')), Paragraph("June 2026 – October/November 2026", style_body)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 384])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#F1F5F9")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(meta_table)
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: GIT COMMIT & MODULAR COMMENT-OUT STRATEGY
    # =========================================================================
    story.append(Paragraph("1. The Simulated Git & Version Control Strategy", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))
    
    git_intro = (
        "Internal project guides regularly review your GitHub repository contribution graph to verify authenticity. "
        "If you commit all 5,000 lines of code in a single day, it raises a major red flag. Use the Git Re-engineering "
        "strategy to make your contribution graph look organic and active throughout the semester."
    )
    story.append(Paragraph(git_intro, style_body_justify))
    
    git_steps = [
        "<b>Step 1: Keep a Backup Branch.</b> Create a new private branch named <code>prod-stable</code> (or keep a local copy outside the repository) that contains the 100% completed project.",
        "<b>Step 2: Initialize a Clean Main Branch.</b> Re-initialize your <code>main</code> branch with only the basic project structure (e.g., <code>README.md</code>, empty <code>app/</code> folder, and <code>requirements.txt</code>). Push this as your 'initial startup' commit in July.",
        "<b>Step 3: Scheduled Copying (The Git Trick).</b> Every week, copy over *only* the specific folder or files scheduled for that week from your completed backup into your active local workspace. For example, in Week 2, copy over <code>app/auth/</code>. In Week 3, copy over <code>app/nlp/</code>.",
        "<b>Step 4: Commit with Micro-Logs.</b> Commit those files with detailed messages as if you just wrote them. Example: <i>\"feat: implement scrypt password hashing and user signup forms validation\"</i>. Make 2 or 3 small commits during the week.",
        "<b>Step 5: Push Before Your Weekly Review.</b> Push the branch to GitHub a day before your weekly meeting. When the teacher checks your repository, they will see a beautiful history of active, progressive coding."
    ]
    for step in git_steps:
        story.append(Paragraph(step, style_list_item))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Modular UI Comment-Out Strategy (The Local Demo)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))
    
    ui_intro = (
        "When running the project locally on your laptop to show your guide, you cannot display the entire, polished dashboard "
        "on week 2. You must temporarily hide or disable advanced features in the user interface."
    )
    story.append(Paragraph(ui_intro, style_body_justify))
    
    ui_steps = [
        "<b>Hide Navigation Links:</b> Open your main layout template (e.g., <code>app/templates/base.html</code>) and comment out the navigation links to the Dashboard, ML Predictor, and Admin Panel. Only leave 'Login' and 'Daily Check-in' active in July.",
        "<b>Disable Blueprints:</b> If a nosy evaluator tries to manually type the URL (like <code>/admin</code> or <code>/ml</code>), you can temporarily comment out the blueprint registration in <code>app/__init__.py</code> so it throws a 404 page.",
        "<b>Uncomment Step-by-Step:</b> As you progress through the semester, slowly uncomment the UI links and blueprint registrations one by one. By September, uncomment the Chart.js code. By October, uncomment the Admin panel and Docker scripts.",
        "<b>Pre-populate Data Safely:</b> Since the app requires history to show nice charts, use the synthetic data generator (<code>generate_data.py</code>). Tell your guide: <i>\"I generated synthetic logs to test how the frontend database queries handle larger datasets.\"</i>"
    ]
    for step in ui_steps:
        story.append(Paragraph(step, style_list_item))
        
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 3: THE REFACTORING NARRATIVE & CRITICAL DEFENCE
    # =========================================================================
    story.append(Paragraph("3. The 'Refactoring & Tuning' Narrative", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))
    
    narrative_intro = (
        "Since your code is complete, you will have empty weeks where you have 'nothing to write'. Frame these "
        "weeks as optimization, performance tuning, and security compliance phases. This makes you look like a highly "
        "diligent, professional developer."
    )
    story.append(Paragraph(narrative_intro, style_body_justify))
    
    narrative_options = [
        "<b>The SQL Tuning Story:</b> <i>\"This week, I was looking into database latency. I optimized the SQLAlchemy models by adding composite indexes and refactored the query loads to prevent the N+1 select query problem on the history route.\"</i>",
        "<b>The GPU Optimization Story:</b> <i>\"I spent this week optimizing our WebGL Simplex Noise shader for the 3D Mood Orb in <code>static/js/orb.js</code>. I patched a modulo division glitch that caused visual flickering on slower GPU architectures like mobile devices.\"</i>",
        "<b>The Security Hardening Story:</b> <i>\"I ran our security auditing suite (<code>security_audit.py</code>). Based on the report, I hardened the Flask session cookies to HttpOnly, SameSite=Lax, and integrated Flask-Talisman to enforce Content Security Policies (CSP) to prevent cross-site scripting (XSS).\"</i>",
        "<b>The Ethics & Bias Story:</b> <i>\"This week I audited our Random Forest classifier for bias using our demographic auditing script (<code>bias_audit.py</code>). I wanted to verify that our burnout prediction accuracy remains fair across different cohorts (such as people logging very low sleep vs high sleep).\"</i>",
        "<b>The Code Coverage Story:</b> <i>\"I set up automated testing scripts using pytest in the <code>tests/</code> directory. I increased our code test coverage to over 90% by writing unit tests for our NLP compound scoring and user deletion GDPR routes.\"</i>"
    ]
    for option in narrative_options:
        story.append(Paragraph(option, style_list_item))
        
    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Defensive Q&A: Handling Teacher Suspicion", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))
    
    suspicion_intro = (
        "Occasionally, a teacher might ask: 'Why did you complete this so quickly?' or 'Are you sure you wrote this code?' "
        "Use these structured answers to defend your work professionally."
    )
    story.append(Paragraph(suspicion_intro, style_body_justify))
    
    questions = [
        (
            "Teacher: \"Your project structure looks extremely professional and complex for a S3 MCA student. Did you write this yourself?\"",
            "<b>Response:</b> <i>\"Yes, sir. I spent a lot of time reading production-grade Flask structures on GitHub and studied standard software blueprints. I wanted to build DayTone as a production-ready application rather than a simple class assignment. I containerized it with Docker and set up Redis rate-limiting to learn real-world deployment architectures.\"</i>"
        ),
        (
            "Teacher: \"The database encryption and model drift monitoring are very advanced. Why did you add them?\"",
            "<b>Response:</b> <i>\"Since the application stores highly sensitive, personal journal entries, standard plain-text storage would fail basic security compliance. I implemented AES-256 at rest to protect user privacy. Model drift monitoring was added because machine learning models degrade when user habits shift. This is a critical requirement for deploying AI in the real world.\"</i>"
        ),
        (
            "Teacher: \"Why are you making so many code refactor commits on GitHub instead of adding new features?\"",
            "<b>Response:</b> <i>\"Sir, once the core features were stable, I shifted my focus to code quality and security. Writing clean code, auditing configurations (using my security audit script), and increasing unit test coverage is just as important as writing the initial logic to prevent bugs when deployed to Render.\"</i>"
        )
    ]
    for q, a in questions:
        story.append(Paragraph(q, style_q_text))
        story.append(Paragraph(a, style_a_text))
        
    doc.build(story, canvasmaker=StrategyCanvas)
    print(f"Strategy PDF generated successfully at: {pdf_path}")

if __name__ == '__main__':
    build_pdf()
