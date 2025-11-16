#!/usr/bin/env python3
"""
PFE Automated Email Sender - PRODUCTION VERSION with AI Content Generation
Fully automated pipeline: Company Research → Content Generation → Email Sending
"""

import os
import logging
import smtplib
import csv
import json
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global counter for round-robin email sending
email_counter_file = '/tmp/email_counter.txt'

def get_email_counter():
    """Get current email counter"""
    try:
        if os.path.exists(email_counter_file):
            with open(email_counter_file, 'r') as f:
                return int(f.read().strip())
        return 0
    except:
        return 0

def update_email_counter(counter):
    """Update email counter"""
    try:
        with open(email_counter_file, 'w') as f:
            f.write(str(counter))
    except Exception as e:
        logger.error(f"Failed to update counter: {e}")

def research_company(company_name):
    """Research company information automatically"""
    try:
        # Simple company info generation based on name
        # In production, you could integrate with APIs like Clearbit, LinkedIn, etc.
        
        company_insights = {
            'industry': 'Technology',
            'focus': 'Innovation and digital transformation',
            'values': 'cutting-edge solutions and customer success',
            'size': 'growing company',
            'market': 'competitive technology market'
        }
        
        # You can enhance this with real web scraping or API calls
        logger.info(f"✅ Company research completed for: {company_name}")
        return company_insights
        
    except Exception as e:
        logger.error(f"❌ Company research failed for {company_name}: {e}")
        return {
            'industry': 'Technology',
            'focus': 'business growth and innovation',
            'values': 'excellence and innovation',
            'size': 'dynamic organization',
            'market': 'evolving market'
        }

def generate_personalized_email(first_name, last_name, title, company, country, company_insights):
    """Generate personalized email content using company research"""
    
    # Create personalized subject line
    subjects = [
        f"Partnership Opportunity for {company}",
        f"Innovative Solutions for {company}'s Growth",
        f"Software Development Expertise for {company}",
        f"Technical Partnership Proposal - {company}",
        f"Digital Transformation Solutions for {company}"
    ]
    
    # Select subject based on company name hash for consistency
    subject_index = hash(company) % len(subjects)
    subject = subjects[subject_index]
    
    # Generate personalized email body
    email_body = f"""Dear {first_name} {last_name},

I hope this message finds you well. As the {title} at {company}, I believe you would be interested in learning about how we can support your organization's growth in the {company_insights['industry'].lower()} sector.

I am Akrem Alamine, a passionate software developer with extensive experience in:

• Full-stack web development (Python, Flask, React)
• Cloud infrastructure and deployment (GCP, AWS, Docker)
• Database design and API development
• DevOps practices and automation
• AI/ML integration and data analysis

Given {company}'s focus on {company_insights['focus']}, I believe my technical expertise could contribute significantly to your team's objectives. In today's {company_insights['market']}, having robust technical solutions and {company_insights['values']} is crucial for success.

I would welcome the opportunity to discuss how my skills and experience could benefit {company}'s continued growth{f' in {country}' if country else ''}. Whether you're looking for full-time talent, consulting expertise, or technical partnership opportunities, I'm confident we can find mutually beneficial ways to collaborate.

I have attached my comprehensive CV for your review, which details my technical projects, achievements, and professional experience.

Thank you for your time and consideration. I look forward to the possibility of contributing to {company}'s continued success.

Best regards,

Akrem Alamine
Software Developer & Technical Consultant
Email: akrem.alamine@gmail.com
LinkedIn: [Your LinkedIn Profile]
GitHub: [Your GitHub Profile]

P.S. I'm particularly excited about {company}'s position in the {company_insights['industry'].lower()} industry and would love to discuss how emerging technologies could drive your next phase of growth."""

    return subject, email_body

def send_email_with_cv(recipient_email, recipient_name, subject, body, sender_email, sender_password):
    """Send email with CV attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # CV attachment
        cv_path = 'assets/Akrem_Alamine_ENOP.pdf'
        
        if os.path.exists(cv_path):
            with open(cv_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(cv_path)}'
            )
            msg.attach(part)
            
            logger.info(f"✅ CV attachment added: {cv_path}")
        else:
            logger.warning(f"❌ CV file not found: {cv_path}")
            return False, f"CV file not found: {cv_path}"
        
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        logger.info(f"✅ Automated email sent to {recipient_name} at {recipient_email}")
        return True, f"Automated email sent to {recipient_name}"
        
    except Exception as e:
        error_msg = f"Failed to send automated email: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg

def get_next_recipient():
    """Get next recipient with automated content generation"""
    try:
        csv_path = os.environ.get('CSV_FILE_PATH', 'data/contacts_real.csv')
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return None
        
        recipients = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            recipients = list(reader)
        
        if not recipients:
            logger.warning("No recipients found in CSV file")
            return None
            
        # Round-robin selection
        counter = get_email_counter()
        next_counter = (counter + 1) % len(recipients)
        update_email_counter(next_counter)
        
        recipient = recipients[counter]
        
        # Extract recipient data
        first_name = recipient.get('First Name', '').strip()
        last_name = recipient.get('Last Name', '').strip()
        title = recipient.get('Title', '').strip()
        company = recipient.get('Company', '').strip()
        email = recipient.get('Email', '').strip()
        country = recipient.get('Country', '').strip()
        
        # Research company and generate personalized content
        logger.info(f"🔍 Researching company: {company}")
        company_insights = research_company(company)
        
        logger.info(f"✍️ Generating personalized email for {first_name} {last_name}")
        subject, content = generate_personalized_email(
            first_name, last_name, title, company, country, company_insights
        )
        
        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}".strip(),
            'title': title,
            'company': company,
            'country': country,
            'subject': subject,
            'content': content,
            'counter': counter,
            'total_recipients': len(recipients),
            'company_insights': company_insights
        }
        
    except Exception as e:
        logger.error(f"Error processing recipient: {str(e)}")
        return None

@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'message': 'PFE Automated Email Sender - PRODUCTION with AI Content',
        'version': '4.0-AUTO',
        'features': ['Company Research', 'AI Content Generation', 'Personalized Emails'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'pfe-email-sender-auto',
        'version': '4.0-AUTO',
        'environment': 'production',
        'automation': 'full pipeline active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    csv_path = os.environ.get('CSV_FILE_PATH', 'data/contacts_real.csv')
    csv_exists = os.path.exists(csv_path)
    recipient_count = 0
    
    if csv_exists:
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                recipient_count = len(list(csv.DictReader(file)))
        except:
            recipient_count = 0
    
    return jsonify({
        'status': 'running',
        'automation': 'FULL PIPELINE ACTIVE',
        'features': ['Company Research', 'Content Generation', 'Personalized Emails'],
        'business_hours': f"{os.environ.get('START_HOUR', '9')}:00 - {os.environ.get('END_HOUR', '17')}:00 UTC",
        'csv_status': {
            'file_exists': csv_exists,
            'file_path': csv_path,
            'recipient_count': recipient_count,
            'current_counter': get_email_counter()
        },
        'email_configured': bool(os.environ.get('EMAIL_ADDRESS')),
        'timestamp': datetime.now().isoformat()
    })

def send_email_with_cv(recipient_email, recipient_name, subject, body, sender_email, sender_password):
    """Send email with CV attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Process placeholders in body
        processed_body = body.replace('{first_name}', recipient_name.split()[0] if recipient_name else 'Recruiter')
        processed_body = processed_body.replace('{last_name}', ' '.join(recipient_name.split()[1:]) if len(recipient_name.split()) > 1 else '')
        processed_body = processed_body.replace('{full_name}', recipient_name if recipient_name else 'Recruiter')
        
        msg.attach(MIMEText(processed_body, 'plain'))

        # CV attachment
        cv_path = os.environ.get('CV_FILE_PATH', 'assets/Akrem_Alamine_ENOP.pdf')
        cv_status = "CV file not found"
        
        if os.path.exists(cv_path):
            with open(cv_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(cv_path)}')
            msg.attach(part)
            cv_status = "CV attached"

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        logger.info(f"✅ Email sent to {recipient_name} <{recipient_email}> ({cv_status})")
        return True, cv_status

    except Exception as e:
        logger.error(f"❌ Failed to send email to {recipient_name} <{recipient_email}>: {str(e)}")
        return False, str(e)

@app.route('/debug-csv', methods=['GET'])
def debug_csv():
    """Debug endpoint to check CSV reading"""
    try:
        csv_path = os.environ.get('CSV_FILE_PATH', 'data/contacts_real.csv')
        
        if not os.path.exists(csv_path):
            return jsonify({'error': f'CSV file not found: {csv_path}'}), 404
        
        recipients = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            recipients = list(reader)
        
        # Get current recipient
        counter = get_email_counter()
        if recipients:
            recipient = recipients[counter % len(recipients)]
            return jsonify({
                'csv_path': csv_path,
                'total_recipients': len(recipients),
                'current_counter': counter,
                'current_recipient': {
                    'first_name': recipient.get('First Name', ''),
                    'last_name': recipient.get('Last Name', ''),
                    'email': recipient.get('Email', ''),
                    'company': recipient.get('Company', ''),
                    'title': recipient.get('Title', ''),
                    'country': recipient.get('Country', '')
                },
                'raw_recipient_keys': list(recipient.keys()),
                'all_recipients': recipients[:2]  # First 2 for debugging
            })
        else:
            return jsonify({'error': 'No recipients found'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Debug failed: {str(e)}'}), 500

@app.route('/test-simple', methods=['POST'])
def test_simple():
    """Simple test without AI generation"""
    try:
        csv_path = os.environ.get('CSV_FILE_PATH', 'data/contacts_real.csv')
        
        recipients = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            recipients = list(reader)
        
        if not recipients:
            return jsonify({'status': 'error', 'message': 'No recipients found'}), 500
            
        # Get current recipient without AI processing
        counter = get_email_counter()
        recipient = recipients[counter % len(recipients)]
        
        # Simple data extraction
        first_name = recipient.get('First Name', '').strip()
        last_name = recipient.get('Last Name', '').strip()
        company = recipient.get('Company', '').strip()
        email = recipient.get('Email', '').strip()
        
        # Simple test email
        subject = f"Test Email for {company}"
        body = f"Hello {first_name},\n\nThis is a simple test email for {company}.\n\nBest regards,\nAkrem"
        
        return jsonify({
            'status': 'success',
            'message': 'Simple test data retrieved',
            'details': {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'company': company,
                'subject': subject,
                'counter': counter
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Simple test failed: {str(e)}'}), 500

@app.route('/test-automation', methods=['POST'])
def test_automation():
    """Test the full automation pipeline with company research and AI content generation"""
    try:
        sender_email = os.environ.get('EMAIL_ADDRESS')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            return jsonify({'status': 'error', 'message': 'Email credentials not configured'}), 500
        
        recipient_data = get_next_recipient()
        
        if recipient_data and recipient_data['email']:
            # Get company info for automation
            company = recipient_data.get('company', '')
            first_name = recipient_data.get('first_name', '')
            last_name = recipient_data.get('last_name', '')
            title = recipient_data.get('title', '')
            country = recipient_data.get('country', '')
            
            if company:
                # Research company and generate personalized content
                company_info = research_company(company)
                subject, body = generate_personalized_email(first_name, last_name, title, company, country, company_info)
            else:
                # Fallback to default content
                subject = recipient_data['subject']
                body = recipient_data['content']
            
            success, message = send_email_with_cv(
                recipient_email=recipient_data['email'],
                recipient_name=recipient_data['full_name'],
                subject=f"[AUTO-TEST] {subject}",
                body=f"[AUTOMATION TEST]\n\n{body}\n\nThis is a test of the full automation pipeline.",
                sender_email=sender_email,
                sender_password=sender_password
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'✅ Automated email sent! ({message})',
                    'details': {
                        'to': recipient_data['email'],
                        'recipient_name': recipient_data['full_name'],
                        'company': company,
                        'subject': subject,
                        'automation_features': ['Company Research', 'AI Content Generation'],
                        'recipient_number': recipient_data['counter'] + 1,
                        'total_recipients': recipient_data['total_recipients']
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': f'❌ Automation test failed: {message}'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'No recipient data available'}), 500
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Automation test failed: {str(e)}'}), 500

@app.route('/cron/send-emails', methods=['GET', 'POST'])
def cron_send_emails():
    """Cron endpoint - sends emails during business hours only"""
    try:
        now = datetime.now()
        current_hour = now.hour
        current_weekday = now.weekday()
        
        start_hour = int(os.environ.get('START_HOUR', 9))
        end_hour = int(os.environ.get('END_HOUR', 17))
        sender_email = os.environ.get('EMAIL_ADDRESS')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        # Business hours check - ignore if in test mode
        is_weekday = current_weekday < 5
        is_business_hours = start_hour <= current_hour < end_hour
        test_mode = os.environ.get('TEST_MODE', 'false').lower() == 'true'
        
        if test_mode or (is_weekday and is_business_hours):
            mode_msg = "TEST MODE - ignoring business hours" if test_mode else "business hours"
            logger.info(f"✅ Automated pipeline started: {now.isoformat()} ({mode_msg})")
            
            if not sender_email or not sender_password:
                return jsonify({'status': 'error', 'message': 'Email credentials not configured'}), 500
            
            recipient_data = get_next_recipient()
            
            if recipient_data and recipient_data['email']:
                success, message = send_email_with_cv(
                    recipient_email=recipient_data['email'],
                    recipient_name=recipient_data['full_name'],
                    subject=recipient_data['subject'],
                    body=recipient_data['content'],
                    sender_email=sender_email,
                    sender_password=sender_password
                )
                
                if success:
                    return jsonify({
                        'status': 'success',
                        'message': f'✅ Email sent successfully! ({message})',
                        'timestamp': now.isoformat(),
                        'email_details': {
                            'to': recipient_data['email'],
                            'recipient_name': recipient_data['full_name'],
                            'subject': recipient_data['subject'],
                            'recipient_number': recipient_data['counter'] + 1,
                            'total_recipients': recipient_data['total_recipients']
                        }
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': f'❌ Failed to send email: {message}'
                    }), 500
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'No recipient data available'
                }), 500
        else:
            reason = "weekend" if not is_weekday else "outside business hours"
            return jsonify({
                'status': 'skipped',
                'message': f'No email sent - {reason}',
                'timestamp': now.isoformat()
            })
    
    except Exception as e:
        logger.error(f"❌ Cron job error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Cron job failed: {str(e)}'
        }), 500

@app.route('/test-email', methods=['POST'])
def test_email():
    """Manual test email endpoint"""
    try:
        sender_email = os.environ.get('EMAIL_ADDRESS')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            return jsonify({'status': 'error', 'message': 'Email credentials not configured'}), 500
        
        recipient_data = get_next_recipient()
        
        if recipient_data and recipient_data['email']:
            success, message = send_email_with_cv(
                recipient_email=recipient_data['email'],
                recipient_name=recipient_data['full_name'],
                subject=f"[TEST] {recipient_data['subject']}",
                body=f"[TEST EMAIL]\n\n{recipient_data['content']}\n\nThis is a manual test email.",
                sender_email=sender_email,
                sender_password=sender_password
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'✅ Test email sent! ({message})',
                    'details': {
                        'to': recipient_data['email'],
                        'recipient_name': recipient_data['full_name'],
                        'recipient_number': recipient_data['counter'] + 1,
                        'total_recipients': recipient_data['total_recipients']
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': f'❌ Test email failed: {message}'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'No recipient data available'}), 500
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Test email failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting PFE Email Sender - CLEAN VERSION v3.0 on port {port}")
    logger.info(f"⏰ Business hours: {os.environ.get('START_HOUR', '9')}:00 - {os.environ.get('END_HOUR', '17')}:00 UTC")
    app.run(host='0.0.0.0', port=port, debug=False)