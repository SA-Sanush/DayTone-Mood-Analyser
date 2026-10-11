from pathlib import Path
from math import atan2, cos, sin, pi

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, Frame, Paragraph, Table, TableStyle

OUT = Path('/home/crystal/Desktop/DayTone/DayTone_SA_Sanush_College_Report.pdf')
W, H = A4
LEFT, RIGHT = 2.1 * cm, 2.1 * cm
TOP, BOTTOM = 2.2 * cm, 2.1 * cm
CONTENT_W = W - LEFT - RIGHT
TITLE = 'DAYTONE - AI MENTAL WELLNESS TRACKER AND BURNOUT PREDICTION'
SHORT = 'DAYTONE - AI MENTAL WELLNESS TRACKER'
STUDENT = 'S A SANUSH'
REGNO = 'REGISTER NO: __________________'
DEPT = 'DEPARTMENT OF COMPUTER APPLICATIONS'
COLLEGE = 'LOURDES MATHA COLLEGE OF SCIENCE AND TECHNOLOGY'
PLACE = 'KUTTICHAL, THIRUVANANTHAPURAM - 695574'
UNIV = 'APJ ABDUL KALAM TECHNOLOGICAL UNIVERSITY, KERALA'
GUIDE = 'Ms. ASHA CHANDRAN S'
HOD = 'Ms. BISMI K CHARLEYS'
YEAR = '2025 - 2026'
SCREENSHOT_DIR = Path('/home/crystal/Pictures/Screenshots')
SCREENSHOTS = [
    ('Screenshot From 2026-09-06 11-18-27.png', 'Login screen with DayTone welcome panel and sign-in form'),
    ('Screenshot From 2026-09-06 11-18-42.png', 'Registration screen for creating a DayTone account'),
    ('Screenshot From 2026-09-06 11-19-22.png', 'User dashboard showing current mood, burnout risk and daily status'),
    ('Screenshot From 2026-09-06 11-19-46.png', 'Dashboard wellness cards, coach signal and achievement badges'),
    ('Screenshot From 2026-09-06 11-19-59.png', 'Analytics and trends section with mood, sleep, stress and suggestions'),
    ('Screenshot From 2026-09-06 11-20-15.png', 'Daily check-in form for mood, sleep, stress, activity and notes'),
    ('Screenshot From 2026-09-06 11-20-25.png', 'History screen with search, filters and export options'),
    ('Screenshot From 2026-09-06 11-20-33.png', 'Mood heatmap showing yearly mood activity and legend'),
    ('Screenshot From 2026-09-06 11-20-41.png', 'Wellness goals page with active goal progress'),
    ('Screenshot From 2026-09-06 11-21-39.png', 'Profile and preference settings for the logged-in user'),
    ('Screenshot From 2026-09-06 11-22-02.png', 'Admin dashboard with platform analytics and risk distribution'),
    ('Screenshot From 2026-09-06 11-22-10.png', 'User management page with role and account controls'),
    ('Screenshot From 2026-09-06 11-22-22.png', 'ML and AI diagnostics page with model comparison and metrics'),
    ('Screenshot From 2026-09-06 11-22-33.png', 'Bias and fairness audit output for the prediction model'),
    ('Screenshot From 2026-09-06 11-22-40.png', 'Admin audit log showing recorded administrative actions'),
    ('Screenshot From 2026-09-06 11-22-54.png', 'Admin invite token management screen'),
    ('Screenshot From 2026-09-06 11-23-13.png', 'Developer command center with protected system controls'),
    ('Screenshot From 2026-09-06 11-23-22.png', 'Developer dashboard with infrastructure and role management sections'),
]

REFERENCE_REPORT = Path('/home/crystal/Downloads/safesurf (1).pdf')
FONT_REGULAR = 'Times-Roman'
FONT_BOLD = 'Times-Bold'
FONT_ITALIC = 'Times-Italic'


def register_reference_fonts():
    global FONT_REGULAR, FONT_BOLD, FONT_ITALIC
    if not REFERENCE_REPORT.exists():
        return
    try:
        import pymupdf
    except Exception:
        return

    wanted = {
        'TimesNewRomanPSMT': 'SafeSurfTimes',
        'TimesNewRomanPS-BoldMT': 'SafeSurfTimesBold',
        'TimesNewRomanPS-ItalicMT': 'SafeSurfTimesItalic',
    }
    found = {}
    doc = pymupdf.open(str(REFERENCE_REPORT))
    for page_index in range(doc.page_count):
        for xref, ext, _, base_font, *_ in doc.get_page_fonts(page_index, full=True):
            clean_name = base_font.split('+')[-1]
            if clean_name not in wanted or clean_name in found:
                continue
            _, extracted_ext, _, data = doc.extract_font(xref)
            if not data:
                continue
            suffix = extracted_ext or ext or 'ttf'
            font_path = Path('/tmp') / f'daytone_{wanted[clean_name]}.{suffix}'
            font_path.write_bytes(data)
            pdfmetrics.registerFont(TTFont(wanted[clean_name], str(font_path)))
            found[clean_name] = wanted[clean_name]
        if len(found) == len(wanted):
            break

    FONT_REGULAR = found.get('TimesNewRomanPSMT', FONT_REGULAR)
    FONT_BOLD = found.get('TimesNewRomanPS-BoldMT', FONT_BOLD)
    FONT_ITALIC = found.get('TimesNewRomanPS-ItalicMT', FONT_ITALIC)


register_reference_fonts()

styles = {
    'cover_title': ParagraphStyle('cover_title', fontName='Times-Bold', fontSize=18, leading=24, alignment=TA_CENTER),
    'cover': ParagraphStyle('cover', fontName='Times-Bold', fontSize=13, leading=19, alignment=TA_CENTER),
    'normal': ParagraphStyle('normal', fontName='Times-Roman', fontSize=11.2, leading=16.6, alignment=TA_JUSTIFY, spaceAfter=7),
    'normal_tight': ParagraphStyle('normal_tight', fontName='Times-Roman', fontSize=10.8, leading=15.7, alignment=TA_JUSTIFY, spaceAfter=5),
    'center': ParagraphStyle('center', fontName='Times-Roman', fontSize=11, leading=16, alignment=TA_CENTER),
    'right': ParagraphStyle('right', fontName='Times-Roman', fontSize=11, leading=16, alignment=TA_RIGHT),
    'bold_center': ParagraphStyle('bold_center', fontName='Times-Bold', fontSize=12, leading=18, alignment=TA_CENTER),
    'chapter': ParagraphStyle('chapter', fontName='Times-Bold', fontSize=18, leading=27, alignment=TA_CENTER, spaceAfter=16),
    'h1': ParagraphStyle('h1', fontName='Times-Bold', fontSize=13, leading=18, alignment=TA_LEFT, spaceBefore=4, spaceAfter=6),
    'bullet': ParagraphStyle('bullet', fontName='Times-Roman', fontSize=10.2, leading=14.2, leftIndent=16, firstLineIndent=-9, alignment=TA_JUSTIFY, spaceAfter=3),
    'caption': ParagraphStyle('caption', fontName='Times-Italic', fontSize=9, leading=12, alignment=TA_CENTER),
    'table': ParagraphStyle('table', fontName='Times-Roman', fontSize=9.2, leading=12, alignment=TA_LEFT),
    'table_b': ParagraphStyle('table_b', fontName='Times-Bold', fontSize=9.2, leading=12, alignment=TA_LEFT),
    'report_normal': ParagraphStyle('report_normal', fontName=FONT_REGULAR, fontSize=12, leading=20.7, alignment=TA_JUSTIFY, spaceAfter=7),
    'report_normal_tight': ParagraphStyle('report_normal_tight', fontName=FONT_REGULAR, fontSize=12, leading=20.7, alignment=TA_JUSTIFY, spaceAfter=5),
    'report_chapter': ParagraphStyle('report_chapter', fontName=FONT_BOLD, fontSize=18, leading=27, alignment=TA_CENTER, spaceAfter=16, keepWithNext=1),
    'report_h1': ParagraphStyle('report_h1', fontName=FONT_BOLD, fontSize=14, leading=19, alignment=TA_LEFT, spaceBefore=4, spaceAfter=6, keepWithNext=1),
    'report_bullet': ParagraphStyle('report_bullet', fontName=FONT_REGULAR, fontSize=12, leading=20.7, leftIndent=16, firstLineIndent=-9, alignment=TA_JUSTIFY, spaceAfter=3),
    'report_caption': ParagraphStyle('report_caption', fontName=FONT_REGULAR, fontSize=12, leading=15, alignment=TA_CENTER),
    'report_table': ParagraphStyle('report_table', fontName=FONT_REGULAR, fontSize=12, leading=15, alignment=TA_LEFT),
    'report_table_b': ParagraphStyle('report_table_b', fontName=FONT_BOLD, fontSize=12, leading=15, alignment=TA_LEFT),
    'screenshot_caption': ParagraphStyle('screenshot_caption', fontName='Times-Italic', fontSize=12, leading=15, alignment=TA_CENTER),
}


def P(text, style='normal'):
    return Paragraph(text, styles[style])


def draw_page_border(c):
    c.setLineWidth(0.45)
    c.rect(0.38 * cm, 0.38 * cm, W - 0.76 * cm, H - 0.76 * cm)


def draw_header_footer(c, printed_page=None):
    if printed_page is None:
        return
    c.setFont(FONT_REGULAR, 12)
    c.drawString(LEFT, H - 1.55 * cm, SHORT + ' AND BURNOUT PREDICTION')
    c.drawCentredString(W / 2, 1.05 * cm, str(printed_page))
    c.drawString(LEFT, 1.45 * cm, 'Department of Computer Applications, LMCST')


def flow(c, items, y_top=None, y_bottom=None):
    y_top = y_top or H - TOP
    y_bottom = y_bottom or BOTTOM
    frame = Frame(LEFT, y_bottom, CONTENT_W, y_top - y_bottom, showBoundary=0)
    frame.addFromList(items, c)


def page(c, items, printed_page=None):
    draw_header_footer(c, printed_page)
    flow(c, items, H - 3.15 * cm if printed_page else H - TOP, 2.15 * cm if printed_page else BOTTOM)
    c.showPage()


def make_table(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.45, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def title_page(c):
    items = [
        P('MINI-PROJECT REPORT', 'cover'),
        P('<br/>' + SHORT, 'cover_title'),
        P('AND BURNOUT PREDICTION', 'cover_title'),
        P('<br/>Submitted By:', 'center'),
        P(STUDENT, 'cover'),
        P(REGNO, 'center'),
        P('<br/><br/><br/><br/><br/><br/><br/><br/>' + DEPT, 'cover'),
        P(COLLEGE, 'cover'),
        P(PLACE, 'cover'),
        P('(AFFILIATED TO APJ ABDUL KALAM TECHNOLOGICAL UNIVERSITY, KERALA (KTU))', 'cover'),
        P('(MANAGED BY ARCHDIOCESE OF CHANGANASSERY)', 'cover')]
    flow(c, items, H - 1.2 * cm, 1.8 * cm)
    c.showPage()


def project_title_page(c):
    items = [
        P(SHORT, 'cover_title'),
        P('AND BURNOUT PREDICTION', 'cover_title'),
        P('<br/>A Project Report', 'cover'),
        P('Submitted By,', 'center'),
        P(STUDENT + ' - ' + REGNO.replace('REGISTER NO:', '').strip(), 'cover'),
        P('in partial fulfilment of the requirements for the award of', 'center'),
        P('the degree in', 'center'),
        P('MASTER OF COMPUTER APPLICATIONS', 'cover'),
        P('at', 'center'),
        P('<br/><br/><br/><br/>' + DEPT, 'cover'),
        P(COLLEGE, 'cover'),
        P(PLACE, 'cover'),
        P('(AFFILIATED TO APJ ABDUL KALAM TECHNOLOGICAL UNIVERSITY, KERALA)', 'cover'),
        P('OCTOBER 2025', 'cover'),
    ]
    flow(c, items, H - 1.2 * cm, 1.8 * cm)
    c.showPage()


def certificate(c):
    items = [P(COLLEGE, 'cover'), P(PLACE, 'cover'), P('(Affiliated to APJ Abdul Kalam Technological University, Kerala)', 'center'), P(DEPT, 'cover'), P('<br/><br/>CERTIFICATE', 'chapter'),
             P('This is to certify that the project work entitled <b>"' + TITLE + '"</b> is a Bonafide record of the work done by <b>' + STUDENT + '</b>, Reg No: ' + REGNO.replace('REGISTER NO:', '').strip() + ', student of Department of Computer Applications, Lourdes Matha College of Science and Technology, Kuttichal, Thiruvananthapuram, affiliated to the APJ Abdul Kalam Technological University, Kerala from July 2025 to October 2025 in partial fulfilment of the requirements for the award of the Degree of Master of Computer Applications from APJ Abdul Kalam Technological University, Kerala.', 'normal')]
    flow(c, items, H - 1.5 * cm, 7.2 * cm)
    t = Table([[P(GUIDE, 'bold_center'), P('Date:', 'right')], [P('(Internal Guide)', 'center'), P('', 'center')], [P('', 'center'), P(HOD, 'bold_center')], [P('', 'center'), P('(Head of the Department)', 'center')]], colWidths=[7.5 * cm, 7.5 * cm])
    t.wrapOn(c, CONTENT_W, 3 * cm)
    t.drawOn(c, LEFT, 4.5 * cm)
    c.showPage()


def declaration(c):
    items = [P('DECLARATION', 'chapter'),
             P('I undersigned hereby declare that the project report <b>"' + TITLE + '"</b> submitted for partial fulfilment of the requirements for the award of degree of Master of Computer Applications of the APJ Abdul Kalam Technological University, Kerala. This submission represents my idea in my own words and I have adequately and accurately cited and referenced the original sources.', 'normal'),
             P('I also declare that I have adhered to ethics of academic honesty and integrity and have not misrepresented or fabricated any data or idea or fact of source in my submission. I understand that any violation of the above will be a cause for disciplinary action by the institute and/or the university.', 'normal'),
             P('<br/><br/><br/><br/><br/><br/>Place: TRIVANDRUM&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + STUDENT + '<br/>Date:', 'normal')]
    flow(c, items)
    c.showPage()


def acknowledgement(c):
    paras = [
        'An endeavour over a long time can be successful only with the advice, encouragement, and support of many well-wishers. I place on record my sincere gratitude to all those who directly or indirectly contributed to the successful completion of this project work.',
        'At the outset, I thank God Almighty for the strength, guidance, and blessings received throughout the period of this Master of Computer Applications project.',
        'It is a great pleasure to express my sincere gratitude to the Director and Principal of Lourdes Matha College of Science and Technology for permitting me to do this project with full support and encouragement.',
        'I am highly obliged to ' + HOD + ', Head of the Department of Computer Applications of Lourdes Matha College of Science and Technology, for being a source of inspiration throughout the course and for valuable guidance.',
        'With heartfelt thanks, I take this opportunity to thank my internal guide ' + GUIDE + ', Assistant Professor, and all staff members of the Department of Computer Applications for their continuous support, encouragement, and suggestions in various stages of the development of this project.',
        'I also express my sincere gratitude to open-source communities whose tools and documentation helped in completing the DayTone project. Finally, I thank my friends and family who directly or indirectly contributed to this venture.'
    ]
    items = [P('ACKNOWLEDGEMENT', 'chapter')] + [P(x, 'normal') for x in paras] + [P('<br/>' + STUDENT, 'right')]
    flow(c, items)
    c.showPage()


def base_paragraph(topic):
    return ('DayTone is designed with emphasis on privacy, usability, maintainability, and academic clarity. '
            'The implementation uses modular Flask blueprints, SQLAlchemy models, local NLP processing, and Scikit-learn prediction so that the system can be explained, tested, and improved in a structured way. '
            'The design also considers practical deployment requirements such as migrations, secure configuration, logging, data export, and administrator monitoring. ')



def expansion_for(key):
    clean = key.replace(' / ', ' and ').replace('-', ' ').title()
    return [
        f'In DayTone, {clean} is treated as a practical part of the complete wellness tracking workflow. The project does not present this topic only as a theoretical concept; it connects the topic with actual screens, database records, backend routes, model outputs, and user decisions. This makes the report useful for explaining how the application works internally and how each module contributes to the final user experience.',
        'The implementation follows a privacy-aware design approach. User wellness data may include personal habits, emotional reflections, stress values, and sleep patterns, so every major module is planned with confidentiality and controlled access in mind. Authentication, role-based pages, optional encryption, CSRF protection, and audit records support this requirement throughout the application.',
        'From a software engineering perspective, the topic is implemented using modular Flask blueprints and reusable helper utilities. This makes the project easier to test and maintain because authentication, mood logging, administration, prediction, reports, mail, suggestions, and analytics are kept in separate areas of the codebase. A modular structure also makes future enhancement possible without rewriting the entire system.',
        'From the user perspective, the topic is important because DayTone must remain simple and understandable. The system converts technical analysis into visible outputs such as dashboard cards, charts, heatmaps, risk labels, suggestions, history tables, and downloadable reports. The user is not expected to understand machine learning internals in order to benefit from the result.',
        'From the academic perspective, the topic demonstrates how web development, database management, data visualization, natural language processing, machine learning, security, and documentation can be combined into a single MCA project. It also shows awareness of limitations, especially the fact that the burnout model is trained on synthetic and semi-real validation data and is not a clinical diagnostic system.'
    ]


def chapter_overview(title):
    items = [
        P(title, 'report_chapter'),
        P('This chapter introduces the related part of the DayTone project and explains its role in the overall system. The discussion is written in the same academic report style as the reference project, but the content is adapted to DayTone, an AI-assisted mental wellness tracker and burnout prediction platform.', 'report_normal'),
        P('The chapter connects theory with implementation. It describes why the topic is required, how it is handled in the application, which technologies are involved, and how the output supports users or administrators. This helps the reader understand the project as a working software system rather than only a list of features.', 'report_normal'),
        P('The project repeatedly focuses on privacy, usability, maintainability, and explainable wellness feedback. Therefore, each chapter explains not only what the application does, but also why that design choice is suitable for a mental wellness tracking system.', 'report_normal'),
    ]
    chapter_fill = [
        'The DayTone project is organised as a complete software solution rather than a single isolated program. It includes user-facing workflows, administrator workflows, machine learning components, database persistence, deployment files, testing support, and documentation. This chapter therefore explains the selected topic with reference to the actual modules present in the application.',
        'The discussion also considers the practical conditions under which the project will be used. A wellness application should not be confusing, intrusive, or careless with private records. For this reason, the design favours simple screens, secure handling of sensitive data, local analysis where possible, and clear wording of prediction results.',
        'Each chapter builds toward the same objective: to show how DayTone can help a user observe daily patterns and how the system can be maintained responsibly by developers or administrators. The report connects academic concepts such as requirement analysis, feasibility, design, algorithms, and testing with the implemented Flask application.',
    ]
    for para in expansion_for(title)[:3] + chapter_fill:
        items.append(P(para, 'report_normal_tight'))
    return items

def section_content(key):
    aliases = {
        '2.1 EXISTING SYSTEM': '2.2 EXISTING SYSTEM',
        '2.2 DRAWBACK OF EXISTING SYSTEM': '2.3 DRAWBACKS OF EXISTING SYSTEM',
        '3.3 REQUIREMENT SPECIFICATION': '3.4 REQUIREMENT SPECIFICATIONS',
        '3.4 FEASIBILITY ANALYSIS': '3.5 FEASIBILITY ANALYSIS',
        '3.4.1 TECHNICAL FEASIBILITY': '3.5.1 TECHNICAL FEASIBILITY',
        '3.4.2 OPERATIONAL FEASIBILITY': '3.5.2 OPERATIONAL FEASIBILITY',
        '3.4.3 ECONOMICAL FEASIBILITY': '3.5.3 ECONOMIC FEASIBILITY',
        '3.4.4 BEHAVIORAL FEASIBILITY': '3.5.4 BEHAVIOURAL FEASIBILITY',
    }
    key = aliases.get(key, key)
    data = {
        'ABSTRACT': [
            'DayTone is an AI-assisted mental wellness tracking web application designed to help users record daily mood, sleep, stress, activity, social interaction, and journal reflections. The system applies local Natural Language Processing and Machine Learning to detect emotional patterns, classify burnout risk, and provide meaningful wellness insights while preserving user privacy. ',
            'The application is developed using Python Flask for the backend, SQLAlchemy for database handling, Scikit-learn for burnout prediction, NLTK VADER for sentiment analysis, Bootstrap and Jinja templates for the interface, and Chart.js, D3.js, and Three.js for interactive visualizations. DayTone also includes secure authentication, encrypted journal storage, PDF/CSV export, admin analytics, reminder emails, audit logs, model monitoring, and Progressive Web App support.',
            'By combining daily self-reporting, local text analysis, burnout classification, and visual dashboards, DayTone provides a practical and privacy-conscious platform for early self-awareness and proactive wellness management. The project is intended as an academic wellness-support system and not as a clinical diagnostic tool.'
        ],
        '1.1 GENERAL INTRODUCTION': [
            'Mental wellness has become an important concern among students and professionals because stress, lack of sleep, academic pressure, social isolation, and continuous screen time can gradually lead to burnout. Many people notice these patterns only after the problem becomes severe. A digital wellness tracker can help users observe daily habits, identify negative trends, and take preventive action. ',
            'DayTone records day-to-day wellness data and converts it into understandable insights. Instead of only storing notes, the system evaluates numerical check-in values and journal text to generate sentiment scores, burnout risk levels, dashboard charts, history records, and personal suggestions.',
            'The system focuses on privacy-first implementation. Journal notes can be encrypted at rest, sentiment analysis is performed locally, and users can export or delete their records. These design choices make the project suitable for academic demonstration of ethical software design.'
        ],
        '1.2 GOAL OF THE PROJECT': [
            'The goal of DayTone is to provide a simple, useful, and secure wellness monitoring system that encourages daily self-reflection and early burnout awareness. The system does not replace professional care, but it helps users recognize repeated negative patterns in sleep, stress, activity, mood, and personal reflections. ',
            'The project aims to combine a friendly interface with intelligent analysis. The user should be able to enter a daily log, immediately view the effect of the log in dashboard charts, and understand whether the pattern suggests Low, Medium, or High burnout risk.',
            'Another goal is to show how academic machine learning systems can be implemented responsibly. The report clearly identifies the limits of synthetic training data and treats DayTone as a wellness-awareness platform rather than a clinical decision system.'
        ],
        '2.1 STUDY OF SIMILAR WORKS': [
            'Existing wellness systems include journal applications, habit trackers, meditation tools, and mood diary platforms. These tools are useful for recording personal experiences but often provide limited analysis. Most applications require users to manually interpret their own mood trends and do not provide burnout prediction. ',
            'Research in sentiment analysis shows that text reflections contain useful emotional indicators. Lexicon-based tools such as VADER are lightweight and suitable for real-time local analysis. Machine Learning models such as Decision Tree, Logistic Regression, and Random Forest can classify risk patterns when provided with structured features such as mood, sleep, stress, and rolling averages.',
            'DayTone takes inspiration from these systems but combines multiple features into a single academic prototype: journal analysis, structured daily check-ins, local prediction, visual dashboards, data export, user goals, admin analytics, audit logs, and privacy controls.'
        ],
        '2.2 EXISTING SYSTEM': [
            'The existing method for wellness monitoring is usually manual logging in notebooks, spreadsheets, or basic mobile apps. These systems store user inputs but provide only simple summaries. In many cases, the user must manually compare dates and interpret patterns without support from an intelligent model. ',
            'Some commercial platforms provide analytics, but they often depend on proprietary cloud processing. This can create privacy concerns when the user records sensitive personal reflections. They may also lack transparent explanation of how risk or recommendation scores are generated.',
            'In institutional settings, counsellors or mentors may manually review records. This process is slow and subjective, and it becomes difficult when many users submit daily logs. A structured web application can reduce this burden and make the workflow more consistent.'
        ],
        '2.3 DRAWBACKS OF EXISTING SYSTEM': [
            'Although existing systems support basic logging, they are not sufficient for a privacy-aware intelligent wellness platform. They either lack predictive power, lack security controls, or lack meaningful visual analytics. ',
            'Most diary applications store entries but do not classify burnout risk. Habit trackers may show streaks but do not interpret emotional state. Cloud-based AI tools may process sensitive data outside the user environment. These gaps reduce user trust and limit practical usefulness.',
            'DayTone addresses these drawbacks by combining structured metrics, journal sentiment, rolling seven-day features, ML prediction, encrypted storage, export tools, and dashboards in one system.'
        ],
        '3.1 PROPOSED SYSTEM': [
            'The proposed system, DayTone, is a Flask-based mental wellness tracker that allows registered users to submit daily logs and view personalized analytics. The backend computes sentiment from journal notes, extracts behavioural features, predicts burnout risk, stores history, and generates suggestions. ',
            'The frontend displays charts, heatmaps, risk status, goals, history, and a WebGL mood orb. Administrators can monitor users, audit logs, invite tokens, model feedback, and platform analytics. The system therefore combines user self-care features with administrative tools.',
            'The proposed system also supports privacy and accountability. Passwords are hashed, forms are CSRF-protected, journal notes can be encrypted, and important administrator actions are recorded in audit logs.'
        ],
        '3.2 FEATURES OF PROPOSED SYSTEM': [
            'DayTone combines daily logging, analysis, visualization, security, and export features in one application. The system is modular, so each function is handled by a separate blueprint or utility module. ',
            'Important user features include registration, login, profile settings, daily mood log, dashboard charts, history page, goals, heatmap, PDF report export, and CSV export. These features make the application useful for regular self-monitoring.',
            'Important administrative features include user list, user detail page, audit log, invite tokens, bias audit, developer dashboard, model feedback review, and high-level analytics. These pages help maintain the platform responsibly.'
        ],
        '3.3 FUNCTIONS OF PROPOSED SYSTEM': [
            'The system performs user authentication, daily wellness data collection, sentiment scoring, burnout risk prediction, suggestion generation, visual analytics, history tracking, report generation, and administrator monitoring. ',
            'When a user submits a daily log, the Flask route validates the values, stores the record, analyses the journal note with VADER, creates a feature vector, executes the prediction module, stores the prediction history, and displays updated dashboard values.',
            'For administrators, DayTone supports user search, user detail inspection, audit log review, model feedback monitoring, and bias audit reporting. These functions are important for academic demonstration and future production readiness.'
        ],
        '3.4 REQUIREMENT SPECIFICATIONS': [
            'The requirement specification defines the technologies, data, security controls, and user operations needed for DayTone. The system must be easy enough for daily use and strong enough to protect personal wellness records. ',
            'Frontend requirements include HTML, CSS, Bootstrap, JavaScript, Chart.js, D3.js, and Three.js. Backend requirements include Python Flask, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Limiter, Flask-Mail, SQLAlchemy, Scikit-learn, NLTK VADER, and ReportLab.',
            'The system also requires secure configuration through environment variables, a database for persistent storage, migrations for schema changes, and deployment support through Gunicorn, Docker, Redis, and PostgreSQL when used in production.'
        ],
        '3.5 FEASIBILITY ANALYSIS': [
            'Feasibility analysis studies whether the proposed system can be built, operated, maintained, and accepted by users. DayTone is feasible because it uses open-source tools, a simple interface, lightweight processing, and a modular design. ',
            'The project can be developed and tested on a normal laptop. It can later be deployed using a web service, database, and Redis-backed rate limiting. This makes it suitable for a student project and for future improvement.',
            'The major feasibility aspects considered are technical feasibility, operational feasibility, economic feasibility, and behavioural feasibility.'
        ],
        '3.5.1 TECHNICAL FEASIBILITY': [
            'DayTone is technically feasible because the backend is implemented with Flask blueprints and standard Python packages for authentication, forms, migrations, mail, reporting, and machine learning [1], [2].',
            'The prediction workflow uses Scikit-learn models and a saved pipeline, while journal sentiment is processed locally with VADER so the application can demonstrate intelligent behaviour without depending on remote clinical services [4], [5].'
        ],
        '3.5.2 OPERATIONAL FEASIBILITY': [
            'The system is operationally feasible because the user workflow is simple: register, log daily wellness values, review the dashboard, and export history when needed.',
            'Administrators have separate pages for user management, audit review, invite tokens, model feedback, and bias checks, so routine platform monitoring can be handled without direct database access.'
        ],
        '3.5.3 ECONOMIC FEASIBILITY': [
            'DayTone is economically feasible because it is built mainly with open-source frameworks and can run with SQLite during development.',
            'For deployment, the same codebase can be moved to PostgreSQL, Redis, Gunicorn, and Docker without changing the core application design, keeping infrastructure cost flexible for an academic prototype.'
        ],
        '3.5.4 BEHAVIOURAL FEASIBILITY': [
            'Behavioural feasibility depends on whether users are willing to record sensitive wellness data regularly.',
            'DayTone supports this through a clear interface, privacy-aware wording, optional journal encryption, and understandable risk labels rather than technical model outputs.'
        ],
        '4.1 REQUIREMENTS': [
            'The project requires a browser-based interface, a Flask backend, persistent database storage, machine learning libraries, charting libraries, and PDF export support.',
            'These requirements are selected to match the implemented DayTone application rather than a generic wellness system.'
        ],
        '4.1.1 HARDWARE REQUIREMENTS': [
            'The application can be developed and demonstrated on a standard laptop or desktop computer with enough memory to run Python, a database, and a local browser.',
            'No special sensor device or clinical hardware is required because all wellness values are entered manually by the user.'
        ],
        '4.1.2 SOFTWARE REQUIREMENTS': [
            'Software requirements include Python, Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Scikit-learn, NLTK VADER, ReportLab, Bootstrap, Chart.js, D3.js, and Three.js [1]-[6], [8], [9].',
            'Deployment-oriented support can include Gunicorn, Docker, Redis, PostgreSQL, and environment variables for secure configuration.'
        ],
        '5.1 SYSTEM DESIGN': [
            'DayTone follows a modular web application design. Authentication, mood tracking, administration, NLP, ML prediction, PDF reporting, analytics, mail, and audit features are separated into focused modules.',
            'This design makes the system easier to maintain because changes to one workflow do not require rewriting unrelated parts of the application.'
        ],
        '5.3 INPUT DESIGN': [
            'The input design focuses on simple daily logging. Users provide mood score, sleep hours, stress level, activity information, social interaction, and journal reflections through validated forms.',
            'Validation helps prevent incomplete or incorrect values from reaching the prediction pipeline, while CSRF protection supports safer form submission [7].'
        ],
        '5.4 OUTPUT DESIGN': [
            'The output design presents wellness insights through dashboard cards, charts, heatmaps, history tables, suggestions, risk labels, and downloadable PDF or CSV reports.',
            'The goal is to convert raw log data and model results into explanations that a normal user can understand without studying the underlying algorithm.'
        ],
        '6.1 FUNCTIONAL REQUIREMENTS': [
            'Functional requirements include registration, login, profile management, daily mood logging, journal sentiment analysis, burnout prediction, dashboard visualisation, goal tracking, history search, and report export.',
            'Administrative functions include user management, audit log viewing, invite token management, model review, bias audit, and developer-only controls.'
        ],
        '6.2 NON - FUNCTIONAL REQUIREMENTS': [
            'Non-functional requirements include privacy, security, usability, maintainability, reliability, accessibility, and performance.',
            'The application supports these requirements through hashed passwords, CSRF protection, role-based access, optional journal encryption, modular code, audit logs, and responsive frontend components [7], [8].'
        ],
        '8.1 SYSTEM TESTING': [
            'System testing verifies that the complete DayTone workflow operates correctly from login to daily logging, prediction, dashboard update, history display, and export.',
            'The goal is to confirm that independent modules work together as one application.'
        ],
        '8.2 UNIT TESTING': [
            'Unit testing checks individual functions, forms, routes, and helper utilities separately.',
            'This is useful for validating sentiment helpers, prediction preparation, authentication rules, and analytics calculations before full-system testing.'
        ],
        '8.3 INTEGRATION TESTING': [
            'Integration testing checks communication between the Flask routes, database models, NLP helper, ML predictor, templates, and export utilities.',
            'It confirms that submitted wellness data moves correctly from the form into storage, analysis, prediction, and dashboard output.'
        ],
        '8.4 BLACK BOX TESTING': [
            'Black box testing examines DayTone from the user side without considering internal code.',
            'Test cases include valid login, invalid login, mood log submission, dashboard display, search filters, export buttons, and administrator page access.'
        ],
        '8.5 VALIDATION TESTING': [
            'Validation testing ensures that forms reject missing, out-of-range, or malformed values.',
            'This protects the quality of stored wellness records and prevents invalid inputs from affecting prediction results.'
        ],
        '8.6 OUTPUT TESTING': [
            'Output testing confirms that charts, heatmaps, risk labels, suggestions, history records, PDF reports, and CSV exports display the expected information.',
            'The emphasis is on clarity, correctness, and consistency between stored data and visible results.'
        ],
        '8.7 USER ACCEPTANCE TESTING': [
            'User acceptance testing checks whether the application feels understandable and useful for a student or professional recording daily wellness data.',
            'The workflow is considered acceptable when a user can complete logging and interpret dashboard feedback without additional technical guidance.'
        ],
        '8.8 WHITE BOX TESTING': [
            'White box testing reviews the internal routes, model calls, permission checks, and database operations.',
            'It helps confirm that protected pages require the correct role and that sensitive workflows follow the intended code path.'
        ],
        '10.1 CONCLUSION': [
            'DayTone successfully demonstrates a privacy-aware mental wellness tracker that combines daily logging, sentiment analysis, burnout prediction, visual dashboards, history tracking, and administrative monitoring.',
            'The project shows how Flask, SQLAlchemy, Scikit-learn, VADER, ReportLab, and browser-based visualisation libraries can be integrated into a complete academic software system [1]-[6], [9].',
            'The system is intended for self-awareness and academic demonstration, not for clinical diagnosis. This limitation is important because automated wellness predictions should be treated as support signals rather than medical conclusions.'
        ],
    }
    default = []
    return list(data.get(key, default))


def detail_paragraphs(heading):
    clean = heading.split(' ', 1)[-1].replace('&', 'and').replace('  ', ' ').title()
    return [
        f'The {clean} section is connected to the working DayTone codebase through Flask routes, Jinja templates, SQLAlchemy models, utility functions, and supporting scripts. This makes the report content directly related to the implemented project instead of remaining at a general theoretical level.',
        'A normal user interacts with DayTone by registering, logging in, entering daily wellness values, writing a reflection, and viewing updated insights. Behind this simple workflow the application validates form data, stores records, computes sentiment, prepares prediction features, saves burnout history, and refreshes dashboard visualisations.',
        'The system uses a layered structure. The presentation layer contains HTML templates, Bootstrap styling, JavaScript charts, heatmap views, and the mood orb. The business logic layer contains authentication, logging, analytics, suggestions, exports, and administrator actions. The data layer stores users, profiles, mood logs, goals, suggestions, burnout history, invite tokens, and audit records.',
        'Privacy is considered throughout the implementation because mood notes and wellness values can reveal sensitive personal information. The project uses password hashing, CSRF-protected forms, session-based login, optional journal encryption, account deletion support, and controlled administrator access to reduce avoidable exposure of personal data.',
        'Maintainability is also an important factor. The application separates authentication, mood tracking, administration, natural language processing, machine learning, PDF reporting, mail handling, analytics, and audit logging into separate modules. This structure helps future developers locate defects and extend features without disturbing unrelated parts of the system.',
        'DayTone presents results in a user-friendly form. Instead of displaying raw model calculations, it uses risk labels, charts, history tables, heatmaps, goal progress, suggestions, and downloadable reports. This is important because the target user needs practical self-awareness rather than technical machine learning terminology.',
        'The project also recognises the limits of automated wellness analysis. The burnout output is an academic prediction based on structured behavioural patterns and local sentiment, not a clinical diagnosis. The interface and documentation therefore treat the result as a supportive early-warning indicator.',
        'From an administrator perspective, DayTone includes audit logs, user management pages, model review features, bias audit support, drift monitoring scripts, and developer dashboards. These components show that the project is designed with accountability and long-term operation in mind.',
        'The implementation can be executed in a student development environment using SQLite and can be deployed more formally using PostgreSQL, Redis, Gunicorn, Docker, and environment-based configuration. This makes the same project suitable for demonstration, testing, and future production-style improvement.',
        'Overall, this section strengthens the project report by showing how academic software engineering topics are reflected in a real application. The DayTone workflow combines data collection, analysis, prediction, visualisation, security, and reporting into one coherent mental wellness tracking system.',
    ]


def bullets_for(key):
    return [
        'Supports the overall DayTone workflow and academic project objective.',
        'Uses modular implementation so the feature can be tested and maintained separately.',
        'Maintains focus on privacy, usability, reliable processing, and clear user feedback.',
        'Can be enhanced in future versions as more validated data and user feedback become available.'
    ]


plan = [
    ('section', 'ABSTRACT', 'ABSTRACT', 1),
    ('chapter', 'CHAPTER 1  INTRODUCTION', 'INTRODUCTION', 1),
    ('section', '1.1  GENERAL INTRODUCTION', '1.1 GENERAL INTRODUCTION', 1),
    ('section', '1.2  GOAL OF THE PROJECT', '1.2 GOAL OF THE PROJECT', 2),
    ('chapter', 'CHAPTER  2  LITERATURE SURVEY', 'LITERATURE SURVEY', 2),
    ('section', '2.1  EXISTING SYSTEM', '2.1 EXISTING SYSTEM', 2),
    ('section', '2.2  DRAWBACK OF EXISTING SYSTEM', '2.2 DRAWBACK OF EXISTING SYSTEM', 2),
    ('chapter', 'CHAPTER  3  OVERALL DESCRIPTION', 'OVERALL DESCRIPTION', 3),
    ('section', '3.1  PROPOSED SYSTEM', '3.1 PROPOSED SYSTEM', 3),
    ('section', '3.2  FEATURES OF PROPOSED SYSTEM', '3.2 FEATURES OF PROPOSED SYSTEM', 3),
    ('section', '3.3  REQUIREMENT SPECIFICATION', '3.3 REQUIREMENT SPECIFICATION', 3),
    ('section', '3.4  FEASIBILITY ANALYSIS', '3.4 FEASIBILITY ANALYSIS', 4),
    ('section', '3.4.1  TECHNICAL FEASIBILITY', '3.4.1 TECHNICAL FEASIBILITY', 4),
    ('section', '3.4.2  OPERATIONAL FEASIBILITY', '3.4.2 OPERATIONAL FEASIBILITY', 4),
    ('section', '3.4.3  ECONOMICAL FEASIBILITY', '3.4.3 ECONOMICAL FEASIBILITY', 5),
    ('section', '3.4.4  BEHAVIORAL FEASIBILITY', '3.4.4 BEHAVIORAL FEASIBILITY', 5),
    ('chapter', 'CHAPTER 4  OPERATING ENVIRONMENT', 'OPERATING ENVIRONMENT', 5),
    ('section', '4.1  REQUIREMENTS', '4.1 REQUIREMENTS', 5),
    ('section', '4.1.1  HARDWARE REQUIREMENTS', '4.1.1 HARDWARE REQUIREMENTS', 5),
    ('section', '4.1.2  SOFTWARE REQUIREMENTS', '4.1.2 SOFTWARE REQUIREMENTS', 5),
    ('chapter', 'CHAPTER 5  DESIGN', 'DESIGN', 6),
    ('section', '5.1  SYSTEM DESIGN', '5.1 SYSTEM DESIGN', 6),
    ('section', '5.2  DATA FLOW DIAGRAM', '5.2 DATA FLOW DIAGRAM', 6),
    ('section', '5.3  INPUT DESIGN', '5.3 INPUT DESIGN', 8),
    ('section', '5.4  OUTPUT DESIGN', '5.4 OUTPUT DESIGN', 8),
    ('chapter', 'CHAPTER 6 FUNCTIONAL &NON- FUNCTIONAL REQUIREMENTS', 'FUNCTIONAL & NON-FUNCTIONAL REQUIREMENTS', 9),
    ('section', '6.1  FUNCTIONAL REQUIREMENTS', '6.1 FUNCTIONAL REQUIREMENTS', 9),
    ('section', '6.2  NON - FUNCTIONAL REQUIREMENTS', '6.2 NON - FUNCTIONAL REQUIREMENTS', 9),
    ('chapter', 'CHAPTER 7 ALGORITHM', 'ALGORITHM', 9),
    ('section', '7.1  DECISION TREE ALGORITHM (ML MODEL)', '7.1 DECISION TREE ALGORITHM (ML MODEL)', 9),
    ('chapter', 'CHAPTER 8 TESTING', 'TESTING', 10),
    ('section', '8.1  SYSTEM TESTING', '8.1 SYSTEM TESTING', 10),
    ('section', '8.2  UNIT TESTING', '8.2 UNIT TESTING', 10),
    ('section', '8.3  INTEGRATION TESTING', '8.3 INTEGRATION TESTING', 10),
    ('section', '8.4  BLACK BOX TESTING', '8.4 BLACK BOX TESTING', 11),
    ('section', '8.5  VALIDATION TESTING', '8.5 VALIDATION TESTING', 11),
    ('section', '8.6  OUTPUT TESTING', '8.6 OUTPUT TESTING', 11),
    ('section', '8.7  USER ACCEPTANCE TESTING', '8.7 USER ACCEPTANCE TESTING', 11),
    ('section', '8.8  WHITE BOX TESTING', '8.8 WHITE BOX TESTING', 11),
    ('chapter', 'CHAPTER 10  CONCLUSION', 'CONCLUSION', 11),
    ('section', '10.1  CONCLUSION', '10.1 CONCLUSION', 11),
    ('section', '10.2  FUTURE ENHANCEMENT', '10.2 FUTURE ENHANCEMENT', 12),
    ('section', 'REFERENCES', 'REFERENCES', 12),
    ('chapter', 'APPENDIX', 'APPENDICES', 13),
    ('section', 'APPENDIX A  SCREENSHOTS', '9.1 SCREENSHOTS', 13),
]


def contents(c):
    chunks = [plan[:26], plan[26:]]
    for chunk_index, chunk in enumerate(chunks):
        draw_page_border(c)
        toc_font = 12
        row_gap = 0.78 * cm
        c.setFont(FONT_BOLD, 16)
        c.drawCentredString(W / 2, H - 1.8 * cm, 'CONTENTS')
        if chunk_index == 0:
            c.setFont(FONT_BOLD, 14)
            c.drawString(LEFT - 0.15 * cm, H - 2.75 * cm, 'TABLE OF CONTENT')
            y = H - 3.55 * cm
        else:
            y = H - 2.9 * cm
        for kind, toc, heading, printed in chunk:
            indent = 1.05 * cm if kind == 'section' and toc != 'ABSTRACT' and toc != 'REFERENCES' else 0
            if toc.startswith(('3.4.', '4.1.', '10.')):
                indent = 1.9 * cm
            c.setFont(FONT_REGULAR, toc_font)
            label = toc
            c.drawString(LEFT + indent, y, label)
            text_w = c.stringWidth(label, FONT_REGULAR, toc_font)
            page_text = str(printed)
            page_w = c.stringWidth(page_text, FONT_REGULAR, toc_font)
            start_x = LEFT + indent + text_w + 2
            end_x = W - RIGHT - page_w - 4
            if end_x > start_x:
                dot_w = c.stringWidth('.', FONT_REGULAR, toc_font)
                c.drawString(start_x, y, '.' * int((end_x - start_x) / dot_w))
            c.drawRightString(W - RIGHT, y, page_text)
            y -= row_gap
        c.showPage()


def diagram_box(caption, height=4.0 * cm):
    t = Table([[P('<br/><br/>DAYTONE DIAGRAM AREA<br/>' + caption, 'report_caption')]], colWidths=[15.8 * cm], rowHeights=[height])
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.8, colors.black), ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    return t


class ScreenshotFlowable(Flowable):
    def __init__(self, image_path, caption, height):
        super().__init__()
        self.image_path = Path(image_path)
        self.caption = caption
        self.width = CONTENT_W
        self.height = height

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def draw(self):
        c = self.canv
        if not self.image_path.exists():
            c.setLineWidth(0.8)
            c.setStrokeColor(colors.black)
            c.setFillColor(colors.whitesmoke)
            c.rect(0, 0, self.width, self.height, fill=1)
            c.setFillColor(colors.black)
            c.setFont(FONT_ITALIC, 12)
            c.drawCentredString(self.width / 2, self.height / 2, self.caption + ' image not found')
            return

        reader = ImageReader(str(self.image_path))
        iw, ih = reader.getSize()
        padding = 0.12 * cm
        max_w = self.width - (2 * padding)
        max_h = self.height - (2 * padding)
        scale = min(max_w / iw, max_h / ih)
        draw_w = iw * scale
        draw_h = ih * scale
        x = (self.width - draw_w) / 2
        y = (self.height - draw_h) / 2
        c.setLineWidth(0.55)
        c.setStrokeColor(colors.black)
        c.rect(x, y, draw_w, draw_h)
        c.drawImage(reader, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')


class DFDFlowable(Flowable):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.width = CONTENT_W
        self.height = {
            'context': 4.5 * cm,
            'user': 9.6 * cm,
            'admin': 8.4 * cm,
            'developer': 8.4 * cm,
        }.get(level, 7.85 * cm if level in (0, 1) else 15.9 * cm)

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def _text(self, x, y, lines, size=7.8, bold=False, center=True):
        self.canv.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
        leading = size + 2
        for i, line in enumerate(lines):
            yy = y - (i * leading)
            if center:
                self.canv.drawCentredString(x, yy, line)
            else:
                self.canv.drawString(x, yy, line)

    def _rect(self, x, y, w, h, lines, size=7.6):
        self.canv.rect(x, y, w, h)
        self._text(x + w / 2, y + h / 2 + ((len(lines) - 1) * 4), lines, size=size)

    def _process(self, x, y, w, h, lines, size=7.4):
        self.canv.roundRect(x, y, w, h, 8)
        self._text(x + w / 2, y + h / 2 + ((len(lines) - 1) * 4), lines, size=size)

    def _circle(self, x, y, w, h, lines, size=6.8):
        self.canv.ellipse(x, y, x + w, y + h)
        self._text(x + w / 2, y + h / 2 + ((len(lines) - 1) * 4), lines, size=size)

    def _store(self, x, y, w, h, label):
        self.canv.line(x, y, x + w, y)
        self.canv.line(x, y + h, x + w, y + h)
        self.canv.line(x + 0.18 * cm, y, x + 0.18 * cm, y + h)
        self._text(x + w / 2, y + h / 2 + 3, [label], size=7.3)

    def _arrow(self, x1, y1, x2, y2, label='', label_dx=0, label_dy=0):
        self.canv.line(x1, y1, x2, y2)
        dx = x2 - x1
        dy = y2 - y1
        angle = atan2(dy, dx)
        size = 6
        spread = pi / 7
        pts = [
            (x2, y2),
            (x2 - size * cos(angle - spread), y2 - size * sin(angle - spread)),
            (x2 - size * cos(angle + spread), y2 - size * sin(angle + spread)),
        ]
        p = self.canv.beginPath()
        p.moveTo(*pts[0])
        p.lineTo(*pts[1])
        p.lineTo(*pts[2])
        p.close()
        self.canv.drawPath(p, fill=1, stroke=0)
        if label:
            mx, my = (x1 + x2) / 2 + label_dx, (y1 + y2) / 2 + label_dy
            label_size = 5.4
            self.canv.setFillColor(colors.black)
            if abs(label_dy) < 0.01:
                my += 0.12 * cm
            self._text(mx, my - 2, [label], size=label_size)

    def _elbow_arrow(self, x1, y1, x2, y2, via_x=None, via_y=None, label='', label_dx=0, label_dy=0):
        if via_x is not None:
            self.canv.line(x1, y1, via_x, y1)
            self._arrow(via_x, y1, x2, y2, label, label_dx, label_dy)
        elif via_y is not None:
            self.canv.line(x1, y1, x1, via_y)
            self._arrow(x1, via_y, x2, y2, label, label_dx, label_dy)
        else:
            self._arrow(x1, y1, x2, y2, label, label_dx, label_dy)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colors.black)
        c.setFillColor(colors.black)
        c.setLineWidth(0.65)
        if self.level == 'context':
            self._draw_context_style()
        elif self.level == 'user':
            self._draw_user_style()
        elif self.level == 'admin':
            self._draw_admin_style()
        elif self.level == 'developer':
            self._draw_developer_style()
        elif self.level == 0:
            self._text(self.width / 2, self.height - 0.35 * cm, [f'Level {self.level} Data Flow Diagram'], size=12, bold=True)
            self._draw_level0()
        elif self.level == 1:
            self._text(self.width / 2, self.height - 0.35 * cm, [f'Level {self.level} Data Flow Diagram'], size=12, bold=True)
            self._draw_level1()
        else:
            self._text(self.width / 2, self.height - 0.35 * cm, [f'Level {self.level} Data Flow Diagram'], size=12, bold=True)
            self._draw_level2()
        c.restoreState()

    def _draw_context_style(self):
        self._text(0.6 * cm, self.height - 0.45 * cm, ['Level 0 (Context Level)'], size=9.5, bold=True, center=False)
        y = 1.35 * cm
        self._rect(0.6 * cm, y + 0.55 * cm, 3.1 * cm, 1.25 * cm, ['User, Admin,', 'Developer'])
        self._circle(6.0 * cm, y + 0.15 * cm, 2.6 * cm, 2.0 * cm, ['DayTone'])
        self._rect(11.1 * cm, y + 0.55 * cm, 3.1 * cm, 1.25 * cm, ['User, Admin,', 'Developer'])
        self._arrow(3.7 * cm, y + 1.2 * cm, 6.0 * cm, y + 1.2 * cm, 'Request', label_dy=0.12 * cm)
        self._arrow(8.6 * cm, y + 1.2 * cm, 11.1 * cm, y + 1.2 * cm, 'Response', label_dy=0.12 * cm)

    def _draw_user_style(self):
        self._text(0.6 * cm, self.height - 0.35 * cm, ['Level 1 (user)'], size=9.5, bold=True, center=False)
        y = 0.15 * cm
        self._rect(0.7 * cm, y + 5.45 * cm, 2.4 * cm, 0.85 * cm, ['USER'])
        self._circle(4.0 * cm, y + 5.0 * cm, 1.55 * cm, 1.35 * cm, ['login'])
        self._circle(7.0 * cm, y + 7.05 * cm, 1.75 * cm, 1.5 * cm, ['daily', 'log'])
        self._circle(7.0 * cm, y + 4.75 * cm, 1.75 * cm, 1.5 * cm, ['analyse', 'mood'])
        self._circle(7.0 * cm, y + 2.55 * cm, 1.75 * cm, 1.5 * cm, ['view', 'dashboard'])
        self._store(10.6 * cm, y + 7.65 * cm, 3.1 * cm, 0.62 * cm, 'D2 Mood Log')
        self._store(10.6 * cm, y + 5.3 * cm, 3.1 * cm, 0.62 * cm, 'D3 Burnout History')
        self._process(10.6 * cm, y + 2.85 * cm, 3.1 * cm, 0.8 * cm, ['PDF / CSV export'])
        self._store(3.95 * cm, y + 2.0 * cm, 3.1 * cm, 0.62 * cm, 'D1 User')
        self._text(3.18 * cm, y + 6.12 * cm, ['email, password'], size=5.4, center=False)
        self._arrow(3.1 * cm, y + 5.88 * cm, 4.0 * cm, y + 5.88 * cm)
        self._arrow(4.8 * cm, y + 5.0 * cm, 4.8 * cm, y + 2.62 * cm, 'user id', label_dx=-0.32 * cm)
        self._arrow(5.2 * cm, y + 6.05 * cm, 7.0 * cm, y + 7.65 * cm, 'user id', label_dx=-0.24 * cm, label_dy=0.18 * cm)
        self._arrow(8.75 * cm, y + 7.8 * cm, 10.6 * cm, y + 7.95 * cm, 'mood, sleep, stress', label_dy=0.18 * cm)
        self._arrow(5.55 * cm, y + 5.65 * cm, 7.0 * cm, y + 5.5 * cm, 'log data', label_dy=0.16 * cm)
        self._arrow(8.75 * cm, y + 5.5 * cm, 10.6 * cm, y + 5.65 * cm, 'risk, sentiment', label_dy=0.18 * cm)
        self._arrow(5.25 * cm, y + 5.05 * cm, 7.0 * cm, y + 3.25 * cm, 'user id', label_dx=-0.32 * cm)
        self._arrow(8.75 * cm, y + 3.3 * cm, 10.6 * cm, y + 3.3 * cm, 'report request', label_dy=0.16 * cm)

    def _draw_admin_style(self):
        self._text(0.6 * cm, self.height - 0.35 * cm, ['Level 1 (admin)'], size=9.5, bold=True, center=False)
        y = 0.2 * cm
        self._rect(0.55 * cm, y + 4.95 * cm, 2.4 * cm, 0.85 * cm, ['ADMIN'])
        self._circle(4.0 * cm, y + 4.75 * cm, 1.55 * cm, 1.35 * cm, ['login'])
        self._circle(7.0 * cm, y + 6.0 * cm, 1.85 * cm, 1.4 * cm, ['manage', 'users'])
        self._circle(7.0 * cm, y + 4.0 * cm, 1.85 * cm, 1.4 * cm, ['view user', 'details'])
        self._circle(7.0 * cm, y + 2.0 * cm, 1.85 * cm, 1.4 * cm, ['view model', 'audit'])
        self._store(10.8 * cm, y + 6.45 * cm, 3.0 * cm, 0.62 * cm, 'D1 User')
        self._store(10.8 * cm, y + 4.45 * cm, 3.0 * cm, 0.62 * cm, 'D2 Mood Log')
        self._store(10.8 * cm, y + 2.45 * cm, 3.0 * cm, 0.62 * cm, 'D5 Audit/Model')
        self._store(3.9 * cm, y + 1.3 * cm, 3.1 * cm, 0.62 * cm, 'D4 Admin')
        self._text(3.05 * cm, y + 5.62 * cm, ['password'], size=5.4, center=False)
        self._arrow(2.95 * cm, y + 5.38 * cm, 4.0 * cm, y + 5.38 * cm)
        self._arrow(4.8 * cm, y + 4.75 * cm, 4.8 * cm, y + 1.92 * cm, 'admin id', label_dx=-0.34 * cm)
        self._arrow(5.55 * cm, y + 5.72 * cm, 7.0 * cm, y + 6.7 * cm, 'admin id', label_dx=-0.28 * cm, label_dy=0.18 * cm)
        self._arrow(8.85 * cm, y + 6.7 * cm, 10.8 * cm, y + 6.75 * cm, 'role, delete', label_dy=0.17 * cm)
        self._arrow(5.55 * cm, y + 5.25 * cm, 7.0 * cm, y + 4.7 * cm, 'user id', label_dy=-0.14 * cm)
        self._arrow(8.85 * cm, y + 4.7 * cm, 10.8 * cm, y + 4.75 * cm, 'fetch logs', label_dy=0.17 * cm)
        self._arrow(5.45 * cm, y + 4.9 * cm, 7.0 * cm, y + 2.7 * cm, 'admin id', label_dx=-0.34 * cm)
        self._arrow(8.85 * cm, y + 2.7 * cm, 10.8 * cm, y + 2.75 * cm, 'audit result', label_dy=0.17 * cm)

    def _draw_developer_style(self):
        self._text(0.6 * cm, self.height - 0.35 * cm, ['Level 1 (developer)'], size=9.5, bold=True, center=False)
        y = 0.2 * cm
        self._rect(0.55 * cm, y + 4.95 * cm, 2.55 * cm, 0.85 * cm, ['DEVELOPER'])
        self._circle(4.0 * cm, y + 4.75 * cm, 1.55 * cm, 1.35 * cm, ['login'])
        self._circle(7.0 * cm, y + 6.0 * cm, 1.95 * cm, 1.4 * cm, ['developer', 'dashboard'])
        self._circle(7.0 * cm, y + 4.0 * cm, 1.95 * cm, 1.4 * cm, ['approve', 'requests'])
        self._circle(7.0 * cm, y + 2.0 * cm, 1.95 * cm, 1.4 * cm, ['system', 'diagnostics'])
        self._store(10.9 * cm, y + 6.45 * cm, 3.15 * cm, 0.62 * cm, 'D1 User/Role')
        self._store(10.9 * cm, y + 4.45 * cm, 3.15 * cm, 0.62 * cm, 'D6 Change Request')
        self._store(10.9 * cm, y + 2.45 * cm, 3.15 * cm, 0.62 * cm, 'D5 Metrics/Audit')
        self._store(3.9 * cm, y + 1.3 * cm, 3.1 * cm, 0.62 * cm, 'D7 Developer')
        self._text(3.2 * cm, y + 5.62 * cm, ['password'], size=5.4, center=False)
        self._arrow(3.1 * cm, y + 5.38 * cm, 4.0 * cm, y + 5.38 * cm)
        self._arrow(4.8 * cm, y + 4.75 * cm, 4.8 * cm, y + 1.92 * cm, 'developer id', label_dx=-0.36 * cm)
        self._arrow(5.55 * cm, y + 5.72 * cm, 7.0 * cm, y + 6.7 * cm, 'developer id', label_dx=-0.34 * cm, label_dy=0.18 * cm)
        self._arrow(8.95 * cm, y + 6.7 * cm, 10.9 * cm, y + 6.75 * cm, 'protected roles', label_dy=0.17 * cm)
        self._arrow(5.55 * cm, y + 5.25 * cm, 7.0 * cm, y + 4.7 * cm, 'request id', label_dy=-0.14 * cm)
        self._arrow(8.95 * cm, y + 4.7 * cm, 10.9 * cm, y + 4.75 * cm, 'approve / reject', label_dy=0.17 * cm)
        self._arrow(5.45 * cm, y + 4.9 * cm, 7.0 * cm, y + 2.7 * cm, 'system data', label_dx=-0.34 * cm)
        self._arrow(8.95 * cm, y + 2.7 * cm, 10.9 * cm, y + 2.75 * cm, 'metrics', label_dy=0.17 * cm)

    def _draw_level0(self):
        y = 1.35 * cm
        self._rect(0.2 * cm, y + 2.2 * cm, 3.5 * cm, 1.25 * cm, ['User'])
        self._process(5.3 * cm, y + 1.75 * cm, 5.0 * cm, 2.15 * cm, ['0', 'DayTone Wellness', 'Tracking System'])
        self._rect(12.0 * cm, y + 2.2 * cm, 3.5 * cm, 1.25 * cm, ['Administrator'])
        self._arrow(3.7 * cm, y + 3.0 * cm, 5.3 * cm, y + 3.0 * cm, 'login, logs')
        self._arrow(5.3 * cm, y + 2.35 * cm, 3.7 * cm, y + 2.35 * cm, 'insights, reports')
        self._arrow(10.3 * cm, y + 3.0 * cm, 12.0 * cm, y + 3.0 * cm, 'analytics')
        self._arrow(12.0 * cm, y + 2.35 * cm, 10.3 * cm, y + 2.35 * cm, 'admin actions')

    def _draw_level1(self):
        y = 0.7 * cm
        self._rect(0.15 * cm, y + 4.6 * cm, 2.5 * cm, 0.85 * cm, ['User'])
        self._process(3.1 * cm, y + 4.55 * cm, 2.6 * cm, 0.95 * cm, ['1.0', 'Authenticate'])
        self._process(3.1 * cm, y + 2.95 * cm, 2.6 * cm, 0.95 * cm, ['2.0', 'Record Log'])
        self._process(6.7 * cm, y + 2.95 * cm, 2.85 * cm, 0.95 * cm, ['3.0', 'Analyse Mood'])
        self._process(10.5 * cm, y + 2.95 * cm, 2.9 * cm, 0.95 * cm, ['4.0', 'Generate Output'])
        self._rect(13.8 * cm, y + 4.6 * cm, 2.3 * cm, 0.85 * cm, ['Admin'])
        self._store(6.6 * cm, y + 5.1 * cm, 3.0 * cm, 0.55 * cm, 'D1 Users')
        self._store(6.6 * cm, y + 1.8 * cm, 3.0 * cm, 0.55 * cm, 'D2 Mood Logs')
        self._store(10.5 * cm, y + 1.8 * cm, 3.0 * cm, 0.55 * cm, 'D3 History')
        self._arrow(2.65 * cm, y + 5.05 * cm, 3.1 * cm, y + 5.05 * cm, 'credentials')
        self._arrow(4.4 * cm, y + 4.55 * cm, 7.0 * cm, y + 5.1 * cm, 'user data')
        self._arrow(2.65 * cm, y + 4.75 * cm, 3.1 * cm, y + 3.45 * cm, 'daily values')
        self._arrow(5.7 * cm, y + 3.42 * cm, 6.7 * cm, y + 3.42 * cm, 'validated log')
        self._arrow(8.1 * cm, y + 2.95 * cm, 8.1 * cm, y + 2.35 * cm, 'save')
        self._arrow(9.55 * cm, y + 3.42 * cm, 10.5 * cm, y + 3.42 * cm, 'risk + sentiment')
        self._arrow(11.95 * cm, y + 2.95 * cm, 11.95 * cm, y + 2.35 * cm, 'store result')
        self._arrow(13.4 * cm, y + 3.42 * cm, 15.0 * cm, y + 4.6 * cm, 'dashboard data')

    def _draw_level2(self):
        y = 0.55 * cm
        self._rect(0.15 * cm, y + 12.4 * cm, 2.4 * cm, 0.85 * cm, ['User'])
        self._process(3.1 * cm, y + 12.35 * cm, 3.0 * cm, 0.9 * cm, ['2.1', 'Enter Daily', 'Wellness Log'])
        self._process(7.0 * cm, y + 12.35 * cm, 3.0 * cm, 0.9 * cm, ['2.2', 'Validate Form', 'Inputs'])
        self._process(11.0 * cm, y + 12.35 * cm, 3.0 * cm, 0.9 * cm, ['2.3', 'Store Mood', 'Record'])
        self._process(3.1 * cm, y + 8.65 * cm, 3.0 * cm, 0.9 * cm, ['3.1', 'Compute VADER', 'Sentiment'])
        self._process(7.0 * cm, y + 8.65 * cm, 3.0 * cm, 0.9 * cm, ['3.2', 'Build 12-Feature', 'Vector'])
        self._process(11.0 * cm, y + 8.65 * cm, 3.0 * cm, 0.9 * cm, ['3.3', 'Predict Burnout', 'Decision Tree'])
        self._process(3.1 * cm, y + 4.95 * cm, 3.0 * cm, 0.9 * cm, ['4.1', 'Generate', 'Suggestions'])
        self._process(7.0 * cm, y + 4.95 * cm, 3.0 * cm, 0.9 * cm, ['4.2', 'Prepare Charts', 'and Heatmap'])
        self._process(11.0 * cm, y + 4.95 * cm, 3.0 * cm, 0.9 * cm, ['4.3', 'Export PDF', 'or CSV'])
        self._store(11.0 * cm, y + 10.75 * cm, 3.2 * cm, 0.55 * cm, 'D2 Mood Logs')
        self._store(11.0 * cm, y + 7.2 * cm, 3.2 * cm, 0.55 * cm, 'D3 Burnout History')
        self._store(6.9 * cm, y + 3.25 * cm, 3.2 * cm, 0.55 * cm, 'D4 Suggestions')
        self._rect(0.15 * cm, y + 4.95 * cm, 2.4 * cm, 0.85 * cm, ['Dashboard'])
        self._arrow(2.55 * cm, y + 12.85 * cm, 3.1 * cm, y + 12.85 * cm, 'mood, sleep, stress')
        self._arrow(6.1 * cm, y + 12.8 * cm, 7.0 * cm, y + 12.8 * cm, 'form data')
        self._arrow(10.0 * cm, y + 12.8 * cm, 11.0 * cm, y + 12.8 * cm, 'valid log')
        self._arrow(12.5 * cm, y + 12.35 * cm, 12.5 * cm, y + 11.3 * cm, 'save')
        self._arrow(11.0 * cm, y + 12.45 * cm, 4.6 * cm, y + 9.55 * cm, 'journal')
        self._arrow(6.1 * cm, y + 9.1 * cm, 7.0 * cm, y + 9.1 * cm, 'sentiment')
        self._arrow(8.5 * cm, y + 8.65 * cm, 8.5 * cm, y + 5.85 * cm, 'trend values')
        self._arrow(10.0 * cm, y + 9.1 * cm, 11.0 * cm, y + 9.1 * cm, 'features')
        self._arrow(12.5 * cm, y + 8.65 * cm, 12.5 * cm, y + 7.75 * cm, 'prediction')
        self._arrow(11.0 * cm, y + 8.65 * cm, 4.6 * cm, y + 5.85 * cm, 'risk level')
        self._arrow(6.1 * cm, y + 5.4 * cm, 6.9 * cm, y + 3.9 * cm, 'tips')
        self._arrow(3.1 * cm, y + 5.55 * cm, 2.55 * cm, y + 5.55 * cm, 'tips')
        self._arrow(7.0 * cm, y + 5.35 * cm, 2.55 * cm, y + 5.35 * cm, 'charts')
        self._arrow(10.0 * cm, y + 5.4 * cm, 11.0 * cm, y + 5.4 * cm, 'history')
        self._arrow(11.0 * cm, y + 5.1 * cm, 2.55 * cm, y + 5.1 * cm, 'report')


def extended_paragraphs(heading, continuation=0):
    extras = {
        '7.1 DECISION TREE ALGORITHM (ML MODEL)': [
            'Decision Tree is used in DayTone as the currently selected machine learning model because the training pipeline compares Decision Tree, Logistic Regression, and Random Forest, then saves the model with the best holdout accuracy. The active model metadata identifies DecisionTree as the saved burnout prediction algorithm.',
            'A Decision Tree classifier works by splitting the input data into branches based on feature values. In DayTone, the tree studies wellness indicators such as mood score, sleep hours, stress level, activity status, social interaction, sentiment score, and rolling seven-day values. These splits lead to a final class label such as Low, Medium, or High burnout risk.',
            'This algorithm is suitable for an academic wellness tracker because its decision process is easier to explain than many black-box models. The system can connect a prediction with understandable drivers such as low mood, high stress, reduced sleep, negative journal sentiment, or repeated difficult days.',
            'The DayTone feature vector includes current mood, sleep hours, stress level, activity status, social interaction, sentiment score, seven-day average mood, seven-day average stress, seven-day average sleep, count of repeated difficult days, and similar behavioural indicators. These values allow the model to study both the current day and the recent trend.',
            'The model output is intentionally simple: Low, Medium, or High burnout risk. This makes the prediction understandable for users and suitable for dashboard display. The system avoids presenting the value as a medical diagnosis and treats it as an early awareness signal.',
            'The ML pipeline is trained with synthetic academic data and can later be retrained using exported real logs after proper consent and anonymisation. This keeps the current project privacy-safe while leaving a clear future path for accuracy improvement.',
        ],
        'REFERENCES': [
            '1. Grinberg, M., Flask Web Development, O Reilly Media.',
            '2. Pallets Projects, Flask Documentation.',
            '3. SQLAlchemy Project, SQLAlchemy ORM Documentation.',
            '4. Scikit-learn Developers, Decision Tree Classifier Documentation.',
            '5. Hutto, C. J. and Gilbert, E., VADER: A Parsimonious Rule-based Model for Sentiment Analysis.',
            '6. ReportLab User Guide, PDF Generation in Python.',
            '7. OWASP Foundation, Web Application Security Guidelines.',
            '8. Bootstrap Documentation, Responsive Frontend Components.',
            '9. Chart.js Documentation, Browser-based Data Visualization.',
            '10. DayTone source code, project documentation, model card, and testing files.',
        ],
        '10.2 FUTURE ENHANCEMENT': [
            'Future versions can improve prediction reliability by collecting consent-based real usage data and periodically retraining the Decision Tree model or comparing it again with ensemble models such as Random Forest. A larger dataset can help reduce bias and make predictions more representative of different student and professional routines.',
            'The system can also add counsellor-facing workflows, anonymous institutional analytics, mobile push notifications, multilingual support, wearable device integration, and stronger explainable AI summaries. These additions would make DayTone more useful while still preserving privacy and user control.',
            'Another enhancement is to introduce adaptive suggestions. Instead of showing only rule-based tips, the system can learn which suggestions users find useful and recommend activities based on previous improvement patterns.',
        ],
    }
    paras = []
    paras.extend(extras.get(heading, []))
    if heading != 'REFERENCES':
        paras.extend(section_content(heading))
    return paras


def entry_page(c, kind, heading, printed, continuation=0):
    if kind == 'chapter':
        if heading.startswith('FUNCTIONAL'):
            line1, line2 = 'CHAPTER 6', 'FUNCTIONAL & NON-FUNCTIONAL REQUIREMENTS'
        else:
            line1 = 'CHAPTER ' + str(printed if printed < 10 else 10)
            chapter_labels = {
                'INTRODUCTION': 'CHAPTER 1',
                'LITERATURE SURVEY': 'CHAPTER 2',
                'OVERALL DESCRIPTION': 'CHAPTER 3',
                'OPERATING ENVIRONMENT': 'CHAPTER 4',
                'DESIGN': 'CHAPTER 5',
                'ALGORITHM': 'CHAPTER 7',
                'TESTING': 'CHAPTER 8',
                'APPENDICES': 'CHAPTER 9',
                'CONCLUSION': 'CHAPTER 10',
            }
            line1 = chapter_labels.get(heading, line1)
            line2 = heading
        c.setFont(FONT_BOLD, 18)
        c.drawCentredString(W / 2, H / 2 + 0.6 * cm, line1)
        c.drawCentredString(W / 2, H / 2 - 0.1 * cm, line2)
        c.showPage()
        return
    else:
        title = heading
        items = [P(title, 'report_h1')]
        for para in extended_paragraphs(heading, continuation):
            items.append(P(para, 'report_normal_tight'))
        if heading == '9.1 SCREENSHOTS':
            items = [P(title, 'report_h1')]
            page_groups = [
                SCREENSHOTS[0:2],
                SCREENSHOTS[2:4],
                SCREENSHOTS[4:6],
                SCREENSHOTS[6:8],
                SCREENSHOTS[8:10],
                SCREENSHOTS[10:12],
                SCREENSHOTS[12:15],
                SCREENSHOTS[15:18],
            ]
            group = page_groups[continuation] if continuation < len(page_groups) else []
            image_height = 7.85 * cm if len(group) <= 2 else 5.05 * cm
            start_index = sum(len(g) for g in page_groups[:continuation]) + 1
            for offset, (filename, fig) in enumerate(group):
                index = start_index + offset
                image_path = SCREENSHOT_DIR / filename
                items.append(ScreenshotFlowable(image_path, fig, image_height))
                items.append(P('Figure ' + str(index) + ': ' + fig, 'screenshot_caption'))
            if not group:
                for para in detail_paragraphs(heading)[:5]:
                    items.append(P(para, 'report_normal_tight'))
        elif heading == '5.2 DATA FLOW DIAGRAM':
            items = [P(title, 'report_h1')]
            if continuation == 0:
                items.append(P('The following data flow diagrams describe how information moves through DayTone. The diagrams follow standard DFD rules by separating external entities, processes, data stores, and labelled data flows.', 'report_normal_tight'))
                items.append(DFDFlowable('context'))
                items.append(DFDFlowable('user'))
            else:
                items.append(P('The Level 1 diagrams are separated by role because DayTone contains normal user workflows, administrator workflows, and a protected developer workflow. This makes the DFD closer to the actual project structure.', 'report_normal_tight'))
                items.append(DFDFlowable('admin'))
                items.append(DFDFlowable('developer'))
        elif heading in {'5.1 SYSTEM DESIGN', '5.2 DATA FLOW DIAGRAM', '5.3 INPUT DESIGN', '5.4 OUTPUT DESIGN'}:
            items.append(diagram_box(heading))
        elif heading != 'REFERENCES':
            for b in bullets_for(heading):
                items.append(P('- ' + b, 'report_bullet'))
    page(c, items, printed)


def append_section(story, heading):
    heading_style = 'report_chapter' if heading == 'ABSTRACT' else 'report_h1'
    if heading == 'ABSTRACT':
        paras = extended_paragraphs(heading)
        story.append(P(heading, heading_style))
        for para in paras:
            story.append(P(para, 'report_normal_tight'))
        return

    if heading == '5.2 DATA FLOW DIAGRAM':
        intro = P('The following data flow diagrams describe how information moves through DayTone. The diagrams follow standard DFD rules by separating external entities, processes, data stores, and labelled data flows.', 'report_normal_tight')
        story.append(P(heading, 'report_h1'))
        story.append(intro)
        dfd_items = [
            ('Figure 1: Context Level Data Flow Diagram for DayTone', DFDFlowable('context')),
            ('Figure 2: Level 1 User Data Flow Diagram for DayTone', DFDFlowable('user')),
            ('Figure 3: Level 1 Administrator Data Flow Diagram for DayTone', DFDFlowable('admin')),
            ('Figure 4: Level 1 Developer Data Flow Diagram for DayTone', DFDFlowable('developer')),
        ]
        for caption, figure in dfd_items:
            story.append(figure)
            story.append(P(caption, 'report_caption'))
        return

    if heading == '9.1 SCREENSHOTS':
        intro = P('The appendix contains selected screenshots from the implemented DayTone application.', 'report_normal_tight')
        story.append(P('APPENDIX A: SCREENSHOTS', 'report_h1'))
        story.append(intro)
        for index, (filename, fig) in enumerate(SCREENSHOTS, start=1):
            image_path = SCREENSHOT_DIR / filename
            story.append(ScreenshotFlowable(image_path, fig, 7.85 * cm))
            story.append(P('Figure A.' + str(index) + ': ' + fig, 'screenshot_caption'))
        return

    paras = extended_paragraphs(heading)
    if paras:
        story.append(P(heading, 'report_h1'))
        for para in paras:
            story.append(P(para, 'report_normal_tight'))
    else:
        story.append(P(heading, 'report_h1'))

    if heading in {'5.1 SYSTEM DESIGN', '5.3 INPUT DESIGN', '5.4 OUTPUT DESIGN'}:
        story.append(diagram_box(heading))


def flow_pages(c, story, first_printed=1):
    printed = first_printed
    while story:
        draw_header_footer(c, printed)
        frame = Frame(LEFT, 2.15 * cm, CONTENT_W, H - 5.3 * cm, showBoundary=0)
        frame.addFromList(story, c)
        c.showPage()
        printed += 1


def render_body(c):
    story = []
    for kind, toc, heading, start in plan:
        if kind == 'chapter':
            if heading == 'APPENDICES':
                story.append(P('APPENDIX', 'report_chapter'))
            else:
                story.append(P(heading, 'report_chapter'))
        else:
            append_section(story, heading)
    flow_pages(c, story)


def build():
    c = canvas.Canvas(str(OUT), pagesize=A4)
    title_page(c)
    project_title_page(c)
    certificate(c)
    declaration(c)
    acknowledgement(c)
    contents(c)
    render_body(c)
    c.save()
    print(OUT)


if __name__ == '__main__':
    build()
