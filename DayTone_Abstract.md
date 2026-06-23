# PROJECT TITLE : DAYTONE – AN AI-POWERED MENTAL WELLNESS TRACKER

---
## ABSTRACT
---

### Background
The growing emphasis on mental health awareness has highlighted a critical gap in accessible, personalized, and data-driven wellness tools. Burnout, stress, and emotional deterioration have become prevalent issues among students, professionals, and individuals in high-pressure environments. Despite the widespread use of digital journaling and mood-tracking apps, most existing solutions offer only surface-level logging without meaningful analysis, risk assessment, or actionable guidance, making proactive mental wellness management difficult.

### Limitations of Existing Systems
Existing mental health applications typically function as isolated diary or mood-logging tools. They lack machine learning-based predictive capabilities, offer no sentiment analysis of journal entries, and provide no automated burnout risk classification. Users must manually interpret their own patterns without data-driven insights, personalized recommendations, or visual analytics. Furthermore, these tools do not integrate multiple wellness dimensions — such as sleep quality, stress intensity, physical activity, and social interaction — into a unified assessment, leaving significant blind spots in mental health monitoring.

### Proposed System — DayTone
To address these limitations, DayTone is developed as a rule-based intelligent mental wellness tracker integrating Natural Language Processing (NLP), Machine Learning (ML), and interactive data visualization into a single web environment. Users submit daily wellness logs capturing mood score, sleep hours, stress level, physical activity, and social interaction, plus optional journal notes. Inputs pass through two pipelines: 
1. **VADER sentiment analysis (NLTK):** Scores journal text from -1.0 to +1.0.
2. **Random Forest Classifier:** Trained on synthetic data, evaluating twelve behavioral features — seven-day rolling averages of mood, sleep, stress; mood variability; bad-day streaks; weekend flags — to predict burnout risk as Low, Medium, or High.

The dashboard presents five Chart.js visualizations (mood timeline, sleep bars, stress trend, sleep-mood scatter, burnout doughnut), a D3.js GitHub-style mood heatmap, and a Three.js WebGL 3D Mood Orb animated in real time. A rule-based suggestions engine delivers personalized daily 'Do' and 'Don't' tips. Additional features include PDF reports (ReportLab), streamed CSV export, email reminders, high-risk admin alerts, and a full admin analytics dashboard.

### User Roles & Security
DayTone supports two user categories:
* **Regular Users:** Log daily wellness data, view dashboards and history, and export reports.
* **Administrators:** Manage users, review platform analytics, edit logs, and monitor high-risk alerts.

Security includes CSRF protection (Flask-WTF), scrypt password hashing, Content Security Policy headers (Flask-Talisman), hardened session cookies (HttpOnly, SameSite=Lax, 8-hour lifetime), login rate limiting (Flask-Limiter), and a 2 MB request size cap.

### Technology Stack & Conclusion
DayTone is developed using **Python and Flask** as the backend framework, **SQLAlchemy with SQLite** for database management, **Scikit-learn** for the Random Forest ML pipeline, **NLTK (VADER)** for sentiment analysis, **ReportLab** for PDF generation, **Chart.js, D3.js, and Three.js** for front-end visualization, and **Bootstrap, HTML, CSS, and JavaScript** for the responsive interface. By integrating NLP, ML, and visual analytics into a single environment, DayTone simplifies wellness management and enables early identification of emotional health risks.

---
**S A Sanush**  
**S3 MCA**  
---
