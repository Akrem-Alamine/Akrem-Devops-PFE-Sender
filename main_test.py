#!/usr/bin/env python3
"""
PFE Automated Email Sender - TEST VERSION (Ignores Business Hours)
Sends personalized emails IMMEDIATELY for testing purposes
"""

import os
import logging
import smtplib
import csv
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
        server.starttls()  # Enable TLS
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        logger.info(f"✅ Email sent successfully to {recipient_name} ({recipient_email})")
        return True, f"Email sent to {recipient_name}"
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg

def get_next_recipient():
    """Get next recipient using round-robin"""
    try:
        csv_path = os.environ.get('CSV_FILE_PATH', 'data/recipients.csv')
        
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
        
        return {
            'email': recipient.get('email', '').strip(),
            'first_name': recipient.get('first_name', '').strip(),
            'last_name': recipient.get('last_name', '').strip(),
            'full_name': f"{recipient.get('first_name', '').strip()} {recipient.get('last_name', '').strip()}".strip(),
            'subject': recipient.get('subject', 'Job Application - Software Developer Position').strip(),
            'content': recipient.get('content', '').strip(),
            'counter': counter,
            'total_recipients': len(recipients)
        }
        
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return None

@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'message': 'PFE Automated Email Sender - TEST MODE (No Business Hours)',
        'version': '3.0-TEST',
        'mode': 'TESTING - SENDS EMAILS ANYTIME',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'pfe-email-sender-test',
        'version': '3.0-TEST',
        'environment': 'testing',
        'mode': 'No business hours restriction',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    csv_path = os.environ.get('CSV_FILE_PATH', 'data/recipients.csv')
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
        'mode': 'TEST MODE - NO BUSINESS HOURS RESTRICTION',
        'business_hours': 'DISABLED (24/7 operation for testing)',
        'csv_status': {
            'file_exists': csv_exists,
            'recipient_count': recipient_count,
            'current_counter': get_email_counter()
        },
        'email_configured': bool(os.environ.get('EMAIL_ADDRESS')),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/debug')
def debug():
    """Debug endpoint to check configuration"""
    import os
    return jsonify({
        'environment_variables': {
            'EMAIL_ADDRESS': bool(os.environ.get('EMAIL_ADDRESS')),
            'EMAIL_PASSWORD': bool(os.environ.get('EMAIL_PASSWORD')),
            'CSV_FILE_PATH': os.environ.get('CSV_FILE_PATH', 'NOT_SET'),
            'CV_FILE_PATH': os.environ.get('CV_FILE_PATH', 'NOT_SET'),
            'SMTP_SERVER': os.environ.get('SMTP_SERVER', 'NOT_SET'),
            'SMTP_PORT': os.environ.get('SMTP_PORT', 'NOT_SET')
        },
        'file_existence': {
            'csv_exists': os.path.exists(os.environ.get('CSV_FILE_PATH', 'data/recipients.csv')),
            'cv_exists': os.path.exists(os.environ.get('CV_FILE_PATH', 'assets/Akrem_Alamine_ENOP.pdf'))
        },
        'email_counter': get_email_counter(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/cron/send-emails', methods=['GET', 'POST'])
def cron_send_emails():
    """TEST Cron endpoint - sends emails ANYTIME (ignores business hours)"""
    try:
        now = datetime.now()
        sender_email = os.environ.get('EMAIL_ADDRESS')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        logger.info(f"🚀 TEST MODE: Cron executed at {now.isoformat()} - Business hours IGNORED")
        
        if not sender_email or not sender_password:
            return jsonify({'status': 'error', 'message': 'Email credentials not configured'}), 500
        
        recipient_data = get_next_recipient()
        
        if recipient_data and recipient_data['email']:
            success, message = send_email_with_cv(
                recipient_email=recipient_data['email'],
                recipient_name=recipient_data['full_name'],
                subject=f"[TEST] {recipient_data['subject']}",
                body=f"[TEST MODE - NO BUSINESS HOURS]\n\n{recipient_data['content']}\n\n--- TEST EMAIL SENT AT {now.isoformat()} ---",
                sender_email=sender_email,
                sender_password=sender_password
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'✅ TEST EMAIL sent successfully! ({message})',
                    'mode': 'TEST MODE - Business hours ignored',
                    'timestamp': now.isoformat(),
                    'email_details': {
                        'to': recipient_data['email'],
                        'recipient_name': recipient_data['full_name'],
                        'subject': f"[TEST] {recipient_data['subject']}",
                        'recipient_number': recipient_data['counter'] + 1,
                        'total_recipients': recipient_data['total_recipients']
                    }
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'❌ Failed to send TEST email: {message}'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'No recipient data available'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ TEST Cron job error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'TEST Cron job failed: {str(e)}'
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
                subject=f"[MANUAL TEST] {recipient_data['subject']}",
                body=f"[MANUAL TEST EMAIL]\n\n{recipient_data['content']}\n\nThis is a manual test email sent at {datetime.now().isoformat()}",
                sender_email=sender_email,
                sender_password=sender_password
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f'✅ Manual test email sent! ({message})',
                    'details': {
                        'to': recipient_data['email'],
                        'recipient_name': recipient_data['full_name'],
                        'recipient_number': recipient_data['counter'] + 1,
                        'total_recipients': recipient_data['total_recipients']
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': f'❌ Manual test email failed: {message}'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'No recipient data available'}), 500
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Manual test email failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting PFE Email Sender - TEST VERSION v3.0 on port {port}")
    logger.info(f"⚠️  TEST MODE: Business hours DISABLED - Sends emails 24/7!")
    app.run(host='0.0.0.0', port=port, debug=False)