# DayTone Wellness App — Participant Information & Informed Consent Form

**Project Title**: DayTone Daily Mood & Wellness Monitoring Pilot Study  
**Investigator**: [Your Name / Student ID]  
**Contact Email**: [Your Contact Email]  
**Application URL**: https://daytone-piyi.onrender.com  

---

## 1. Introduction & Purpose
You are invited to participate in a 2-to-4-week pilot evaluation of **DayTone**, a wellness-tracking application designed to help individuals monitor daily mood, sleep quality, stress levels, and identify early signs of burnout using local machine learning analytics. 

The purpose of this pilot is to gather real-world, anonymous wellness logs to validate and retrain the application’s scikit-learn machine learning classification model, replacing synthetic training data with real human insights.

## 2. What Data is Collected?
If you agree to participate, you will be asked to create an account and complete a brief check-in once a day. The check-in form collects:
*   **Wellness Metrics**: Daily mood score (1–5 scale), sleep duration (hours), stress level (1–5 scale), and daily physical activity completion (yes/no).
*   **Journal / Reflection (Optional)**: Short text notes describing your day.
*   **Account Details**: Your name/display name, email address, age, and occupation (used for demographic bias auditing).

## 3. How is Your Data Stored & Secured?
Your privacy is our highest priority. The following security measures are implemented:
*   **Encryption at Rest**: Any text written in your daily journal notes is automatically encrypted using **AES-256 (Fernet)** symmetric encryption before being saved to the database. Even database administrators cannot read your plain-text notes.
*   **No Third-Party Sharing**: Your data is stored on a secure, private cloud server (Render + PostgreSQL) and is **never** shared, sold, or sent to external parties or third-party AI services. All natural language processing (sentiment analysis) is performed locally.
*   **Anonymized ML Training**: When model training is performed, names and email addresses are entirely excluded.

## 4. Your Rights & GDPR Compliance
Your participation is entirely voluntary. Under GDPR regulations, you hold the following rights:
*   **Right to Withdraw**: You can stop participating at any time.
*   **Right to Erasure (Right to be Forgotten)**: You can permanently delete your account and all associated daily logs at any time via the **Settings / Profile** page. Deletion is instantaneous and Cascading (all databases records are completely wiped).

## 5. Disclaimer & Health Warning
> [!IMPORTANT]
> **DayTone is NOT a medical device, diagnostic tool, or clinical service.** 
> All ML burnout risk classifications and recommendations are informational only. If you are experiencing severe stress, depression, or a mental health crisis, please consult a qualified medical professional or contact crisis services (such as calling or texting **988** in the US/Canada, calling the Kiran national helpline at **1800-599-0019** in India, or contacting local emergency services).

---

## Informed Consent Agreement

By registering an account and checking in on the DayTone application, you confirm that:
1.  You have read and understood this participant information sheet.
2.  You are at least **13 years of age** (required for Terms of Service compliance).
3.  You voluntarily consent to log your wellness data for the duration of this study.
4.  You understand that you can delete your account and all data at any time.
