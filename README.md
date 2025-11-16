# PFE Automated Email Sender - Clean Production Version

## 📋 Overview
Automated email sender that sends personalized recruitment emails during business hours (Monday-Friday, 9 AM - 5 PM UTC) using CSV recipient data.

## ✅ Features
- **Business Hours Only**: Emails sent Monday-Friday, 9 AM - 5 PM UTC
- **Round-Robin Recipients**: Cycles through CSV recipients automatically  
- **CV Attachment**: Includes CV in every email
- **Personalization**: Uses first name, last name, and full name placeholders
- **GCP Deployment**: Ready for Google Cloud Platform
- **Cron Automation**: Sends 1 email per minute during business hours

## 🚀 Quick Deployment

### 1. Upload to GitHub
```bash
git clone https://github.com/Akrem-Alamine/PFE-Email-Sender-Clean.git
cd PFE-Email-Sender-Clean
```

### 2. Deploy to GCP
```bash
# Deploy application
gcloud app deploy app.yaml --quiet

# Deploy cron jobs  
gcloud app deploy deployment/cron.yaml --quiet
```

### 3. Test System
```bash
# Test health
curl https://your-project.uc.r.appspot.com/health

# Test manual email
curl -X POST https://your-project.uc.r.appspot.com/test-email

# Check status
curl https://your-project.uc.r.appspot.com/status
```

## 📁 File Structure
```
PFE-Email-Sender-Clean/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── app.yaml               # GCP configuration
├── data/
│   └── recipients.csv     # Email recipients (10 mock entries)
├── assets/
│   └── Akrem_Alamine_ENOP.pdf  # CV attachment
└── deployment/
    └── cron.yaml         # Cron job configuration
```

## 📧 CSV Format
The `data/recipients.csv` file should have these columns:
- `first_name`: Recipient's first name
- `last_name`: Recipient's last name
- `email`: Recipient's email address (all set to akrem.alamine@etudiant-fst.utm.tn for testing)
- `subject`: Email subject line
- `content`: Email body with placeholders ({first_name}, {last_name}, {full_name})

## 🎯 Expected Behavior
- **10 Mock Recipients**: System cycles through 10 test recipients
- **All Emails to Test Address**: Every email goes to akrem.alamine@etudiant-fst.utm.tn
- **Business Hours Only**: No emails sent on weekends or outside 9 AM - 5 PM UTC
- **1 Email/Minute**: During business hours, sends 1 personalized email per minute
- **CV Attached**: Every email includes the CV PDF attachment

## 🔧 Configuration
Environment variables are set in `app.yaml`:
- `EMAIL_ADDRESS`: akrem.alamine@gmail.com
- `EMAIL_PASSWORD`: apkrvuqqrhhwscas
- `START_HOUR`: 9 (9 AM UTC)
- `END_HOUR`: 17 (5 PM UTC)
- `CSV_FILE_PATH`: data/recipients.csv
- `CV_FILE_PATH`: assets/Akrem_Alamine_ENOP.pdf

## 🎉 Success Indicators
1. ✅ Health check returns status "healthy"
2. ✅ Status shows correct recipient count (10)
3. ✅ Test email sends successfully with CV attached
4. ✅ Cron jobs skip during off-hours and weekends
5. ✅ During business hours, emails are sent every minute