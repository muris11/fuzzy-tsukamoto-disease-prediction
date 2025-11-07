# ✅ CHECKLIST DEPLOY PYTHONANYWHERE

## 📋 PRE-DEPLOY CHECKLIST

### Local Testing (Wajib!)

- [ ] `python -c "from api_app import app; print('Import OK')"`
- [ ] `python -c "from fis_tsukamoto import Diagnoser; print('Diagnoser OK')"`
- [ ] Test API: `uvicorn api_app:app --host 127.0.0.1 --port 8000`
- [ ] Health check: `curl http://127.0.0.1:8000/health`
- [ ] Schema check: `curl http://127.0.0.1:8000/v1/schema`
- [ ] Prediction test dengan sample data

### Files Ready

- [ ] `api_app.py` - FastAPI app
- [ ] `fis_tsukamoto.py` - Fuzzy logic engine
- [ ] `rifqy11_pythonanywhere_com_wsgi.py` - WSGI configuration ✅ **READY**
- [ ] `requirements_pythonanywhere.txt` - Dependencies
- [ ] `.gitignore` - Updated (no venv/cache files)
- [ ] Repository pushed to GitHub

---

## 🚀 DEPLOYMENT STEPS

### 1. PythonAnywhere Account

- [ ] Sign up at pythonanywhere.com
- [ ] Choose Beginner plan (free)
- [ ] Username: `rifqy11`
- [ ] Email verified

### 2. Web App Setup

- [ ] Login to dashboard
- [ ] Go to **Web** tab
- [ ] Click **Add a new web app**
- [ ] Choose **Manual configuration**
- [ ] Select **Python 3.10**
- [ ] Domain: `rifqy11.pythonanywhere.com`

### 3. Code Upload

- [ ] Go to **Consoles** tab
- [ ] Open **Bash** console
- [ ] `cd /home/rifqy11/`
- [ ] `git clone https://github.com/muris11/fuzzy-tsukamoto-disease-prediction.git`
- [ ] `cd fuzzy-tsukamoto-disease-prediction`
- [ ] `ls -la` (verify files)

### 4. Environment Setup

- [ ] `python3.10 -m venv venv`
- [ ] `source venv/bin/activate`
- [ ] `pip install --upgrade pip`
- [ ] `pip install -r requirements_pythonanywhere.txt`
- [ ] `pip list | grep -E "(fastapi|pydantic|uvicorn)"`

### 5. WSGI Configuration

- [ ] Create WSGI file: `/home/rifqy11/rifqy11_pythonanywhere_com_wsgi.py` ✅ **FILE READY**
- [ ] Copy WSGI code from `PYTHONANYWHERE_DEPLOY.md` (atau gunakan file yang sudah ada)
- [ ] Go to **Web** tab
- [ ] Set **Source code** path: `/home/rifqy11/fuzzy-tsukamoto-disease-prediction`
- [ ] Set **WSGI file** path: `/home/rifqy11/rifqy11_pythonanywhere_com_wsgi.py`
- [ ] Set **Working directory**: `/home/rifqy11/fuzzy-tsukamoto-disease-prediction`

### 6. Reload & Test

- [ ] Click **Reload** button
- [ ] Wait for status: **Live**
- [ ] Test health: `curl https://rifqy11.pythonanywhere.com/health`
- [ ] Test schema: `curl https://rifqy11.pythonanywhere.com/v1/schema`
- [ ] Test predict: `curl -X POST https://rifqy11.pythonanywhere.com/v1/predict -H "Content-Type: application/json" -d '{"nama":"Test","fever":"berat","cough":"sering"}'`

---

## 🔍 TROUBLESHOOTING CHECKLIST

### If Import Error:

- [ ] Check virtual environment: `source venv/bin/activate`
- [ ] Verify packages: `pip list`
- [ ] Test import: `python -c "from api_app import app"`

### If WSGI Error:

- [ ] Check **Server error log** in Web tab
- [ ] Verify WSGI file path
- [ ] Verify project directory path
- [ ] Check file permissions

### If CORS Error:

- [ ] Check API middleware in `api_app.py`
- [ ] Test with simple curl request
- [ ] Check **Server access log**

### If Slow Response:

- [ ] Free tier limitation
- [ ] Check CPU usage in Account tab
- [ ] Consider paid upgrade

---

## 📊 POST-DEPLOY VERIFICATION

### API Endpoints Working:

- [ ] `GET /health` → Status 200, JSON response
- [ ] `GET /v1/schema` → Status 200, 10 questions
- [ ] `POST /v1/predict` → Status 200, diagnosis with 98.5% confidence
- [ ] `POST /v1/report` → Status 200, HTML report

### Integration Ready:

- [ ] Flutter app base URL updated
- [ ] Web app API_BASE updated
- [ ] Mobile app tested with live API

---

## 🎯 FINAL STATUS

- [ ] **Local Testing**: ✅ All passed
- [ ] **PythonAnywhere Account**: ✅ Created
- [ ] **Web App**: ✅ Configured
- [ ] **Code**: ✅ Uploaded
- [ ] **Environment**: ✅ Setup
- [ ] **WSGI**: ✅ Configured
- [ ] **API**: ✅ Live & Working
- [ ] **Integration**: ✅ Ready

**LIVE URL**: https://rifqy11.pythonanywhere.com

---

## 📞 SUPPORT

Jika ada masalah:

1. Cek **Server error log** di Web tab
2. Cek **Server access log** di Web tab
3. Test dengan curl commands di atas
4. Pastikan virtual environment aktif
5. Reload web app setelah perubahan

**Happy Deploying! 🚀**
