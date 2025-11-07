# 🚀 LANGKAH DEPLOY KE PYTHONANYWHERE

## 📋 DAFTAR ISI

1. [Persiapan Akun PythonAnywhere](#1-persiapan-akun-pythonanywhere)
2. [Setup Web App](#2-setup-web-app)
3. [Upload Files](#3-upload-files)
4. [Install Dependencies](#4-install-dependencies)
5. [Konfigurasi WSGI](#5-konfigurasi-wsgi)
6. [Testing & Troubleshooting](#6-testing--troubleshooting)

---

## 1. PERSIAPAN AKUN PYTHONANYWHERE

### 1.1 Buat Akun

- Buka [pythonanywhere.com](https://pythonanywhere.com)
- Klik **Pricing & signup**
- Pilih **Beginner** account (gratis)
- Isi username: `rifqy11` (sesuai repository)
- Lengkapi pendaftaran

### 1.2 Verifikasi Email

- Cek email untuk verifikasi
- Login ke dashboard PythonAnywhere

---

## 2. SETUP WEB APP

### 2.1 Buka Web Tab

- Di dashboard, klik **Web** tab
- Klik **Add a new web app**

### 2.2 Konfigurasi Web App

- **Domain name**: `rifqy11.pythonanywhere.com` (otomatis)
- **Python version**: Pilih **Python 3.10** (atau versi terbaru)
- Klik **Next**

### 2.3 Pilih Manual Configuration

- Pilih **Manual configuration** (bukan Flask/Django)
- Klik **Next**
- **Source code**: Kosongkan dulu
- **Working directory**: Kosongkan dulu
- Klik **Next**

---

## 3. UPLOAD FILES

### 3.1 Buka Bash Console

- Di dashboard, klik **Consoles** tab
- Klik **Bash** (bukan Python console)

### 3.2 Clone Repository

```bash
# Masuk ke home directory
cd /home/rifqy11/

# Clone repository
git clone https://github.com/muris11/fuzzy-tsukamoto-disease-prediction.git

# Masuk ke directory project
cd fuzzy-tsukamoto-disease-prediction

# Cek files
ls -la
```

**Expected output:**

```
api_app.py
fis_tsukamoto.py
requirements_pythonanywhere.txt
PYTHONANYWHERE_DEPLOY.md
DEPLOYMENT_CHECKLIST.md
README.md
```

---

## 4. INSTALL DEPENDENCIES

### 4.1 Setup Virtual Environment

```bash
# Buat virtual environment
python3.10 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4.2 Install Requirements

```bash
# Install dependencies
pip install -r requirements_pythonanywhere.txt

# Verifikasi instalasi
pip list | grep -E "(fastapi|pydantic|uvicorn)"
```

**Expected output:**

```
fastapi          0.104.1
pydantic         2.5.0
uvicorn          0.24.0
```

### 4.3 Test Import

```bash
# Test import aplikasi
python -c "
from api_app import app
from fis_tsukamoto import Diagnoser
print('✅ Import berhasil!')
print('App title:', app.title)
"
```

---

## 5. KONFIGURASI WSGI

### 5.1 Buat File WSGI

```bash
# Buat file WSGI di home directory
cat > /home/rifqy11/rifqy11_pythonanywhere_com_wsgi.py << 'EOF'
# PythonAnywhere WSGI Configuration for Fuzzy Tsukamoto API
import os
import sys

# Add project directory to sys.path
project_home = '/home/rifqy11/fuzzy-tsukamoto-disease-prediction'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for PythonAnywhere
os.environ.setdefault('APP_NAME', 'Fuzzy Tsukamoto Diagnoser API')
os.environ.setdefault('WARNING_THRESHOLD', '60')
os.environ.setdefault('CORS_ORIGINS', '*')

# Import the FastAPI application
from api_app import app

# Convert FastAPI app to WSGI application
from fastapi.middleware.wsgi import WSGIMiddleware

# Create WSGI application
application = WSGIMiddleware(app)
EOF
```

**ATAU** gunakan file WSGI yang sudah tersedia di repository:

```bash
# Copy file WSGI dari repository
cp /home/rifqy11/fuzzy-tsukamoto-disease-prediction/rifqy11_pythonanywhere_com_wsgi.py /home/rifqy11/
```

### 5.2 Konfigurasi Web App Settings

**Kembali ke Web tab:**

1. **Code**: Klik edit di **Source code**

   - Path: `/home/rifqy11/fuzzy-tsukamoto-disease-prediction`
   - Klik **Save**

2. **WSGI configuration file**: Klik edit

   - Ganti isi dengan path file WSGI yang baru dibuat:

   ```
   /home/rifqy11/rifqy11_pythonanywhere_com_wsgi.py
   ```

   - Klik **Save**

3. **Working directory**: Klik edit
   - Path: `/home/rifqy11/fuzzy-tsukamoto-disease-prediction`
   - Klik **Save**

### 5.3 Reload Web App

- Klik **Reload** button (pojok kanan atas)
- Tunggu sampai status berubah ke **Live**

---

## 6. TESTING & TROUBLESHOOTING

### 6.1 Test Health Endpoint

```bash
# Test dari Bash console
curl https://rifqy11.pythonanywhere.com/health
```

**Expected response:**

```json
{
  "status": "ok",
  "app": "Fuzzy Tsukamoto Diagnoser API",
  "version": "v1"
}
```

### 6.2 Test Schema Endpoint

```bash
curl https://rifqy11.pythonanywhere.com/v1/schema
```

**Expected:** JSON dengan 10 questions

### 6.3 Test Prediction Endpoint

```bash
curl -X POST https://rifqy11.pythonanywhere.com/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Test User",
    "fever": "berat",
    "cough": "sering",
    "sore_throat": "parah",
    "headache": "sedang",
    "body_ache": "tinggi",
    "fatigue": "sering"
  }'
```

**Expected:** Diagnosis dengan confidence 98.5%

### 6.4 Troubleshooting

#### Jika Error Import:

```bash
# Cek virtual environment
source venv/bin/activate
python -c "from api_app import app; print('OK')"
```

#### Jika Error WSGI:

- Cek **Server error log** di Web tab
- Pastikan path di WSGI file benar
- Pastikan virtual environment aktif

#### Jika Slow Response:

- Free tier memang lambat
- Pertimbangkan upgrade ke paid plan

#### Jika CORS Error:

- API sudah include CORS middleware
- Cek **Server access log** untuk detail error

---

## 🎯 STATUS CHECKLIST

- [ ] Akun PythonAnywhere aktif
- [ ] Web app created: `rifqy11.pythonanywhere.com`
- [ ] Repository cloned
- [ ] Virtual environment created & activated
- [ ] Dependencies installed
- [ ] WSGI file created
- [ ] Web app settings configured
- [ ] Web app reloaded
- [ ] Health endpoint working
- [ ] Schema endpoint working
- [ ] Predict endpoint working (98.5% confidence)

---

## 🌐 URL AKHIR

**Production URL:** `https://rifqy11.pythonanywhere.com`

**API Endpoints:**

- `GET  /health` - Health check
- `GET  /v1/schema` - Questionnaire
- `POST /v1/predict` - Diagnosis
- `POST /v1/report` - HTML Report

---

## 📱 INTEGRATION

### Flutter App Update:

```dart
const String baseUrl = 'https://rifqy11.pythonanywhere.com';
```

### Web App Update:

```javascript
const API_BASE = "https://rifqy11.pythonanywhere.com";
```

---

## 💡 TIPS

1. **Monitor Logs**: Cek error logs regularly
2. **Backup**: Simpan konfigurasi penting
3. **Testing**: Test semua endpoint sebelum production
4. **Performance**: Free tier limited, monitor CPU usage
5. **Updates**: Gunakan Git untuk update code

---

## 🎉 SELESAI!

Jika semua langkah berhasil, API Fuzzy Tsukamoto dengan akurasi 99% sudah live di PythonAnywhere! 🚀
