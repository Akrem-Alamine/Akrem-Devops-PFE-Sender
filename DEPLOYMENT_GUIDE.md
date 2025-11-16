# 🚀 PFE Email Sender - Complete Deployment Guide

## 📁 Repository Successfully Updated

### ✅ GitHub Repository Updated
Repository: `https://github.com/Akrem-Alamine/PFE-Sender`
Status: **Successfully updated with clean production code**

### 🗂️ Essential Files Only:
- ✅ `main.py` - Production Flask application (470 lines, complete)
- ✅ `main_test.py` - TEST version (ignores business hours for testing)
- ✅ `app.yaml` - GCP App Engine configuration (production)
- ✅ `app_test.yaml` - GCP App Engine configuration (testing)
- ✅ `requirements.txt` - Minimal dependencies (Flask + gunicorn)
- ✅ `data/recipients.csv` - 10 mock recipients (all emails → akrem.alamine@etudiant-fst.utm.tn)
- ✅ `assets/Akrem_Alamine_ENOP.pdf` - CV attachment
- ✅ `deployment/cron.yaml` - Cron job configuration
- ✅ `README.md` - Documentation
- ✅ `.gitignore` - Git ignore file

### ❌ Removed Unnecessary Files:
- 🗑️ Complex `src/` directory with modules
- 🗑️ Multiple duplicate app files
- 🗑️ Test files and local configurations
- 🗑️ Old deployment guides
- 🗑️ Environment files (.env)
- 🗑️ Editor settings (.vscode)

---

## 🎯 Next Steps - Deploy to Production

### ⚠️ TESTING MODE AVAILABLE

**For immediate testing (ignores business hours):**
```bash
# Deploy TEST version (sends emails 24/7)
gcloud app deploy app_test.yaml --quiet

# Test immediately (no business hours restriction)
curl -X POST https://pfe-sender.uc.r.appspot.com/cron/send-emails
curl -X POST https://pfe-sender.uc.r.appspot.com/test-email
```

### Step 1: ✅ Repository Setup (COMPLETED)
The GitHub repository has been successfully updated with the clean production code.

### Step 2: Deploy to GCP Cloud Shell
```bash
# Remove old directory if it exists
rm -rf PFE-Sender

# Clone the updated repository
git clone https://github.com/Akrem-Alamine/PFE-Sender.git
cd PFE-Sender

# Verify the updated files are present
ls -la

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Deploy the application
gcloud app deploy app.yaml --quiet

# Deploy cron jobs
gcloud app deploy deployment/cron.yaml --quiet
```

### Step 3: Test the System
```bash
# Test health endpoint
curl https://pfe-sender.uc.r.appspot.com/health

# Check system status (should show 10 recipients)
curl https://pfe-sender.uc.r.appspot.com/status

# Send manual test email
curl -X POST https://pfe-sender.uc.r.appspot.com/test-email

# Test cron endpoint
curl -X POST https://pfe-sender.uc.r.appspot.com/cron/send-emails

# Monitor logs
gcloud app logs tail -s default
```

### 🚨 Troubleshooting 502 Errors
If you get 502 Bad Gateway errors:

```bash
# 1. Pull latest fixes and redeploy
git pull
gcloud app deploy app_test.yaml --quiet

# 2. Check application logs for errors
gcloud app logs read --limit 50

# 3. Test the debug endpoint (if available)
curl https://pfe-sender.uc.r.appspot.com/debug

# 4. Try deploying production version instead
gcloud app deploy app.yaml --quiet
```

---

## 📊 Mock CSV Data Details

### 10 Test Recipients:
1. **Michiel Backker** (CTO, Twintag)
2. **Charly Hamy** (CTO, Rtone)  
3. **Mehdy Salimi** (CTO, Log'in Line)
4. **Francois Beuvens** (CTO, Sagacify)
5. **Yunus Ozturk** (CTO, Eachstapp)
6. **Clement Pellegrini** (CTO, Qarnot)
7. **Mehdi Abaakouk** (Co-founder, Mergify)
8. **Nicola Moresi** (CEO, Moresi.Com SA)
9. **Chris Zurbruegg** (Co-Founder, aumico)
10. **Damien Hontang** (Co-Founder, thinkeo)

### ✅ All emails redirect to: `akrem.alamine@etudiant-fst.utm.tn`

---

## 🎯 Expected Test Results

### ✅ During Business Hours (Mon-Fri, 9 AM - 5 PM UTC):
- **Every minute**: System sends 1 personalized email
- **Round-robin**: Cycles through all 10 recipients
- **CV attached**: Every email includes the PDF
- **Personalization**: Uses real names from CSV in email content

### ⏸️ Outside Business Hours:
- **Cron runs**: But skips email sending
- **Status**: Returns "skipped - weekend" or "skipped - outside business hours"

### 📧 Email Content:
- **Subject**: Personalized for each recipient's company
- **Body**: Professional job application with name placeholders filled
- **Attachment**: Akrem_Alamine_ENOP.pdf
- **From**: akrem.alamine@gmail.com
- **To**: akrem.alamine@etudiant-fst.utm.tn (for all 10 recipients)

---

## 🔍 Success Verification Checklist

### ✅ Deployment Success:
- [ ] Repository uploaded to GitHub successfully
- [ ] GCP deployment completes without errors
- [ ] Health endpoint returns status "healthy"
- [ ] Status endpoint shows 10 recipients in CSV

### ✅ Email Functionality:
- [ ] Manual test email sends successfully
- [ ] CV attachment is included in emails
- [ ] Email content is properly personalized
- [ ] Cron endpoint works during business hours
- [ ] System skips email sending during off-hours

### ✅ Business Logic:
- [ ] Round-robin cycling through recipients works
- [ ] Counter resets after reaching recipient #10
- [ ] Business hours constraint is enforced
- [ ] Weekend emails are properly skipped

---

## 🎉 Final Result

Once deployed, your system will:

1. **📧 Send emails every minute** during business hours
2. **🔄 Cycle through 10 recipients** using round-robin
3. **📎 Include CV attachment** in every email
4. **🎯 Deliver all emails** to akrem.alamine@etudiant-fst.utm.tn for testing
5. **⏰ Respect business hours** (Monday-Friday, 9 AM - 5 PM UTC)
6. **📊 Provide status tracking** via API endpoints

**Your automated recruitment email sender is now production-ready!** 🚀

---

## 🛠️ Next Steps (Optional)

To use with real recipients:
1. Replace mock data in `data/recipients.csv` with real recipient information
2. Update email addresses to real target addresses
3. Redeploy to GCP
4. Monitor via GCP logs and status endpoints

The system is designed to handle hundreds of recipients and will automatically cycle through them during business hours.