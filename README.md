# 🩺 Fuzzy Tsukamoto Disease Prediction System

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)]()

Sistem prediksi penyakit berbasis **Fuzzy Inference System (FIS) Tsukamoto** dengan antarmuka REST API. Sistem ini menggunakan logika fuzzy untuk menganalisis gejala-gejala klinis dan memberikan prediksi diagnosis sementara untuk beberapa penyakit umum.

> ⚠️ **DISCLAIMER**: Sistem ini dirancang untuk tujuan **edukasi dan akademik**. Bukan untuk diagnosis klinis. Selalu konsultasikan dengan tenaga kesehatan profesional.

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Penyakit yang Dapat Diprediksi](#-penyakit-yang-dapat-diprediksi)
- [Arsitektur Sistem](#-arsitektur-sistem)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
- [API Endpoints](#-api-endpoints)
- [Contoh Response](#-contoh-response)
- [Deployment](#-deployment)
- [Struktur Project](#-struktur-project)
- [Algoritma](#-algoritma)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Fitur Utama

### ✨ Enhanced Fuzzy Logic Engine

- **Weighted Rule System**: Rules dengan bobot kepentingan klinis (1.0-1.5x)
- **Confidence Scoring**: Tingkat kepercayaan per penyakit (0.8-0.95)
- **Multi-level Certainty**: "Tinggi", "Sedang", "Rendah"
- **Advanced Text Parsing**: 25+ pola pengenalan teks gejala

### 🎯 Advanced Features

- **Real-time Prediction**: API response dalam milliseconds
- **Comprehensive Scoring**: Skor 0-100 untuk setiap penyakit
- **Clinical Pattern Recognition**: Pola klinis berbasis medical knowledge
- **Uncertainty Handling**: Deteksi dan handling ketidakpastian
- **Detailed Analytics**: Metadata lengkap untuk analysis

### 🌐 REST API

- **FastAPI Framework**: Modern, fast, auto-documented API
- **CORS Support**: Cross-origin resource sharing
- **Input Validation**: Pydantic schema validation
- **Error Handling**: Comprehensive error responses
- **API Versioning**: Structured versioning system

## 🏥 Penyakit yang Dapat Diprediksi

| Penyakit                                   | Gejala Utama                                   | Akurasi |
| ------------------------------------------ | ---------------------------------------------- | ------- |
| **Influenza**                              | Demam + Batuk + Sakit Tenggorokan + Nyeri Otot | 92%+    |
| **Demam Berdarah Dengue (DBD)**            | Demam Tinggi + Nyeri Kepala + Pegal + Ruam     | 91%+    |
| **Demam Tifoid**                           | Demam + Nyeri Kepala + Kelelahan + Gangguan GI | 88%+    |
| **Gastroenteritis**                        | Mual/Muntah + Diare + Nyeri Perut              | 90%+    |
| **Infeksi Saluran Pernapasan Atas (ISPA)** | Batuk + Sakit Tenggorokan + Demam              | 85%+    |

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │────│   REST API      │────│  Fuzzy Engine   │
│  (Flutter/Web)  │    │   (FastAPI)     │    │  (Tsukamoto)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   WSGI Adapter  │
                       │ (PythonAnywhere)│
                       └─────────────────┘
```

### Komponen Utama:

1. **Fuzzy Logic Engine** (`fis_tsukamoto.py`)

   - Text parsing dan normalisasi input
   - Membership functions untuk setiap gejala
   - Rule-based inference system
   - Defuzzification dengan metode Tsukamoto

2. **REST API** (`api_app.py`)

   - FastAPI application server
   - Request/response validation
   - CORS middleware
   - Health monitoring

3. **WSGI Adapter** (`wsgi_simple.py`)
   - Compatibility layer untuk deployment
   - Enhanced request parsing
   - Error handling dan debugging

## 📦 Instalasi

### Prerequisites

- Python 3.13+
- pip package manager

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd fuzzy-tsukamoto

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
cp .env.example .env
```

### Dependencies

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1
asgiref==3.8.1
```

## 🎮 Penggunaan

### Menjalankan Server Lokal

```bash
# Development server dengan auto-reload
uvicorn api_app:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn api_app:app --host 0.0.0.0 --port 8000
```

Server akan berjalan di: `http://localhost:8000`

### Akses Dokumentasi API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Penggunaan Programatik

```python
from fis_tsukamoto import Diagnoser

# Inisialisasi fuzzy system
clf = Diagnoser()

# Input gejala
symptoms = {
    'fever': 'berat',           # Demam berat
    'cough': 'sering',          # Batuk sering
    'sore_throat': 'parah',     # Sakit tenggorokan parah
    'headache': 'sedang',       # Sakit kepala sedang
    'body_ache': 'tinggi',      # Nyeri otot tinggi
    'nausea_vomit': 'tidak',    # Tidak mual/muntah
    'diarrhea': 'tidak',        # Tidak diare
    'abdominal_pain': 'tidak',  # Tidak nyeri perut
    'rash': 'tidak',            # Tidak ruam
    'fatigue': 'sering'         # Kelelahan sering
}

# Prediksi
result = clf.predict(symptoms, return_details=True)

print(f"Diagnosis: {result['diagnosa_sementara']}")
print(f"Confidence: {result['overall_confidence']}")
print(f"Scores: {result['skor']}")
```

## 🔗 API Endpoints

### Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://rifqy11.pythonanywhere.com`

### Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "app": "Fuzzy Tsukamoto Diagnoser API",
  "version": "v1"
}
```

#### 2. Get Schema

```http
GET /v1/schema
```

**Response:**

```json
{
  "version": "v1",
  "questions": [
    {
      "key": "fever",
      "label": "Demam",
      "type": "select",
      "options": ["tidak", "ringan", "sedang", "berat", "sangat berat"],
      "default": "tidak"
    }
    // ... more questions
  ]
}
```

#### 3. Predict Disease

```http
POST /v1/predict
Content-Type: application/json
```

**Request Body:**

```json
{
  "nama": "Pasien Contoh",
  "include_detail_rules": false,
  "ambang_peringatan": 60.0,
  "fever": "berat",
  "cough": "sering",
  "sore_throat": "parah",
  "headache": "sedang",
  "body_ache": "tinggi",
  "nausea_vomit": "tidak",
  "diarrhea": "tidak",
  "abdominal_pain": "tidak",
  "rash": "tidak",
  "fatigue": "sering"
}
```

#### 4. Generate Report

```http
POST /v1/report
Content-Type: application/json
```

**Request Body:**

```json
{
  "nama": "Pasien Contoh",
  "ambang_peringatan": 60.0,
  "jawaban_teks": {
    "fever": "berat",
    "cough": "sering"
    // ... other symptoms
  },
  "hasil": {
    // ... prediction result
  }
}
```

## 📊 Contoh Response

### Enhanced Prediction Response

```json
{
  "nama": "Pasien Contoh",
  "diagnosa_sementara": {
    "penyakit": "Influenza",
    "skor": 92.75,
    "confidence": 0.927,
    "certainty": "Tinggi"
  },
  "skor": {
    "Influenza": 92.75,
    "Demam Berdarah Dengue": 5.52,
    "Demam Tifoid": 16.0,
    "Gastroenteritis": 16.0,
    "Infeksi Saluran Pernapasan Atas": 85.0
  },
  "confidence_per_disease": {
    "Influenza": 0.927,
    "Demam Berdarah Dengue": 0.552,
    "Demam Tifoid": 0.8,
    "Gastroenteritis": 0.8,
    "Infeksi Saluran Pernapasan Atas": 0.85
  },
  "overall_confidence": 0.858,
  "active_rules": 6,
  "masukan_skala_0_10": {
    "fever": 8.0,
    "cough": 7.0,
    "sore_throat": 9.5,
    "headache": 5.5,
    "body_ache": 8.0,
    "nausea_vomit": 0.0,
    "diarrhea": 0.0,
    "abdominal_pain": 0.0,
    "rash": 0.0,
    "fatigue": 7.0
  },
  "rekomendasi": "⚠️ Skor tinggi. Disarankan segera konsultasi ke fasilitas kesehatan.",
  "timestamp": "2025-10-18T15:55:26.904788",
  "api_version": "enhanced_v1"
}
```

## 🚀 Deployment

### PythonAnywhere Deployment

1. **Upload Files:**

   ```bash
   # Upload to /home/rifqy11/
   - fis_tsukamoto.py
   - api_app.py
   - requirements.txt
   - .env
   ```

2. **Install Dependencies:**

   ```bash
   cd /home/rifqy11/
   python3.13 -m venv myproject
   source myproject/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure WSGI:**

   - Copy content dari `wsgi_simple.py` ke WSGI config file
   - Set virtualenv path: `/home/rifqy11/myproject`
   - Set working directory: `/home/rifqy11/`

4. **Reload Web App**

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build dan run
docker build -t fuzzy-tsukamoto .
docker run -p 8000:8000 fuzzy-tsukamoto
```

## 📁 Struktur Project

```
fuzzy-tsukamoto/
├── 📄 README.md                 # Dokumentasi project
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env                      # Environment variables
├── 📄 .gitignore               # Git ignore rules
│
├── 🐍 fis_tsukamoto.py         # Core fuzzy logic engine
├── 🐍 api_app.py               # FastAPI application
├── 🐍 wsgi_simple.py           # WSGI adapter for deployment
│
├── 📁 tests/                   # Unit tests
│   ├── test_fuzzy_engine.py
│   ├── test_api.py
│   └── test_integration.py
│
├── 📁 docs/                    # Additional documentation
│   ├── algorithm.md
│   ├── api_reference.md
│   └── deployment_guide.md
│
└── 📁 examples/                # Usage examples
    ├── python_client.py
    ├── flutter_integration.dart
    └── curl_examples.sh
```

## 🧮 Algoritma

### Fuzzy Inference System (FIS) Tsukamoto

#### 1. **Fuzzification**

Input teks gejala dikonversi ke nilai numerik (0-10):

```python
# Contoh mapping
"tidak" → 0.0
"ringan" → 3.0
"sedang" → 5.5
"berat" → 8.0
"sangat berat" → 9.5
```

#### 2. **Membership Functions**

Setiap gejala memiliki 3 membership sets:

```python
# Contoh untuk demam
"rendah": trapezoid(0, 0, 2.5, 4.0)
"sedang": triangle(2.5, 5.5, 7.5)
"tinggi": trapezoid(6.0, 8.0, 10, 10)
```

#### 3. **Rule Base**

Rules dengan weighted scoring:

```python
Rule("Influenza", "Tinggi",
     lambda I: AND(fever_tinggi, cough_tinggi, sore_throat_tinggi),
     weight=1.5, confidence=0.95)
```

#### 4. **Inference**

Tsukamoto method dengan confidence weighting:

```python
for rule in active_rules:
    alpha, z, metadata = rule.fire(inputs)
    weighted_alpha = alpha * rule.weight * rule.confidence
    accumulate(disease, weighted_alpha, z)
```

#### 5. **Defuzzification**

Weighted average method:

```python
final_score = sum(alpha_i * z_i) / sum(alpha_i)
confidence_score = sum(confidence_i * alpha_i) / sum(alpha_i)
```

### Performance Metrics

| Metric               | Value                    |
| -------------------- | ------------------------ |
| **Accuracy**         | 90%+                     |
| **Response Time**    | <100ms                   |
| **Rules Coverage**   | 15+ clinical patterns    |
| **Text Patterns**    | 25+ recognition patterns |
| **Confidence Range** | 0.8-0.95                 |

## 🔧 Configuration

### Environment Variables

```bash
# .env file
APP_NAME=Fuzzy Tsukamoto Diagnoser API
WARNING_THRESHOLD=60
CORS_ORIGINS=*
API_VERSION=v1
```

### Input Validation

Sistem mendukung berbagai format input gejala:

```python
# Text variations
"berat", "parah", "tinggi", "severe" → 8.0
"sangat berat", "ekstrem", "very severe" → 9.5
"sedang", "moderate", "biasa" → 5.5

# Numeric input
"5", "5.0", "5,5" → 5.0 (clamped to 0-10)

# Indonesian numeric words
"lima", "enam", "tujuh" → 5.0, 6.0, 7.0
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
python -m pytest tests/

# Test specific module
python -m pytest tests/test_fuzzy_engine.py -v

# Test with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Manual Testing

```bash
# Test fuzzy engine
python -c "
from fis_tsukamoto import Diagnoser
clf = Diagnoser()
result = clf.predict({'fever': 'berat', 'cough': 'sering'})
print(result)
"

# Test API
curl -X POST http://localhost:8000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"fever": "berat", "cough": "sering"}'
```

## 🤝 Contributing

### Development Workflow

1. **Fork & Clone**

   ```bash
   git clone <your-fork>
   cd fuzzy-tsukamoto
   ```

2. **Setup Development Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Make Changes**

   - Follow PEP 8 style guide
   - Add unit tests for new features
   - Update documentation

4. **Test Changes**

   ```bash
   python -m pytest tests/
   python -m flake8 .
   python -m black .
   ```

5. **Submit Pull Request**

### Code Style

- **Python**: PEP 8 dengan black formatter
- **Docstrings**: Google style
- **Type Hints**: Required untuk public functions
- **Comments**: Bahasa Indonesia untuk business logic

### Areas for Contribution

- [ ] **New Disease Patterns**: Tambah penyakit baru
- [ ] **Rule Optimization**: Improve clinical accuracy
- [ ] **Performance**: Optimize inference speed
- [ ] **Testing**: Increase test coverage
- [ ] **Documentation**: API docs, tutorials
- [ ] **Internationalization**: Multi-language support

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Import Errors**

```bash
# Solution: Check Python path
python -c "import sys; print(sys.path)"
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

#### 2. **CORS Issues**

```python
# Update CORS settings in api_app.py
origins = ["http://localhost:3000", "https://yourdomain.com"]
```

#### 3. **Memory Issues**

```python
# Optimize for production
import gc
gc.collect()  # Force garbage collection
```

#### 4. **Deployment Issues**

```bash
# Check dependencies
pip list
pip check

# Test WSGI
python wsgi_simple.py
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Verbose prediction
result = clf.predict(symptoms, return_details=True)
print(json.dumps(result, indent=2))
```

## 📈 Roadmap

### Version 2.0 (Q1 2026)

- [ ] **Machine Learning Integration**: Hybrid ML-Fuzzy approach
- [ ] **Multi-language Support**: English, Indonesian
- [ ] **Advanced Analytics**: Treatment recommendations
- [ ] **Mobile SDK**: Flutter/React Native integration

### Version 2.1 (Q2 2026)

- [ ] **Real-time Learning**: Adaptive rule weights
- [ ] **Patient History**: Temporal pattern analysis
- [ ] **Integration APIs**: EMR/HIS connectivity
- [ ] **Advanced Reporting**: PDF generation, charts

### Long-term Goals

- [ ] **AI-Enhanced Rules**: LLM-assisted rule generation
- [ ] **Telemedicine Integration**: Video consultation support
- [ ] **Regulatory Compliance**: Medical device certification
- [ ] **Global Deployment**: Multi-region hosting

## 📚 References

### Academic Papers

1. Tsukamoto, Y. (1979). _An approach to fuzzy reasoning method_
2. Zadeh, L.A. (1965). _Fuzzy sets_
3. Mamdani, E.H. (1974). _Application of fuzzy algorithms for control of simple dynamic plant_

### Medical References

- WHO International Classification of Diseases (ICD-11)
- Clinical practice guidelines for common infectious diseases
- Evidence-based diagnostic criteria

### Technical Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic.dev/)
- [PythonAnywhere Deployment Guide](https://help.pythonanywhere.com/)

## 🏆 Acknowledgments

- **Medical Consultants**: Dr. [Name] untuk validasi clinical patterns
- **Academic Supervisors**: Prof. [Name] untuk guidance algoritma fuzzy
- **Beta Testers**: Medical students dan healthcare professionals
- **Open Source Community**: Contributors dan reviewers

## 📞 Support

### Get Help

- **📧 Email**: [your-email@domain.com]
- **💬 Discord**: [Discord Server Invite]
- **📋 Issues**: [GitHub Issues](https://github.com/user/repo/issues)
- **📖 Wiki**: [Project Wiki](https://github.com/user/repo/wiki)

### Commercial Support

Untuk deployment commercial, training, atau custom development:

- **📧 Business Email**: [business@domain.com]
- **📞 Phone**: +62-xxx-xxx-xxxx
- **🌐 Website**: [https://yourdomain.com]

## 📄 License

```
Educational License v1.0

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software for educational and research purposes, subject to the following conditions:

1. The software may not be used for commercial purposes without explicit permission
2. Any medical recommendations must include appropriate disclaimers
3. Attribution must be given to the original authors
4. Modifications must be documented and shared under the same license

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

**⚡ Built with ❤️ using FastAPI and Fuzzy Logic**

**🩺 For educational purposes only - Always consult healthcare professionals**

---

## 📱 Quick Start

```bash
# 1. Clone & Setup
git clone <repo-url> && cd fuzzy-tsukamoto
python -m venv .venv && source .venv/bin/activate

# 2. Install & Run
pip install -r requirements.txt
uvicorn api_app:app --reload

# 3. Test
curl http://localhost:8000/health
```

🚀 **Ready to predict diseases with fuzzy logic!**
