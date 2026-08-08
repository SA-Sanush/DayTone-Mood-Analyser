from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, Table, TableStyle

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

styles = {
    'cover_title': ParagraphStyle('cover_title', fontName='Times-Bold', fontSize=18, leading=24, alignment=TA_CENTER),
    'cover': ParagraphStyle('cover', fontName='Times-Bold', fontSize=13, leading=19, alignment=TA_CENTER),
    'normal': ParagraphStyle('normal', fontName='Times-Roman', fontSize=10.8, leading=15.8, alignment=TA_JUSTIFY, spaceAfter=6),
    'normal_tight': ParagraphStyle('normal_tight', fontName='Times-Roman', fontSize=10.2, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=4),
    'center': ParagraphStyle('center', fontName='Times-Roman', fontSize=11, leading=16, alignment=TA_CENTER),
    'right': ParagraphStyle('right', fontName='Times-Roman', fontSize=11, leading=16, alignment=TA_RIGHT),
    'bold_center': ParagraphStyle('bold_center', fontName='Times-Bold', fontSize=12, leading=18, alignment=TA_CENTER),
    'chapter': ParagraphStyle('chapter', fontName='Times-Bold', fontSize=18, leading=27, alignment=TA_CENTER, spaceAfter=16),
    'h1': ParagraphStyle('h1', fontName='Times-Bold', fontSize=13, leading=18, alignment=TA_LEFT, spaceBefore=4, spaceAfter=6),
    'bullet': ParagraphStyle('bullet', fontName='Times-Roman', fontSize=10.2, leading=14.2, leftIndent=16, firstLineIndent=-9, alignment=TA_JUSTIFY, spaceAfter=3),
    'caption': ParagraphStyle('caption', fontName='Times-Italic', fontSize=9, leading=12, alignment=TA_CENTER),
    'table': ParagraphStyle('table', fontName='Times-Roman', fontSize=9.2, leading=12, alignment=TA_LEFT),
    'table_b': ParagraphStyle('table_b', fontName='Times-Bold', fontSize=9.2, leading=12, alignment=TA_LEFT),
}


def P(text, style='normal'):
    return Paragraph(text, styles[style])


def draw_header_footer(c, printed_page=None):
    if printed_page is None:
        return
    c.setFont('Times-Roman', 9)
    c.drawString(LEFT, H - 1.45 * cm, SHORT)
    c.drawRightString(W - RIGHT, H - 1.45 * cm, DEPT + ', LMCST')
    c.line(LEFT, H - 1.62 * cm, W - RIGHT, H - 1.62 * cm)
    c.line(LEFT, 1.65 * cm, W - RIGHT, 1.65 * cm)
    c.drawString(LEFT, 1.27 * cm, 'Department of Computer Applications, LMCST')
    c.drawRightString(W - RIGHT, 1.27 * cm, str(printed_page))


def flow(c, items, y_top=None, y_bottom=None):
    y_top = y_top or H - TOP
    y_bottom = y_bottom or BOTTOM
    frame = Frame(LEFT, y_bottom, CONTENT_W, y_top - y_bottom, showBoundary=0)
    frame.addFromList(items, c)


def page(c, items, printed_page=None):
    draw_header_footer(c, printed_page)
    flow(c, items, H - 2.0 * cm if printed_page else H - TOP, 2.05 * cm if printed_page else BOTTOM)
    c.showPage()


def make_table(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.45, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def title_page(c):
    items = [
        P('MINI PROJECT REPORT', 'cover'), P('ON', 'cover'), P(TITLE, 'cover_title'),
        P('Submitted in partial fulfilment of the requirements for the award of the degree of', 'center'),
        P('MASTER OF COMPUTER APPLICATIONS', 'cover'), P('of', 'center'), P(UNIV, 'cover'),
        P('<br/><br/>Submitted By', 'center'), P(STUDENT, 'cover'), P(REGNO, 'center'),
        P('<br/>Under the Guidance of', 'center'), P(GUIDE, 'cover'),
        P('<br/><br/>' + DEPT, 'cover'), P(COLLEGE, 'cover'), P(PLACE, 'cover'), P(YEAR, 'cover')]
    flow(c, items, H - 1.2 * cm, 1.8 * cm)
    c.showPage()


def certificate(c):
    items = [P(COLLEGE, 'cover'), P(PLACE, 'cover'), P(DEPT, 'cover'), P('<br/>CERTIFICATE', 'chapter'),
             P('This is to certify that the project work entitled <b>"' + TITLE + '"</b> is a bonafide record of the work done by <b>' + STUDENT + '</b>, student of ' + DEPT + ', ' + COLLEGE + ', affiliated to ' + UNIV + ', in partial fulfilment of the requirements for the award of the degree of Master of Computer Applications.', 'normal'),
             P('The project has been carried out under my supervision and guidance during the academic year ' + YEAR + '. The report has not been submitted elsewhere for the award of any degree or diploma.', 'normal')]
    flow(c, items, H - 1.5 * cm, 7.2 * cm)
    t = Table([[P(GUIDE, 'bold_center'), P(HOD, 'bold_center')], [P('Internal Guide', 'center'), P('Head of the Department', 'center')]], colWidths=[7.5 * cm, 7.5 * cm])
    t.wrapOn(c, CONTENT_W, 3 * cm)
    t.drawOn(c, LEFT, 4.5 * cm)
    c.showPage()


def declaration(c):
    items = [P('DECLARATION', 'chapter'),
             P('I, the undersigned, hereby declare that the project report <b>"' + TITLE + '"</b> submitted for partial fulfilment of the requirements for the award of the degree of Master of Computer Applications of ' + UNIV + ' is a record of my original project work.', 'normal'),
             P('This report is prepared in my own words and all sources used for study, comparison, implementation, and reference have been acknowledged properly. I have followed the principles of academic honesty and integrity and have not misrepresented, fabricated, or copied any data, idea, or implementation detail in this submission.', 'normal'),
             P('I understand that any violation of the above will be a cause for disciplinary action by the institute and/or the university.', 'normal'),
             P('<br/><br/><br/>Place: THIRUVANANTHAPURAM<br/>Date:', 'normal'), P('<br/><br/>' + STUDENT, 'right')]
    flow(c, items)
    c.showPage()


def acknowledgement(c):
    paras = [
        'An endeavour over a long time can be successful only with the advice, encouragement, and support of many well-wishers. I place on record my sincere gratitude to all those who directly or indirectly contributed to the successful completion of this project work.',
        'At the outset, I thank God Almighty for the strength, guidance, and blessings received throughout the period of this Master of Computer Applications project.',
        'I express my sincere gratitude to the Director, Principal, and the Department of Computer Applications of Lourdes Matha College of Science and Technology for providing the facilities, support, and academic environment required for completing this project.',
        'I am especially thankful to ' + GUIDE + ', my internal guide, for her valuable guidance, constant support, and constructive suggestions during the various stages of development and documentation.',
        'I also thank ' + HOD + ', Head of the Department, and all faculty members of the Department of Computer Applications for their encouragement and support. Finally, I thank my friends and family for their motivation and cooperation.'
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
        P(title, 'chapter'),
        P('This chapter introduces the related part of the DayTone project and explains its role in the overall system. The discussion is written in the same academic report style as the reference project, but the content is adapted to DayTone, an AI-assisted mental wellness tracker and burnout prediction platform.', 'normal'),
        P('The chapter connects theory with implementation. It describes why the topic is required, how it is handled in the application, which technologies are involved, and how the output supports users or administrators. This helps the reader understand the project as a working software system rather than only a list of features.', 'normal'),
        P('The project repeatedly focuses on privacy, usability, maintainability, and explainable wellness feedback. Therefore, each chapter explains not only what the application does, but also why that design choice is suitable for a mental wellness tracking system.', 'normal'),
    ]
    for para in expansion_for(title)[:3]:
        items.append(P(para, 'normal_tight'))
    return items

def section_content(key):
    data = {
        'ABSTRACT': [
            'DayTone is an AI-assisted mental wellness tracking web application designed to help users record daily mood, sleep, stress, activity, social interaction, and journal reflections. The system applies local Natural Language Processing and Machine Learning to detect emotional patterns, classify burnout risk, and provide meaningful wellness insights while preserving user privacy. ' + base_paragraph('abstract'),
            'The application is developed using Python Flask for the backend, SQLAlchemy for database handling, Scikit-learn for burnout prediction, NLTK VADER for sentiment analysis, Bootstrap and Jinja templates for the interface, and Chart.js, D3.js, and Three.js for interactive visualizations. DayTone also includes secure authentication, encrypted journal storage, PDF/CSV export, admin analytics, reminder emails, audit logs, model monitoring, and Progressive Web App support.',
            'By combining daily self-reporting, local text analysis, burnout classification, and visual dashboards, DayTone provides a practical and privacy-conscious platform for early self-awareness and proactive wellness management. The project is intended as an academic wellness-support system and not as a clinical diagnostic tool.'
        ],
        '1.1 GENERAL INTRODUCTION': [
            'Mental wellness has become an important concern among students and professionals because stress, lack of sleep, academic pressure, social isolation, and continuous screen time can gradually lead to burnout. Many people notice these patterns only after the problem becomes severe. A digital wellness tracker can help users observe daily habits, identify negative trends, and take preventive action. ' + base_paragraph('intro'),
            'DayTone records day-to-day wellness data and converts it into understandable insights. Instead of only storing notes, the system evaluates numerical check-in values and journal text to generate sentiment scores, burnout risk levels, dashboard charts, history records, and personal suggestions.',
            'The system focuses on privacy-first implementation. Journal notes can be encrypted at rest, sentiment analysis is performed locally, and users can export or delete their records. These design choices make the project suitable for academic demonstration of ethical software design.'
        ],
        '1.2 GOAL OF THE PROJECT': [
            'The goal of DayTone is to provide a simple, useful, and secure wellness monitoring system that encourages daily self-reflection and early burnout awareness. The system does not replace professional care, but it helps users recognize repeated negative patterns in sleep, stress, activity, mood, and personal reflections. ' + base_paragraph('goal'),
            'The project aims to combine a friendly interface with intelligent analysis. The user should be able to enter a daily log, immediately view the effect of the log in dashboard charts, and understand whether the pattern suggests Low, Medium, or High burnout risk.',
            'Another goal is to show how academic machine learning systems can be implemented responsibly. The report clearly identifies the limits of synthetic training data and treats DayTone as a wellness-awareness platform rather than a clinical decision system.'
        ],
        '2.1 STUDY OF SIMILAR WORKS': [
            'Existing wellness systems include journal applications, habit trackers, meditation tools, and mood diary platforms. These tools are useful for recording personal experiences but often provide limited analysis. Most applications require users to manually interpret their own mood trends and do not provide burnout prediction. ' + base_paragraph('similar works'),
            'Research in sentiment analysis shows that text reflections contain useful emotional indicators. Lexicon-based tools such as VADER are lightweight and suitable for real-time local analysis. Machine Learning models such as Decision Tree, Logistic Regression, and Random Forest can classify risk patterns when provided with structured features such as mood, sleep, stress, and rolling averages.',
            'DayTone takes inspiration from these systems but combines multiple features into a single academic prototype: journal analysis, structured daily check-ins, local prediction, visual dashboards, data export, user goals, admin analytics, audit logs, and privacy controls.'
        ],
        '2.2 EXISTING SYSTEM': [
            'The existing method for wellness monitoring is usually manual logging in notebooks, spreadsheets, or basic mobile apps. These systems store user inputs but provide only simple summaries. In many cases, the user must manually compare dates and interpret patterns without support from an intelligent model. ' + base_paragraph('existing'),
            'Some commercial platforms provide analytics, but they often depend on proprietary cloud processing. This can create privacy concerns when the user records sensitive personal reflections. They may also lack transparent explanation of how risk or recommendation scores are generated.',
            'In institutional settings, counsellors or mentors may manually review records. This process is slow and subjective, and it becomes difficult when many users submit daily logs. A structured web application can reduce this burden and make the workflow more consistent.'
        ],
        '2.3 DRAWBACKS OF EXISTING SYSTEM': [
            'Although existing systems support basic logging, they are not sufficient for a privacy-aware intelligent wellness platform. They either lack predictive power, lack security controls, or lack meaningful visual analytics. ' + base_paragraph('drawbacks'),
            'Most diary applications store entries but do not classify burnout risk. Habit trackers may show streaks but do not interpret emotional state. Cloud-based AI tools may process sensitive data outside the user environment. These gaps reduce user trust and limit practical usefulness.',
            'DayTone addresses these drawbacks by combining structured metrics, journal sentiment, rolling seven-day features, ML prediction, encrypted storage, export tools, and dashboards in one system.'
        ],
        '3.1 PROPOSED SYSTEM': [
            'The proposed system, DayTone, is a Flask-based mental wellness tracker that allows registered users to submit daily logs and view personalized analytics. The backend computes sentiment from journal notes, extracts behavioural features, predicts burnout risk, stores history, and generates suggestions. ' + base_paragraph('proposed'),
            'The frontend displays charts, heatmaps, risk status, goals, history, and a WebGL mood orb. Administrators can monitor users, audit logs, invite tokens, model feedback, and platform analytics. The system therefore combines user self-care features with administrative tools.',
            'The proposed system also supports privacy and accountability. Passwords are hashed, forms are CSRF-protected, journal notes can be encrypted, and important administrator actions are recorded in audit logs.'
        ],
        '3.2 FEATURES OF PROPOSED SYSTEM': [
            'DayTone combines daily logging, analysis, visualization, security, and export features in one application. The system is modular, so each function is handled by a separate blueprint or utility module. ' + base_paragraph('features'),
            'Important user features include registration, login, profile settings, daily mood log, dashboard charts, history page, goals, heatmap, PDF report export, and CSV export. These features make the application useful for regular self-monitoring.',
            'Important administrative features include user list, user detail page, audit log, invite tokens, bias audit, developer dashboard, model feedback review, and high-level analytics. These pages help maintain the platform responsibly.'
        ],
        '3.3 FUNCTIONS OF PROPOSED SYSTEM': [
            'The system performs user authentication, daily wellness data collection, sentiment scoring, burnout risk prediction, suggestion generation, visual analytics, history tracking, report generation, and administrator monitoring. ' + base_paragraph('functions'),
            'When a user submits a daily log, the Flask route validates the values, stores the record, analyses the journal note with VADER, creates a feature vector, executes the prediction module, stores the prediction history, and displays updated dashboard values.',
            'For administrators, DayTone supports user search, user detail inspection, audit log review, model feedback monitoring, and bias audit reporting. These functions are important for academic demonstration and future production readiness.'
        ],
        '3.4 REQUIREMENT SPECIFICATIONS': [
            'The requirement specification defines the technologies, data, security controls, and user operations needed for DayTone. The system must be easy enough for daily use and strong enough to protect personal wellness records. ' + base_paragraph('requirements'),
            'Frontend requirements include HTML, CSS, Bootstrap, JavaScript, Chart.js, D3.js, and Three.js. Backend requirements include Python Flask, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Limiter, Flask-Mail, SQLAlchemy, Scikit-learn, NLTK VADER, and ReportLab.',
            'The system also requires secure configuration through environment variables, a database for persistent storage, migrations for schema changes, and deployment support through Gunicorn, Docker, Redis, and PostgreSQL when used in production.'
        ],
        '3.5 FEASIBILITY ANALYSIS': [
            'Feasibility analysis studies whether the proposed system can be built, operated, maintained, and accepted by users. DayTone is feasible because it uses open-source tools, a simple interface, lightweight processing, and a modular design. ' + base_paragraph('feasibility'),
            'The project can be developed and tested on a normal laptop. It can later be deployed using a web service, database, and Redis-backed rate limiting. This makes it suitable for a student project and for future improvement.',
            'The major feasibility aspects considered are technical feasibility, operational feasibility, economic feasibility, and behavioural feasibility.'
        ],
    }
    default = [
        key.title() + ' is an important part of the DayTone project report. This section explains how the selected concept supports the overall objective of creating a secure, privacy-aware, AI-assisted mental wellness tracker. ' + base_paragraph(key),
        'In this part of the project, the design decisions are connected to practical implementation. The section describes the role of the module, its interaction with other modules, the data it uses, and the expected result produced for users or administrators.',
        'The same design philosophy is followed throughout DayTone: keep sensitive data protected, keep the interface simple, keep prediction results explainable, and keep the codebase maintainable for future enhancement.'
    ]
    paras = list(data.get(key, default))
    for extra in expansion_for(key):
        if len(paras) >= 7:
            break
        paras.append(extra)
    return paras


def bullets_for(key):
    return [
        'Supports the overall DayTone workflow and academic project objective.',
        'Uses modular implementation so the feature can be tested and maintained separately.',
        'Maintains focus on privacy, usability, reliable processing, and clear user feedback.',
        'Can be enhanced in future versions as more validated data and user feedback become available.'
    ]


plan = [
    ('section', 'ABSTRACT', 'ABSTRACT'),
    ('chapter', 'CHAPTER - 1  1. INTRODUCTION', 'INTRODUCTION'),
    ('section', '1.1 GENERAL INTRODUCTION', '1.1 GENERAL INTRODUCTION'),
    ('section', '1.2 GOAL OF THE PROJECT', '1.2 GOAL OF THE PROJECT'),
    ('chapter', 'CHAPTER - 2  2. LITERATURE SURVEY', 'LITERATURE SURVEY'),
    ('section', '2.1 STUDY OF SIMILAR WORKS', '2.1 STUDY OF SIMILAR WORKS'),
    ('section', '2.2 EXISTING SYSTEM', '2.2 EXISTING SYSTEM'),
    ('section', '2.3 DRAWBACKS OF EXISTING SYSTEM', '2.3 DRAWBACKS OF EXISTING SYSTEM'),
    ('chapter', 'CHAPTER - 3  3. OVERALL DESCRIPTION', 'OVERALL DESCRIPTION'),
    ('section', '3.1 PROPOSED SYSTEM', '3.1 PROPOSED SYSTEM'),
    ('section', '3.2 FEATURES OF PROPOSED SYSTEM', '3.2 FEATURES OF PROPOSED SYSTEM'),
    ('section', '3.3 FUNCTIONS OF PROPOSED SYSTEM', '3.3 FUNCTIONS OF PROPOSED SYSTEM'),
    ('section', '3.4 REQUIREMENT SPECIFICATIONS', '3.4 REQUIREMENT SPECIFICATIONS'),
    ('section', '3.5 FEASIBILITY ANALYSIS', '3.5 FEASIBILITY ANALYSIS'),
    ('section', '3.5.1 TECHNICAL FEASIBILITY', '3.5.1 TECHNICAL FEASIBILITY'),
    ('section', '3.5.2 OPERATIONAL FEASIBILITY', '3.5.2 OPERATIONAL FEASIBILITY'),
    ('section', '3.5.3 ECONOMIC FEASIBILITY', '3.5.3 ECONOMIC FEASIBILITY'),
    ('section', '3.5.4 BEHAVIOURAL FEASIBILITY', '3.5.4 BEHAVIOURAL FEASIBILITY'),
    ('chapter', 'CHAPTER - 4  4. OPERATING ENVIRONMENT', 'OPERATING ENVIRONMENT'),
    ('section', '4.1 HARDWARE REQUIREMENTS', '4.1 HARDWARE REQUIREMENTS'),
    ('section', '4.2 SOFTWARE REQUIREMENTS', '4.2 SOFTWARE REQUIREMENTS'),
    ('section', '4.3 TOOLS AND PLATFORMS', '4.3 TOOLS AND PLATFORMS'),
    ('section', '4.3.1 PYTHON', '4.3.1 PYTHON'),
    ('section', '4.3.2 FLASK', '4.3.2 FLASK'),
    ('section', '4.3.3 SQLALCHEMY / DATABASE', '4.3.3 SQLALCHEMY / DATABASE'),
    ('section', '4.3.4 SCIKIT-LEARN AND VADER', '4.3.4 SCIKIT-LEARN AND VADER'),
    ('section', '4.3.5 FRONTEND VISUALIZATION TOOLS', '4.3.5 FRONTEND VISUALIZATION TOOLS'),
    ('chapter', 'CHAPTER - 5  5. DESIGN', 'DESIGN'),
    ('section', '5.1 SYSTEM DESIGN', '5.1 SYSTEM DESIGN'),
    ('section', '5.2 DATA FLOW DIAGRAM', '5.2 DATA FLOW DIAGRAM'),
    ('section', '5.3 INPUT DESIGN', '5.3 INPUT DESIGN'),
    ('section', '5.4 OUTPUT DESIGN', '5.4 OUTPUT DESIGN'),
    ('section', '5.5 PROGRAM DESIGN', '5.5 PROGRAM DESIGN'),
    ('chapter', 'CHAPTER - 6  6. FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS', 'FUNCTIONAL AND NON-FUNCTIONAL REQUIREMENTS'),
    ('section', '6.1 FUNCTIONAL REQUIREMENTS', '6.1 FUNCTIONAL REQUIREMENTS'),
    ('section', '6.2 NON-FUNCTIONAL REQUIREMENTS', '6.2 NON-FUNCTIONAL REQUIREMENTS'),
    ('chapter', 'CHAPTER - 7  7. TESTING', 'TESTING'),
    ('section', '7.1 SYSTEM TESTING', '7.1 SYSTEM TESTING'),
    ('section', '7.2 UNIT TESTING', '7.2 UNIT TESTING'),
    ('section', '7.3 INTEGRATION TESTING', '7.3 INTEGRATION TESTING'),
    ('section', '7.4 BLACK BOX TESTING', '7.4 BLACK BOX TESTING'),
    ('section', '7.5 VALIDATION TESTING', '7.5 VALIDATION TESTING'),
    ('section', '7.6 OUTPUT TESTING', '7.6 OUTPUT TESTING'),
    ('section', '7.7 USER ACCEPTANCE TESTING', '7.7 USER ACCEPTANCE TESTING'),
    ('section', '7.8 MODEL TESTING', '7.8 MODEL TESTING'),
    ('chapter', 'CHAPTER - 8  8. RESULTS AND DISCUSSIONS', 'RESULTS AND DISCUSSIONS'),
    ('section', '8.1 RESULTS', '8.1 RESULTS'),
    ('section', '8.2 SCREENSHOTS', '8.2 SCREENSHOTS'),
    ('chapter', 'CHAPTER - 9  9. CONCLUSION', 'CONCLUSION'),
    ('section', '9.1 SYSTEM IMPLEMENTATION', '9.1 SYSTEM IMPLEMENTATION'),
    ('section', '9.2 SYSTEM MAINTENANCE', '9.2 SYSTEM MAINTENANCE'),
    ('section', '9.3 FUTURE ENHANCEMENT', '9.3 FUTURE ENHANCEMENT'),
    ('section', '9.4 CONCLUSION', '9.4 CONCLUSION'),
    ('chapter', 'CHAPTER - 10  10. BIBLIOGRAPHY', 'BIBLIOGRAPHY'),
    ('section', '10.1 REFERENCES', '10.1 REFERENCES'),
]

for i, entry in enumerate(plan, start=1):
    entry_page = i
    # tuple is immutable, rebuild with printed page
    plan[i - 1] = entry + (entry_page,)


def contents(c):
    rows = [[P('CONTENT', 'table_b'), P('Page No.', 'table_b')]]
    for kind, toc, heading, printed in plan:
        rows.append([P(toc, 'table'), P(str(printed), 'table')])
    chunks = [rows[:19], [rows[0]] + rows[19:37], [rows[0]] + rows[37:]]
    for chunk in chunks:
        page(c, [P('CONTENTS', 'chapter'), make_table(chunk, [13 * cm, 3 * cm])], None)


def chapter_page(c, title, printed):
    page(c, chapter_overview(title), printed)


def section_page(c, heading, printed):
    items = [P(heading, 'h1')]
    paras = section_content(heading)
    for para in paras:
        items.append(P(para, 'normal_tight'))
    if heading == '8.2 SCREENSHOTS':
        for fig in ['Figure 1: Login and registration screen', 'Figure 2: Daily wellness check-in form', 'Figure 3: User dashboard with mood trends', 'Figure 4: History, heatmap and report export', 'Figure 5: Admin dashboard and audit log']:
            t = Table([[P('<br/><br/>DAYTONE INTERFACE SCREEN<br/>' + fig, 'caption')]], colWidths=[15.8 * cm], rowHeights=[2.35 * cm])
            t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.8, colors.black), ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
            items.append(t)
            items.append(P(fig, 'caption'))
    elif heading in {'5.1 SYSTEM DESIGN', '5.2 DATA FLOW DIAGRAM', '5.3 INPUT DESIGN', '5.4 OUTPUT DESIGN'}:
        t = Table([[P('<br/><br/><br/>DAYTONE FIGURE AREA<br/>' + heading, 'caption')]], colWidths=[15.8 * cm], rowHeights=[4.3 * cm])
        t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.8, colors.black), ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        items.append(t)
    else:
        for b in bullets_for(heading):
            items.append(P('- ' + b, 'bullet'))
    page(c, items, printed)


def render_body(c):
    for kind, toc, heading, printed in plan:
        if kind == 'chapter':
            chapter_page(c, heading, printed)
        else:
            section_page(c, heading, printed)


def build():
    c = canvas.Canvas(str(OUT), pagesize=A4)
    title_page(c)
    certificate(c)
    declaration(c)
    acknowledgement(c)
    contents(c)
    render_body(c)
    c.save()
    print(OUT)


if __name__ == '__main__':
    build()
