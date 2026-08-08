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
            primary_color = colors.HexColor("#0F766E")  # Teal Accent
            muted_color = colors.HexColor("#64748B")    # Slate Gray
            border_color = colors.HexColor("#E2E8F0")   # Light Gray border
            
            # --- RUNNING HEADER ---
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(primary_color)
            self.drawString(54, 750, "DAYTONE MOOD ANALYSER  |  DEVELOPER & TECHNICAL DOCUMENTATION")
            
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(muted_color)
            self.drawRightString(558, 750, "Architecture, Models & Deployment Specifications")
            
            # Header Line
            self.setStrokeColor(border_color)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # --- RUNNING FOOTER ---
            self.setFont("Helvetica", 8)
            self.setFillColor(muted_color)
            self.drawString(54, 40, "Confidential  •  DayTone Dev Docs  •  GDPR & SOC-2 Hardened")
            self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
            
            # Footer Line
            self.line(54, 50, 558, 50)
            
            self.restoreState()

def build_pdf():
    # Setup document path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(base_dir, "technical_documentation.pdf")
    
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
    c_primary = colors.HexColor("#0F766E")    # Teal Accent
    c_secondary = colors.HexColor("#1E293B")  # Deep Slate Dark
    c_dark = colors.HexColor("#1F2937")       # Charcoal Body Text
    c_muted = colors.HexColor("#4B5563")      # Soft Gray Text
    c_bg_light = colors.HexColor("#F8FAFC")   # Soft Slate background
    c_code_bg = colors.HexColor("#0F172A")    # Code block dark background
    c_code_text = colors.HexColor("#38BDF8")  # Code block cyan text
    
    # Custom Paragraph Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=c_secondary,
        spaceAfter=15
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
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
        fontSize=16,
        leading=20,
        textColor=c_secondary,
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        textColor=c_dark,
        spaceAfter=6
    )
    
    style_body_justify = ParagraphStyle(
        'BodyDarkJustify',
        parent=style_body,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    style_bullet_item = ParagraphStyle(
        'BulletItem',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    style_table_header = ParagraphStyle(
        'TableHeaderText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
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
    
    style_code_block = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=c_code_text,
        spaceAfter=8,
        leftIndent=10
    )

    story = []
    
    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 100))
    
    # Accent Banner
    story.append(HRFlowable(width="100%", thickness=4, color=c_primary, spaceBefore=0, spaceAfter=20))
    
    # Title
    story.append(Paragraph("DAYTONE MOOD ANALYSER", style_cover_title))
    story.append(Paragraph("DEVELOPER & TECHNICAL DOCUMENTATION", style_cover_subtitle))
    
    story.append(HRFlowable(width="30%", thickness=1, color=c_secondary, spaceBefore=0, spaceAfter=40, hAlign='CENTER'))
    
    # Executive Summary Box
    summary_text = (
        "<b>System Overview:</b> DayTone is a self-hosted, GDPR-compliant Flask web "
        "application designed for personal mood tracking, local sentiment analysis, and machine "
        "learning-based burnout prediction. The platform leverages local NLP models (NLTK VADER/DistilBERT) "
        "and on-device machine learning classifiers to predict burnout risk across 12 unique physiological "
        "and behavioral features. This technical specification documents the software architecture, database "
        "schemas, ML pipeline dynamics, security configurations, and operations guide."
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
    
    story.append(Spacer(1, 120))
    
    # Metadata Block
    meta_data = [
        [Paragraph("Document Type:", style_cover_meta_label), Paragraph("System Architecture & Specifications", style_cover_meta_val)],
        [Paragraph("Project Version:", style_cover_meta_label), Paragraph("1.0.0", style_cover_meta_val)],
        [Paragraph("Deployment Platform:", style_cover_meta_label), Paragraph("Render Cloud Infrastructure (Private Redis + PostgreSQL)", style_cover_meta_val)],
        [Paragraph("Developer Contact:", style_cover_meta_label), Paragraph("MCA Semester 3 Mini Project Team", style_cover_meta_val)],
    ]
    
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(meta_table)
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("1. System Architecture", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "DayTone follows a modular, layered architectural design with distinct presentation, business logic, "
        "and data access boundaries. It is designed to work fully locally for development and automatically "
        "scale to a containerized service stack in production.",
        style_body_justify
    ))
    
    story.append(Paragraph("A. Presentation Layer", style_h2))
    story.append(Paragraph(
        "Responsible for handling client-side interactions, assets loading, and visuals:",
        style_body
    ))
    story.append(Paragraph("• <b>User Interface</b>: Responsive HTML5/CSS3 templates styled with a dark theme, integrated CSS grids, and mobile-responsive viewport bindings.", style_bullet_item))
    story.append(Paragraph("• <b>WebGL Shaders (Orb)</b>: A customized Three.js implementation that deforms a 3D sphere vertex mesh dynamically based on the user's daily metrics (mood, sleep, stress) using simplex noise equations.", style_bullet_item))
    story.append(Paragraph("• <b>Visual Charts</b>: Interactive dashboard graphics rendered client-side via Chart.js, visualizing history and goal milestones.", style_bullet_item))
    story.append(Paragraph("• <b>PWA Offline Caching</b>: A standard Service Worker (<code>sw.js</code>) intercepts fetch requests and handles caching for offline app execution.", style_bullet_item))
    
    story.append(Paragraph("B. Business Logic Layer (Flask Core)", style_h2))
    story.append(Paragraph(
        "The core Flask application manages authentication, data sanitization, logging schedules, and analytical workflows:",
        style_body
    ))
    story.append(Paragraph("• <b>Blueprints</b>: Modular application structures mapping to distinct areas: Auth (users/GDPR), Mood (check-ins/charts/exports), and Admin (auditing/user management).", style_bullet_item))
    story.append(Paragraph("• <b>Local NLP engine</b>: Textual analyses run directly in app memory using NLTK VADER or DistilBERT models, preventing external data leaks.", style_bullet_item))
    story.append(Paragraph("• <b>ML Classifier Pipeline</b>: Scikit-learn predictor loading trained decision tree weights and classifying daily inputs into burnout risk categories.", style_bullet_item))
    
    story.append(Paragraph("C. Data & Infrastructure Layer", style_h2))
    story.append(Paragraph(
        "Manages storage state, cache stores, and container operations:",
        style_body
    ))
    story.append(Paragraph("• <b>Relational DB</b>: Dual-target storage schema supporting SQLite (development) and PostgreSQL (production) accessed via SQLAlchemy.", style_bullet_item))
    story.append(Paragraph("• <b>Cache & Limit Store</b>: Private Redis instance used as a session cache and rate limit registry (Flask-Limiter).", style_bullet_item))
    story.append(Paragraph("• <b>Encryption Engine</b>: AES-256 Fernet symmetric encryption layers that secure sensitive text column inputs at rest.", style_bullet_item))
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 3: DATABASE SCHEMA SPECIFICATIONS
    # =========================================================================
    story.append(Paragraph("2. Database Models & Schema Design", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "DayTone employs a highly relational database architecture. Below is the specification breakdown "
        "of the core models defined in <code>app/models.py</code>:",
        style_body_justify
    ))
    
    db_table_data = [
        [
            Paragraph("Model Name", style_table_header),
            Paragraph("Core Fields", style_table_header),
            Paragraph("Purpose & Relational Constraints", style_table_header)
        ],
        [
            Paragraph("<b>User</b>", style_table_cell_bold),
            Paragraph("id, name, email, password_hash, role, organization_id, deleted_at", style_table_cell),
            Paragraph("Core account data. Integrates soft-deletes (deleted_at). Relates to UserProfile, MoodLog, and Goal via cascading deletes.", style_table_cell)
        ],
        [
            Paragraph("<b>UserProfile</b>", style_table_cell_bold),
            Paragraph("id, user_id, age, gender, preferred_activity, calm_mode, predict_burnout", style_table_cell),
            Paragraph("User preferences. <code>calm_mode</code> disables WebGL deformations for accessibility. One-to-one mapping with User.", style_table_cell)
        ],
        [
            Paragraph("<b>MoodLog</b>", style_table_cell_bold),
            Paragraph("id, user_id, log_date, mood_score, sleep_hours, stress_level, social_interaction, notes, sentiment_score, burnout_risk, deleted_at", style_table_cell),
            Paragraph("Stores daily check-ins. <code>notes</code> are AES-encrypted at rest. Sentiment and burnout features are calculated upon save.", style_table_cell)
        ],
        [
            Paragraph("<b>BurnoutHistory</b>", style_table_cell_bold),
            Paragraph("id, user_id, log_id, prediction, confidence, algorithm_used, predicted_at, is_accurate", style_table_cell),
            Paragraph("Operational model tracking predictor performance and audit logs. Captures user feedback on accuracy.", style_table_cell)
        ],
        [
            Paragraph("<b>Goal</b>", style_table_cell_bold),
            Paragraph("id, user_id, target_type, target_value, start_date, end_date, completed", style_table_cell),
            Paragraph("Tracks personal sleep, mood, or activity metrics. Supports dashboard progress visualizations.", style_table_cell)
        ],
        [
            Paragraph("<b>AuditLog</b>", style_table_cell_bold),
            Paragraph("id, admin_id, action, target_type, target_id, detail, ip_address, performed_at", style_table_cell),
            Paragraph("Admin activity log for SOC-2 accountability, mapping critical actions like role toggles and user soft-deletes.", style_table_cell)
        ],
        [
            Paragraph("<b>Organization</b>", style_table_cell_bold),
            Paragraph("id, name, invite_code", style_table_cell),
            Paragraph("Multi-tenancy grouping. Users joining an organization share metadata boundaries.", style_table_cell)
        ]
    ]
    
    db_table = Table(db_table_data, colWidths=[90, 164, 250])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(db_table)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("A. Cryptographic Column Security (Notes Field)", style_h2))
    story.append(Paragraph(
        "DayTone does not store raw journals in plaintext. The database field <code>_notes_encrypted</code> "
        "is mapped via a custom SQLAlchemy hybrid property. Writing to <code>log.notes</code> encrypts the "
        "text automatically using AES-256 (via the cryptography Fernet module) with the <code>ENCRYPTION_KEY</code> "
        "environment variable. Decryption occurs only in app memory when reading from the getter.",
        style_body_justify
    ))
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 4: NLP AND ML PIPELINES
    # =========================================================================
    story.append(Paragraph("3. Local NLP & Machine Learning Pipelines", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("A. Local Natural Language Processing (NLP)", style_h2))
    story.append(Paragraph(
        "Journal notes undergo localized sentiment parsing to extract emotional cues without compromising privacy:",
        style_body_justify
    ))
    story.append(Paragraph("• <b>NLTK VADER</b>: Utilized by default. It processes word-level emotional polarization vectors, calculating a normalized compound sentiment score.", style_bullet_item))
    story.append(Paragraph("• <b>DistilBERT (Optional Transformer)</b>: If the application detects the <code>transformers</code> library and sufficient memory, it attempts to load a lightweight <code>distilbert-base-uncased-finetuned-sst-2-english</code> model. The resulting classifier outputs are scaled to compile sentiment compound scores.", style_bullet_item))
    story.append(Paragraph("• <b>Degraded Execution Mode</b>: If both engines fail to load, the system degrades to output a neutral 0.0 sentiment score, maintaining application availability.", style_bullet_item))
    
    story.append(Paragraph("B. Burnout Predictor Feature Matrix", style_h2))
    story.append(Paragraph(
        "The Machine Learning classifier evaluates 12 distinct mathematical features compiled at check-in time:",
        style_body
    ))
    
    features_data = [
        [Paragraph("Feature Name", style_table_header), Paragraph("Data Type", style_table_header), Paragraph("Derivation / Source", style_table_header)],
        [Paragraph("<code>mood_score</code>", style_table_cell), Paragraph("Integer (1-5)", style_table_cell), Paragraph("User daily mood check-in selection.", style_table_cell)],
        [Paragraph("<code>sleep_hours</code>", style_table_cell), Paragraph("Float", style_table_cell), Paragraph("User sleep duration input.", style_table_cell)],
        [Paragraph("<code>stress_level</code>", style_table_cell), Paragraph("Integer (1-5)", style_table_cell), Paragraph("User daily stress rating input.", style_table_cell)],
        [Paragraph("<code>activity_done</code>", style_table_cell), Paragraph("Integer (0/1)", style_table_cell), Paragraph("Boolean check for daily exercise.", style_table_cell)],
        [Paragraph("<code>social_interaction</code>", style_table_cell), Paragraph("Integer (1-3)", style_table_cell), Paragraph("Low, Medium, or High social activity.", style_table_cell)],
        [Paragraph("<code>sentiment_score</code>", style_table_cell), Paragraph("Float (-1 to 1)", style_table_cell), Paragraph("VADER sentiment score from journal notes.", style_table_cell)],
        [Paragraph("<code>avg_mood_7d</code>", style_table_cell), Paragraph("Float", style_table_cell), Paragraph("Rolling 7-day average of user's mood scores.", style_table_cell)],
        [Paragraph("<code>avg_stress_7d</code>", style_table_cell), Paragraph("Float", style_table_cell), Paragraph("Rolling 7-day average of stress inputs.", style_table_cell)],
        [Paragraph("<code>avg_sleep_7d</code>", style_table_cell), Paragraph("Float", style_table_cell), Paragraph("Rolling 7-day average of sleep hours.", style_table_cell)],
        [Paragraph("<code>consecutive_bad_days</code>", style_table_cell), Paragraph("Integer", style_table_cell), Paragraph("Count of consecutive days with mood score ≤ 2.", style_table_cell)],
        [Paragraph("<code>mood_variability</code>", style_table_cell), Paragraph("Float", style_table_cell), Paragraph("Standard deviation of mood scores over 7 days.", style_table_cell)],
        [Paragraph("<code>is_weekend</code>", style_table_cell), Paragraph("Integer (0/1)", style_table_cell), Paragraph("1 if log date is Saturday/Sunday, else 0.", style_table_cell)]
    ]
    
    feat_table = Table(features_data, colWidths=[154, 80, 270])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(feat_table)
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("C. Model Operations & Retraining (MLOps)", style_h2))
    story.append(Paragraph(
        "DayTone includes scripts to automate the data pipeline: "
        "<code>scripts/export_db_to_training.py</code> compiles historical database records into "
        "training matrices. The training script (<code>train.py</code>) fits models (Decision Tree, Logistic Regression, "
        "Random Forest), validates accuracy, and outputs a <code>model.pkl</code> payload containing the model weights "
        "and metadata. Drift checks (KS-test) and bias audits evaluate operational metrics on the Admin page.",
        style_body_justify
    ))
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 5: SECURITY, PWA, AND ACCESSIBILITY
    # =========================================================================
    story.append(Paragraph("4. Security, PWA, & Accessibility Specifications", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("A. Security Controls & GDPR Hardening", style_h2))
    story.append(Paragraph(
        "DayTone implements key application security and compliance standards:",
        style_body_justify
    ))
    story.append(Paragraph("• <b>HTTP Security Headers</b>: Talisman enforces strict content security policies (CSP) including <code>frame-ancestors 'self'</code> and <code>form-action 'self'</code>. In production, sessions rely on secure, HTTP-only cookies (<code>SESSION_COOKIE_SECURE=True</code>).", style_bullet_item))
    story.append(Paragraph("• <b>Brute-Force Protection</b>: Auth views are protected via <code>flask-limiter</code>. In production, limits are stored in a private Redis cache using token bucket algorithms.", style_bullet_item))
    story.append(Paragraph("• <b>Admin Tokenization</b>: Direct registrations are disabled. Admins generate cryptographically secure database-backed invite tokens to register other staff, avoiding configuration credentials.", style_bullet_item))
    story.append(Paragraph("• <b>Right to Be Forgotten</b>: Account purge functions wipe profiles and related DB entries instantly.", style_bullet_item))
    story.append(Paragraph("• <b>Crisis Resource Reveal Shield</b>: If a High burnout risk is predicted, emergency lifelines are rendered on the UI, covered by an opt-in reveal shield to prevent immediate user anxiety.", style_bullet_item))
    
    story.append(Paragraph("B. Progressive Web App (PWA) Dynamics", style_h2))
    story.append(Paragraph(
        "DayTone operates as a modern Progressive Web App (PWA):",
        style_body_justify
    ))
    story.append(Paragraph("• <b>Service Worker caching</b>: The application installs <code>sw.js</code>. The worker cache stores assets locally. If the user loses connectivity, they receive cached views and a graceful <code>offline.html</code> fallback page.", style_bullet_item))
    story.append(Paragraph("• <b>Cross-Tab Broadcast Sync</b>: Utilizes the browser's <code>BroadcastChannel</code>. When a user submits a log in one tab, the update broadcasts to other open tabs, triggering a toast alert.", style_bullet_item))
    story.append(Paragraph("• <b>Query Caching</b>: Frequently accessed endpoints (such as goals lists and daily heatmaps) are cached via Flask-Caching, with automatic cache invalidation upon check-in updates.", style_bullet_item))
    
    story.append(Paragraph("C. Accessibility & Motion Controls (WCAG 2.1)", style_h2))
    story.append(Paragraph(
        "The dashboard includes accessibility features to support diverse user needs:",
        style_body_justify
    ))
    story.append(Paragraph("• <b>Calm Mode</b>: A profile setting that disables WebGL vertex simplex deformations on the 3D Orb and stops Chart.js animation loops, supporting users with motion sensitivities.", style_bullet_item))
    story.append(Paragraph("• <b>A11y Landmarks</b>: Implements standard skip-to-content links, clear tab-focus rings, layout landmarks (<code>&lt;main&gt;</code>, <code>&lt;header&gt;</code>, <code>&lt;footer&gt;</code>), and explicit aria-live regions.", style_bullet_item))
    
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 6: OPERATIONS AND DEVELOPMENT WORKFLOW
    # =========================================================================
    story.append(Paragraph("5. Operations & Developer Workflows", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("A. Local Development Setup", style_h2))
    story.append(Paragraph(
        "To configure a local developer environment, execute the following commands in order:",
        style_body_justify
    ))
    
    setup_code = (
        "# 1. Initialize environment and dependencies\n"
        "python3 -m venv .venv\n"
        "source .venv/bin/activate\n"
        "pip install -r requirements.txt -r requirements-dev.txt\n\n"
        "# 2. Configure environment settings\n"
        "cp .env.example .env\n"
        "# Open .env and set SECRET_KEY, ENCRYPTION_KEY, etc.\n\n"
        "# 3. Run database migrations\n"
        "flask db upgrade\n\n"
        "# 4. Generate training baseline data & train model\n"
        "python -m app.ml.generate_data\n"
        "python -m app.ml.train\n\n"
        "# 5. Run local development server\n"
        "python run.py"
    )
    story.append(Table([[Paragraph(setup_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 10),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("B. Test Execution & Analysis", style_h2))
    story.append(Paragraph(
        "To verify application features, execute styling validation and unit tests:",
        style_body_justify
    ))
    
    test_code = (
        "# Run the PyTest automation suite\n"
        "pytest -v\n\n"
        "# Verify PEP-8 coding compliance\n"
        "flake8 app/\n\n"
        "# Run metrics drift diagnostics\n"
        "python scripts/monitor_drift.py\n\n"
        "# Run model bias audits\n"
        "python scripts/bias_audit.py"
    )
    story.append(Table([[Paragraph(test_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code_block)]], 
                       colWidths=[504], 
                       style=TableStyle([
                           ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                           ('PADDING', (0,0), (-1,-1), 10),
                           ('BOX', (0,0), (-1,-1), 0.5, c_primary),
                       ])))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("C. Production Deployment (Render Blueprint)", style_h2))
    story.append(Paragraph(
        "Production deployments utilize the IaC configuration in <code>render.yaml</code>. "
        "The build command runs <code>flask db upgrade</code>, while the start command runs a gunicorn cluster: "
        "<code>gunicorn \"app:create_app()\" --workers 2 --threads 2 --bind 0.0.0.0:$PORT --preload</code>. "
        "A private Redis cluster stores sessions and rate limit logs within Render's internal subnet.",
        style_body_justify
    ))
    
    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Technical Document PDF generated successfully at: {pdf_path}")

if __name__ == '__main__':
    build_pdf()
