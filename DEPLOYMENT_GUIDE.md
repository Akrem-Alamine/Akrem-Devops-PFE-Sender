# 🚀 PFE Email Sender - Complete Deployment Guide

## 📁 Project Analysis & Cleanup Complete

### ✅ Clean Project Created
Location: `c:\Users\akrem\OneDrive\Desktop\PFE-Email-Sender-Clean\`

### 🗂️ Essential Files Only:
- ✅ `main.py` - Production Flask application (470 lines, complete)
- ✅ `requirements.txt` - Minimal dependencies (Flask + gunicorn)
- ✅ `app.yaml` - GCP App Engine configuration
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

## 🎯 Step-by-Step Deployment Guide

### Step 1: Initialize Git Repository
```powershell
cd "c:\Users\akrem\OneDrive\Desktop\PFE-Email-Sender-Clean"
git init
git branch -M main
git add .
git commit -m "Clean production-ready email sender with 10 mock recipients"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `PFE-Email-Sender-Clean`
3. Description: `Automated email sender for recruitment - Clean production version`
4. Set to **Public**
5. Click **Create repository**

### Step 3: Upload to GitHub
```powershell
# Add remote repository
git remote add origin https://github.com/Akrem-Alamine/PFE-Email-Sender-Clean.git

# Push to GitHub
git push -u origin main
```

### Step 4: Deploy to GCP Cloud Shell
```bash
# In Google Cloud Shell, clone the repository
git clone https://github.com/Akrem-Alamine/PFE-Email-Sender-Clean.git
cd PFE-Email-Sender-Clean

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

# Deploy the application
gcloud app deploy app.yaml --quiet

# Deploy cron jobs
gcloud app deploy deployment/cron.yaml --quiet
```

### Step 5: Test the System
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