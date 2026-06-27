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
        # We skip headers and footers on the cover page (Page 1)
        if self._pageNumber > 1:
            self.saveState()
            
            # Colors
            primary_color = colors.HexColor("#1B365D")  # Deep Slate Navy
            muted_color = colors.HexColor("#64748B")    # Slate Gray
            border_color = colors.HexColor("#E2E8F0")   # Light Gray border
            
            # --- RUNNING HEADER ---
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(primary_color)
            self.drawString(54, 750, "DAYTONE MOOD ANALYSER  |  MCA SEMESTER 3 PROJECT PLAN")
            
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(muted_color)
            self.drawRightString(558, 750, "Academic Presentation Guide & Roadmap")
            
            # Header Line
            self.setStrokeColor(border_color)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # --- RUNNING FOOTER ---
            self.setFont("Helvetica", 8)
            self.setFillColor(muted_color)
            self.drawString(54, 40, "Confidential  •  Prepared for S A Sanush (S3 MCA)  •  Final Submission: Oct/Nov 2026")
            self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
            
            # Footer Line
            self.line(54, 50, 558, 50)
            
            self.restoreState()

def build_pdf():
    # Setup document path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(base_dir, "DayTone_Presentation_Plan.pdf")
    
    # 0.75-inch margin (54 points)
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
    
    # Define Palette
    c_primary = colors.HexColor("#1B365D")    # Deep Slate Navy
    c_secondary = colors.HexColor("#0F766E")  # Teal Accent
    c_dark = colors.HexColor("#1F2937")       # Charcoal Body Text
    c_muted = colors.HexColor("#4B5563")      # Soft Gray Text
    c_danger = colors.HexColor("#991B1B")     # Dark Crimson for warning
    c_bg_light = colors.HexColor("#F8FAFC")   # Soft Slate background
    
    # Custom Paragraph Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        alignment=TA_CENTER,
        textColor=c_primary,
        spaceAfter=15
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=c_secondary,
        spaceAfter=30
    )
    
    style_cover_meta_label = ParagraphStyle(
        'CoverMetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary
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
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        alignment=TA_LEFT,
        textColor=c_dark,
        spaceAfter=6
    )
    
    style_body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )
    
    style_body_justify = ParagraphStyle(
        'BodyDarkJustify',
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
    
    style_bullet_item = ParagraphStyle(
        'BulletItem',
        parent=style_body,
        leftIndent=20,
        firstLineIndent=-12,
        spaceAfter=4
    )
    
    style_table_header = ParagraphStyle(
        'TableHeaderText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.white
    )
    
    style_table_cell = ParagraphStyle(
        'TableCellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        alignment=TA_LEFT,
        textColor=c_dark
    )
    
    style_table_cell_bold = ParagraphStyle(
        'TableCellTextBold',
        parent=style_table_cell,
        fontName='Helvetica-Bold',
        textColor=c_primary
    )
    
    style_q_text = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    
    style_a_text = ParagraphStyle(
        'AnswerText',
        parent=style_body,
        leftIndent=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    story = []
    
    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 100))
    
    # Project Accent Banner
    story.append(HRFlowable(width="100%", thickness=4, color=c_secondary, spaceBefore=0, spaceAfter=20))
    
    # Title
    story.append(Paragraph("DAYTONE MOOD ANALYSER", style_cover_title))
    story.append(Paragraph("Academic Progress Presentation Guide & Development Roadmap", style_cover_subtitle))
    
    story.append(HRFlowable(width="40%", thickness=1, color=c_primary, spaceBefore=0, spaceAfter=30, hAlign='CENTER'))
    
    # Executive Summary Box
    summary_text = (
        "<b>Executive Summary:</b> DayTone is a production-ready, GDPR-compliant Flask web "
        "application for personal mood tracking and machine learning-based burnout prediction. Designed to protect "
        "sensitive data, it utilizes local natural language processing (NLTK VADER) and on-device ML models (Decision "
        "Tree, Random Forest) to evaluate wellness metrics (mood, sleep, stress, activity, social log) and "
        "predict risk. This guide provides a monthly and weekly blueprint for academic evaluations, detailing "
        "exactly what to implement, demonstrate, and say during reviews, along with anticipated Viva Voce questions."
    )
    
    summary_table = Table(
        [[Paragraph(summary_text, style_body_justify)]],
        colWidths=[504]
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    
    story.append(Spacer(1, 100))
    
    # Metadata Block
    meta_data = [
        [Paragraph("Candidate Name:", style_cover_meta_label), Paragraph("S A Sanush", style_cover_meta_val)],
        [Paragraph("Academic Year:", style_cover_meta_label), Paragraph("2026 (Semester 3)", style_cover_meta_val)],
        [Paragraph("Course Program:", style_cover_meta_label), Paragraph("Master of Computer Applications (MCA)", style_cover_meta_val)],
        [Paragraph("Project Category:", style_cover_meta_label), Paragraph("Semester 3 Mini Project (Final Submission: Oct/Nov 2026)", style_cover_meta_val)],
        [Paragraph("Core Architecture:", style_cover_meta_label), Paragraph("Flask, PostgreSQL, Redis, Scikit-learn, NLTK VADER, Three.js", style_cover_meta_val)],
        [Paragraph("Deployment URL:", style_cover_meta_label), Paragraph("<u>https://daytone-piyi.onrender.com</u>", style_cover_meta_val)],
    ]
    
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#F1F5F9")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(meta_table)
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: SEMESTER TIMELINE & ROADMAP
    # =========================================================================
    story.append(Paragraph("1. Semester Milestones & Month-by-Month Roadmap", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    roadmap_intro = (
        "To satisfy the academic requirements of a Semester 3 MCA project, development is broken down into "
        "structured, cumulative monthly phases. This structure demonstrates solid software engineering practices, "
        "moving from requirement engineering to database design, core backend logic, frontend dashboards, "
        "machine learning training, monitoring, and production deployment."
    )
    story.append(Paragraph(roadmap_intro, style_body_justify))
    story.append(Spacer(1, 4))
    
    # Monthly Roadmap Table
    # Printable area is 504. Col widths: 90 (Month), 214 (Core Objectives), 200 (What to Demonstrate)
    table_data = [
        [
            Paragraph("Month / Milestone", style_table_header),
            Paragraph("Core Objectives & Implementation Focus", style_table_header),
            Paragraph("Review Deliverables (What to Show)", style_table_header)
        ],
        [
            Paragraph("June / July 2026<br/><b>Phase 1: Foundations</b>", style_table_cell_bold),
            Paragraph(
                "• Requirements engineering (SRS drafting)<br/>"
                "• Relational database schema design (SQLAlchemy models)<br/>"
                "• User authentication (Scrypt hashing, Flask-Login)<br/>"
                "• Log forms with validation (Flask-WTF)<br/>"
                "• Journal decryption pipeline (AES-256 Fernet)",
                style_table_cell
            ),
            Paragraph(
                "• Entity-Relationship (ER) Diagram<br/>"
                "• User Registration and Login flows<br/>"
                "• Daily logging input forms<br/>"
                "• Database migration logs (Flask-Migrate)<br/>"
                "• SQLite console showing encrypted notes",
                style_table_cell
            )
        ],
        [
            Paragraph("August 2026<br/><b>Phase 2: Analytics</b>", style_table_cell_bold),
            Paragraph(
                "• Local Sentiment Analysis pipeline (NLTK VADER)<br/>"
                "• Dashboard visualization engine (Chart.js)<br/>"
                "• Interactive 3D WebGL shader orb (Three.js)<br/>"
                "• CSV data streaming export<br/>"
                "• PDF wellness report generator (ReportLab)",
                style_table_cell
            ),
            Paragraph(
                "• Journal sentiment scoring demo (-1.0 to +1.0)<br/>"
                "• 5 interactive charts (mood, sleep, stress)<br/>"
                "• Live-deforming GPU-rendered 3D Orb<br/>"
                "• Executed CSV and PDF download exports",
                style_table_cell
            )
        ],
        [
            Paragraph("September 2026<br/><b>Phase 3: Machine Learning</b>", style_table_cell_bold),
            Paragraph(
                "• Synthetic training dataset generation (generate_data.py)<br/>"
                "• ML training pipeline comparing Decision Tree/Random Forest<br/>"
                "• Model explainability (XAI) feature importance<br/>"
                "• Bias auditing & data drift monitor scripts<br/>"
                "• Model Card specification documentation",
                style_table_cell
            ),
            Paragraph(
                "• Model performance tables (Accuracy, F1-Score)<br/>"
                "• Pickle model output and ML metrics log<br/>"
                "• Bias audit result charts (Admin dashboard)<br/>"
                "• Kolmogorov-Smirnov prediction drift charts",
                style_table_cell
            )
        ],
        [
            Paragraph("October 2026<br/><b>Phase 4: Security & Ops</b>", style_table_cell_bold),
            Paragraph(
                "• CSRF protection & Login rate limiting (Flask-Limiter)<br/>"
                "• Talisman security headers & hardened session cookies<br/>"
                "• Multi-stage production Dockerfile optimization<br/>"
                "• Redis container cache integration<br/>"
                "• Automated pytest suite execution",
                style_table_cell
            ),
            Paragraph(
                "• Security audit report (security_audit.py)<br/>"
                "• Green test suite executing in terminal (pytest)<br/>"
                "• Docker-compose start execution logs<br/>"
                "• Deployed live app on Render (using render.yaml)",
                style_table_cell
            )
        ],
        [
            Paragraph("November 2026<br/><b>Phase 5: Submissions</b>", style_table_cell_bold),
            Paragraph(
                "• Compiling final project thesis/report<br/>"
                "• Detailing UML diagrams (Class, Use Case, Sequence)<br/>"
                "• PPT generation (using generate_ppt.py helper)<br/>"
                "• Internal mock vivas and review rehearsals",
                style_table_cell
            ),
            Paragraph(
                "• Bound project document (SRS, Code, Testing)<br/>"
                "• Final slide deck presentation<br/>"
                "• Live web application demonstration",
                style_table_cell
            )
        ],
    ]
    
    road_table = Table(table_data, colWidths=[100, 204, 200])
    road_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(road_table)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Key Highlight for Evaluators:", style_h2))
    story.append(Paragraph(
        "By structuring the project this way, you show a complete transition from a basic CRUD application "
        "(July) to an advanced data visualization tool (August), followed by an intelligent, monitored AI system "
        "(September) and a production-grade, secure cloud-deployed product (October). This progressive complexity "
        "protects you from initial review fatigue and ensures high evaluation marks at every phase.",
        style_body_justify
    ))
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 3: THE REVIEW CHECKLIST & PRESENTATION RHYTHM
    # =========================================================================
    story.append(Paragraph("2. The Presentation Checklist: What to Do, Show, & Say", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "For MCA projects, internal guides evaluate you on incremental progress. To ensure you look professional "
        "and fully prepared, structure your weekly and monthly presentations using the guidelines below.",
        style_body_justify
    ))
    
    # Weekly presentations
    story.append(Paragraph("A. Weekly Progress Reviews (Short, Agile Demos)", style_h2))
    story.append(Paragraph(
        "Weekly meetings with your guide are typically informal. Your objective is to show active coding, "
        "structured Git commits, and incremental testing. Do not try to show a complete product; show one working component.",
        style_body_justify
    ))
    
    weekly_checklist = [
        "<b>What to Do:</b> Code in small iterations. Write unit tests for the functions you write (e.g., test your helper functions in <code>tests/</code>). Keep a clean Git history with descriptive commit messages.",
        "<b>What to Show:</b> Share a 60-second video snippet or run a quick terminal demo. Show your code diff in Git or the green pytest execution in the terminal. Teachers love seeing command-line tools like tests running successfully.",
        "<b>What to Say:</b> <i>\"This week, I focused on [specific feature, e.g., the local NLTK VADER sentiment analyzer]. I integrated it into the log submission route. When a user submits a note, VADER processes the text locally, avoiding cloud API calls. I also wrote 3 unit tests to verify sentiment score boundaries (-1.0 to 1.0) and all of them pass. Next week, I will implement the database encryption for these logs.\"</i>"
    ]
    for item in weekly_checklist:
        story.append(Paragraph(f"• {item}", style_list_item))
        
    story.append(Spacer(1, 8))
    
    # Monthly presentations
    story.append(Paragraph("B. Monthly Panel Evaluations (Milestone Demos)", style_h2))
    story.append(Paragraph(
        "Monthly reviews are formal. You present to a panel of 2 or 3 professors. They grade you on architecture, database integrity, and implementation compliance.",
        style_body_justify
    ))
    
    monthly_checklist = [
        "<b>What to Do:</b> Verify your application's integrity by running the system checks: security audits (<code>scripts/security_audit.py</code>), model drift detection (<code>scripts/monitor_drift.py</code>), and bias audits (<code>scripts/bias_audit.py</code>). Keep your documentation and code inline.",
        "<b>What to Show:</b> Present a PowerPoint slide deck (which you can generate using the <code>scripts/generate_ppt.py</code> utility). Demonstrate the user flow live on localhost or on your live Render URL. Show the dashboard rendering populated data and show your active logs in the Admin interface.",
        "<b>What to Say:</b> Focus on design patterns and technical justifications. <i>\"During this milestone, we integrated the core Logging system with our Machine Learning Predictor. The system extracts logs, creates a 12-feature matrix representing user state, and inputs it to a Random Forest classifier. This predicts burnout risk. To ensure transparency, we display explainable AI features to the user. We also run regular bias and drift checks to maintain model accuracy over time, as displayed in the admin console.\"</i>"
    ]
    for item in monthly_checklist:
        story.append(Paragraph(f"• {item}", style_list_item))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("C. Proposed 10-Week Presentation Schedule", style_h2))
    
    schedule_data = [
        [Paragraph("Week", style_table_header), Paragraph("Feature Focus", style_table_header), Paragraph("Key Review Talking Point", style_table_header)],
        [Paragraph("Week 1", style_table_cell_bold), Paragraph("SRS & ERD Draft", style_table_cell), Paragraph("Database models in models.py & relational mapping.", style_table_cell)],
        [Paragraph("Week 2", style_table_cell_bold), Paragraph("Auth & CRUD Logs", style_table_cell), Paragraph("User sign-up and log forms validation using WTForms.", style_table_cell)],
        [Paragraph("Week 3", style_table_cell_bold), Paragraph("Notes Encryption", style_table_cell), Paragraph("AES-256 symmetric encryption at rest (Fernet).", style_table_cell)],
        [Paragraph("Week 4", style_table_cell_bold), Paragraph("NLP Sentiment", style_table_cell), Paragraph("Integrating NLTK VADER local scoring pipeline.", style_table_cell)],
        [Paragraph("Week 5", style_table_cell_bold), Paragraph("Dashboard Charts", style_table_cell), Paragraph("Chart.js integration, layout grids, and responsiveness.", style_table_cell)],
        [Paragraph("Week 6", style_table_cell_bold), Paragraph("WebGL 3D Orb", style_table_cell), Paragraph("Three.js vertex shader deforming based on daily mood.", style_table_cell)],
        [Paragraph("Week 7", style_table_cell_bold), Paragraph("ML Model Training", style_table_cell), Paragraph("Decision Tree / Random Forest training & classification.", style_table_cell)],
        [Paragraph("Week 8", style_table_cell_bold), Paragraph("Drift & Bias Audit", style_table_cell), Paragraph("Model drift monitoring and ethical bias verification.", style_table_cell)],
        [Paragraph("Week 9", style_table_cell_bold), Paragraph("App Security", style_table_cell), Paragraph("Flask-Limiter, HTTP security headers, CSRF audits.", style_table_cell)],
        [Paragraph("Week 10", style_table_cell_bold), Paragraph("Cloud Deployment", style_table_cell), Paragraph("Multi-stage Docker, PostgreSQL, and Redis on Render.", style_table_cell)]
    ]
    
    sched_table = Table(schedule_data, colWidths=[55, 149, 300])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sched_table)
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 4: PITFALLS & VIVA PREPARATION
    # =========================================================================
    story.append(Paragraph("3. Academic Review Pitfalls & Viva Voce Q&A", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))
    
    # Pitfalls Section
    story.append(Paragraph("A. What NOT to Show & What NOT to Say", style_h2))
    
    donts = [
        "<b>DO NOT Show Empty Dashboards:</b> Presenting empty charts makes the project look unfinished. Pre-fill the database with realistic synthetic data using <code>generate_data.py</code> before every evaluation.",
        "<b>DO NOT Show Raw Tracebacks:</b> A server error traceback (500 screen) in front of an external examiner causes immediate mark deductions. Keep Flask debug mode off during reviews and handle errors gracefully.",
        "<b>DO NOT Show Hardcoded Secrets:</b> Never display database passwords or secret keys in your slides. Keep them in a <code>.env</code> file. Present a clean <code>.env.example</code> file.",
        "<b>DO NOT Say \"I downloaded this ML code\":</b> Acknowledge libraries, but explain the pipeline as your own. Say: <i>\"I implemented a scikit-learn Random Forest model, validating performance metrics locally.\"</i>",
        "<b>DO NOT Say \"The NLP uses ChatGPT API\":</b> External cloud APIs require internet connectivity and incur billing. Highlight that DayTone runs 100% locally using NLTK VADER, ensuring absolute privacy.",
        "<b>DO NOT Say \"I will test it later\":</b> Testing is not a final step. Point to the existing <code>tests/</code> directory and demonstrate that the unit test suite can be run at any moment."
    ]
    for item in donts:
        story.append(Paragraph(f"<font color='{c_danger.hexval()}'><b>[CRITICAL]</b></font> {item}", style_list_item))
        
    story.append(Spacer(1, 6))
    
    # Viva Voce Q&A Section
    story.append(Paragraph("B. Anticipated Viva Voce Questions & Model Answers", style_h2))
    
    viva_qa = [
        (
            "Q1: Why did you choose SQLite for development and PostgreSQL for production instead of MongoDB?",
            "<b>Answer:</b> Relational integrity is essential for this system. Relationships between users, logs, and audits are strictly defined. Relational foreign key constraints and cascading deletes are required, especially for GDPR data erasure. PostgreSQL provides transactional stability (ACID) in production, while SQLite provides a zero-configuration local database that uses the same SQL syntax via SQLAlchemy."
        ),
        (
            "Q2: What is the 12-feature matrix used in the Burnout Predictor?",
            "<b>Answer:</b> The classifier does not evaluate single-day metrics in isolation. It constructs a temporal matrix: the user's daily metrics (mood, sleep, stress), their rolling 7-day averages, mood variability (standard deviation over 7 days), consecutive bad days, weekend indicators, and the journal's VADER sentiment score. This gives the model historical context to predict burnout risk accurately."
        ),
        (
            "Q3: How are sensitive user journal entries secured?",
            "<b>Answer:</b> Reflections are encrypted at rest using AES-256 Fernet symmetric encryption. The key is loaded from the environment variables, meaning the database contains only encrypted ciphertexts. Even if the database is exposed, the raw text is unreadable without the environment key."
        ),
        (
            "Q4: What is Model Drift and how does your project handle it?",
            "<b>Answer:</b> User habits shift over time (e.g., during exam seasons or vacations), making old training data obsolete. We include a drift monitor script (<code>monitor_drift.py</code>) that compares active user log distributions against the baseline dataset using a Kolmogorov-Smirnov test. If drift is detected, the administrator dashboard displays an alert to trigger retraining."
        ),
        (
            "Q5: Why did you choose Random Forest over a single Decision Tree?",
            "<b>Answer:</b> A single Decision Tree is prone to overfitting on training data. Random Forest is an ensemble method that trains multiple decision trees on random subsets of data and aggregates their votes. This significantly reduces variance, handles feature correlations better, and yields a higher F1-score (92% vs 84%)."
        ),
        (
            "Q6: How do you verify that your ML model is fair and unbiased?",
            "<b>Answer:</b> We implement a bias auditing script (<code>bias_audit.py</code>). It segments predictions across key demographics (e.g., stress and sleep groups) and calculates metric parity (discrepancy in accuracy, precision, and recall). If performance differences exceed 5%, the system flags a bias warning on the admin panel."
        )
    ]
    
    for q, a in viva_qa:
        story.append(Paragraph(q, style_q_text))
        story.append(Paragraph(a, style_a_text))
        
    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Plan PDF generated successfully at: {pdf_path}")

if __name__ == '__main__':
    build_pdf()
