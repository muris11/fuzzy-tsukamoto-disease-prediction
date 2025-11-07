# 🚀 DEPLOY KE VERCEL

## 📋 Prasyarat

- Akun Vercel (github.com/vercel)
- GitHub repository
- Vercel CLI (opsional)

## ⚡ Langkah Deploy

### 1. Connect Repository

1. Buka [vercel.com](https://vercel.com)
2. Login dengan GitHub
3. Klik **New Project**
4. Import repository: `muris11/fuzzy-tsukamoto-disease-prediction`

### 2. Konfigurasi Project

Vercel akan otomatis mendeteksi file `vercel.json` dan `api/index.py`:

- **Framework Preset**: Python
- **Root Directory**: `./` (default)
- **Build Command**: (otomatis)
- **Output Directory**: (otomatis)

### 3. Environment Variables (Opsional)

Di **Project Settings** → **Environment Variables**:

```
APP_NAME=Fuzzy Tsukamoto Diagnoser API
WARNING_THRESHOLD=60
CORS_ORIGINS=*
```

### 4. Deploy

Klik **Deploy** - Vercel akan:

- Install dependencies dari `requirements_vercel.txt`
- Build serverless function
- Deploy ke production

## 🔍 Testing Deploy

### Health Check

```bash
curl https://your-project.vercel.app/health
```

### API Schema

```bash
curl https://your-project.vercel.app/v1/schema
```

### Prediction Test

```bash
curl -X POST https://your-project.vercel.app/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Test User",
    "fever": "berat",
    "cough": "sering"
  }'
```

## 📁 File Structure

```
project/
├── api/
│   └── index.py              # Vercel serverless function
├── vercel.json               # Vercel configuration
├── requirements_vercel.txt   # Dependencies for Vercel
├── api_app.py               # FastAPI app
├── fis_tsukamoto.py         # Fuzzy logic engine
└── ...
```

## ⚙️ Konfigurasi Files

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "runtime": "python3.9",
      "maxDuration": 15
    }
  }
}
```

### api/index.py

```python
from api_app import app
app = app  # Export for Vercel
```

## 💡 Keunggulan Vercel

- ✅ **Gratis**: Generous free tier
- ✅ **Cepat**: Global CDN
- ✅ **Auto-scaling**: Serverless
- ✅ **Git Integration**: Auto-deploy dari GitHub
- ✅ **Custom Domain**: Mudah setup

## 🔧 Troubleshooting

### Build Error

- Cek `requirements_vercel.txt`
- Pastikan semua dependencies compatible dengan Python 3.9

### Runtime Error

- Cek Vercel function logs
- Pastikan `api/index.py` exports `app`

### CORS Issues

- Cek CORS middleware di `api_app.py`
- Update `CORS_ORIGINS` environment variable

## 🌐 URL Structure

Setelah deploy:

- **Base URL**: `https://your-project.vercel.app`
- **Health**: `GET /health`
- **Schema**: `GET /v1/schema`
- **Predict**: `POST /v1/predict`
- **Report**: `POST /v1/report`

## 📱 Integration

### Flutter App

```dart
const String baseUrl = 'https://your-project.vercel.app';
```

### Web App

```javascript
const API_BASE = "https://your-project.vercel.app";
```

## 🎯 Status Deploy

- ✅ **Repository**: Ready
- ✅ **Vercel Config**: Ready (`vercel.json`)
- ✅ **API Handler**: Ready (`api/index.py`)
- ✅ **Dependencies**: Ready (`requirements_vercel.txt`)
- ✅ **FastAPI App**: Compatible
- ✅ **Fuzzy Logic**: Working

**Ready for Vercel deployment! 🚀**
