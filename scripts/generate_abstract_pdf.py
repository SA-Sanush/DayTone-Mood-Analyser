import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def generate_pdf():
    # Set output path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(base_dir, "DayTone_Abstract.pdf")
    
    # Page setup - 0.75 inch margins (54 points) to guarantee single-page fit
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
    
    # Custom styles matching the screenshot
    style_header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4A727A") # Slate teal color
    )
    
    style_abstract_title = ParagraphStyle(
        'AbstractTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1B2A27") # Dark charcoal green
    )
    
    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#1B2A27"),
        spaceBefore=8,
        spaceAfter=3
    )
    
    style_body_text = ParagraphStyle(
        'BodyTextJustify',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#2C3E3A"), # Off-black green tint
        spaceAfter=8
    )
    
    style_footer_name = ParagraphStyle(
        'FooterName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1B2A27")
    )
    
    style_footer_mca = ParagraphStyle(
        'FooterMCA',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#609488") # Soft teal mint
    )
    
    story = []
    
    # 1. Top Header Title
    story.append(Paragraph("PROJECT TITLE : DAYTONE – AN AI-POWERED MENTAL WELLNESS TRACKER", style_header_title))
    story.append(Spacer(1, 6))
    
    # 2. Top Line
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1B2A27"), spaceBefore=0, spaceAfter=12))
    
    # 3. ABSTRACT Heading
    story.append(Paragraph("ABSTRACT", style_abstract_title))
    story.append(Spacer(1, 8))
    
    # 4. Background Section
    story.append(Paragraph("Background", style_section_heading))
    story.append(Paragraph(
        "The growing emphasis on mental health awareness has highlighted a critical gap in accessible, personalized, "
        "and data-driven wellness tools. Burnout, stress, and emotional deterioration have become prevalent issues "
        "among students, professionals, and individuals in high-pressure environments. Despite the widespread use "
        "of digital journaling and mood-tracking apps, most existing solutions offer only surface-level logging without "
        "meaningful analysis, risk assessment, or actionable guidance, making proactive mental wellness management difficult.",
        style_body_text
    ))
    
    # 5. Limitations Section
    story.append(Paragraph("Limitations of Existing Systems", style_section_heading))
    story.append(Paragraph(
        "Existing mental health applications typically function as isolated diary or mood-logging tools. They lack "
        "machine learning-based predictive capabilities, offer no sentiment analysis of journal entries, and provide no "
        "automated burnout risk classification. Users must manually interpret their own patterns without data-driven "
        "insights, personalized recommendations, or visual analytics. Furthermore, these tools do not integrate "
        "multiple wellness dimensions — such as sleep quality, stress intensity, physical activity, and social "
        "interaction — into a unified assessment, leaving significant blind spots in mental health monitoring.",
        style_body_text
    ))
    
    # 6. Proposed System Section
    story.append(Paragraph("Proposed System — DayTone", style_section_heading))
    story.append(Paragraph(
        "To address these limitations, DayTone is developed as a rule-based intelligent mental wellness tracker "
        "integrating Natural Language Processing (NLP), Machine Learning (ML), and interactive data visualization "
        "into a single web environment. Users submit daily wellness logs capturing mood score, sleep hours, stress "
        "level, physical activity, and social interaction, plus optional journal notes. Inputs pass through two pipelines: "
        "(1) VADER sentiment analysis (NLTK), which scores journal text from -1.0 to +1.0; and (2) a Random Forest "
        "classifier trained on synthetic data, evaluating twelve behavioral features — seven-day rolling averages of "
        "mood, sleep, stress; mood variability; bad-day streaks; weekend flags — to predict burnout risk as Low, "
        "Medium, or High.",
        style_body_text
    ))
    story.append(Paragraph(
        "The dashboard presents five Chart.js visualizations (mood timeline, sleep bars, stress trend, sleep-mood "
        "scatter, burnout doughnut), a D3.js GitHub-style mood heatmap, and a Three.js WebGL 3D Mood Orb "
        "animated in real time. A rule-based suggestions engine delivers personalized daily 'Do' and 'Don't' tips. "
        "Additional features include PDF reports (ReportLab), streamed CSV export, email reminders, high-risk admin "
        "alerts, and a full admin analytics dashboard.",
        style_body_text
    ))
    
    # 7. User Roles & Security Section
    story.append(Paragraph("User Roles & Security", style_section_heading))
    story.append(Paragraph(
        "DayTone supports two user categories: Regular Users, who log daily wellness data, view dashboards and "
        "history, and export reports; and Administrators, who manage users, review platform analytics, edit logs, "
        "and monitor high-risk alerts. Security includes CSRF protection (Flask-WTF), scrypt password hashing, "
        "Content Security Policy headers (Flask-Talisman), hardened session cookies (HttpOnly, SameSite=Lax, 8-hour "
        "lifetime), login rate limiting (Flask-Limiter), and a 2 MB request size cap.",
        style_body_text
    ))
    
    # 8. Technology Stack Section
    story.append(Paragraph("Technology Stack & Conclusion", style_section_heading))
    story.append(Paragraph(
        "DayTone is developed using Python and Flask as the backend framework, SQLAlchemy with SQLite for "
        "database management, Scikit-learn for the Random Forest ML pipeline, NLTK (VADER) for sentiment "
        "analysis, ReportLab for PDF generation, Chart.js, D3.js, and Three.js for front-end visualization, and "
        "Bootstrap, HTML, CSS, and JavaScript for the responsive interface. By integrating NLP, ML, and "
        "visual analytics into a single environment, DayTone simplifies wellness management and enables early "
        "identification of emotional health risks.",
        style_body_text
    ))
    
    # 9. Bottom Line
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1B2A27"), spaceBefore=10, spaceAfter=8))
    
    # 10. Footer S A Sanush
    story.append(Paragraph("S A Sanush", style_footer_name))
    story.append(Paragraph("S3 MCA", style_footer_mca))
    
    # Build PDF
    doc.build(story)
    print(f"PDF abstract saved to: {pdf_path}")

if __name__ == '__main__':
    generate_pdf()
