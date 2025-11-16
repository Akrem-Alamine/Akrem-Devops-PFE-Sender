#!/usr/bin/env python3
"""
PFE Automated Email Sender - Production Version
Sends personalized emails during business hours using CSV data
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

def get_next_recipient():
    """Get next recipient from CSV using round-robin"""
    csv_path = os.environ.get('CSV_FILE_PATH', 'data/recipients.csv')
    
    if not os.path.exists(csv_path):
        logger.warning(f"CSV file not found at {csv_path}")
        return None
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            recipients = list(csv_reader)
            
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
        'message': 'PFE Automated Email Sender - Production',
        'version': '3.0-CLEAN',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'pfe-email-sender',
        'version': '3.0-CLEAN',
        'environment': 'production',
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
        'business_hours': f"{os.environ.get('START_HOUR', '9')}:00 - {os.environ.get('END_HOUR', '17')}:00 UTC",
        'csv_status': {
            'file_exists': csv_exists,
            'recipient_count': recipient_count,
            'current_counter': get_email_counter()
        },
        'email_configured': bool(os.environ.get('EMAIL_ADDRESS')),
        'timestamp': datetime.now().isoformat()
    })

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
        
        # Business hours check
        is_weekday = current_weekday < 5
        is_business_hours = start_hour <= current_hour < end_hour
        
        if is_weekday and is_business_hours:
            logger.info(f"✅ Cron executed during business hours: {now.isoformat()}")
            
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