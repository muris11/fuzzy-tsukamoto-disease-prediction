# api_app.py
# -*- coding: utf-8 -*-
import os
from typing import Dict, Optional, List, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fis_tsukamoto import Diagnoser, LABEL_ID, render_report_html

load_dotenv()
APP_NAME = os.getenv("APP_NAME", "Fuzzy Tsukamoto Diagnoser API")
API_VERSION = "v1"
DEFAULT_WARNING_THRESHOLD = float(os.getenv("WARNING_THRESHOLD", "60"))

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="REST API Prediksi Penyakit berbasis Fuzzy Tsukamoto (Bahasa Indonesia). "
                "DISCLAIMER: Edukasi/akademik; bukan diagnosis klinis."
)

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionnaireItem(BaseModel):
    key: str
    label: str
    type: Literal["select", "text"] = "select"
    options: List[str] = []
    default: str = "tidak"

class SchemaResponse(BaseModel):
    version: str
    questions: List[QuestionnaireItem]

class PredictRequest(BaseModel):
    nama: Optional[str] = Field(default="Pengguna")
    include_detail_rules: bool = False
    ambang_peringatan: float = Field(default=DEFAULT_WARNING_THRESHOLD, ge=0, le=100)
    fever: str = "tidak"
    cough: str = "tidak"
    sore_throat: str = "tidak"
    headache: str = "tidak"
    body_ache: str = "tidak"
    nausea_vomit: str = "tidak"
    diarrhea: str = "tidak"
    abdominal_pain: str = "tidak"
    rash: str = "tidak"
    fatigue: str = "tidak"
    def to_internal_dict(self) -> Dict[str, str]:
        return {
            "fever": self.fever, "cough": self.cough, "sore_throat": self.sore_throat,
            "headache": self.headache, "body_ache": self.body_ache,
            "nausea_vomit": self.nausea_vomit, "diarrhea": self.diarrhea,
            "abdominal_pain": self.abdominal_pain, "rash": self.rash, "fatigue": self.fatigue
        }

class PredictResponse(BaseModel):
    nama: str
    diagnosa_sementara: Optional[Dict] = None
    skor: Dict[str, float]
    confidence_per_disease: Optional[Dict[str, float]] = None
    overall_confidence: Optional[float] = None
    active_rules: Optional[int] = None
    masukan_skala_0_10: Dict[str, float]
    detail_aturan: Optional[Dict[str, List[Dict]]] = None
    rekomendasi: str
    timestamp: Optional[str] = None
    api_version: str = "enhanced_v1"

class ReportRequest(BaseModel):
    nama: str = "Pengguna"
    ambang_peringatan: float = Field(default=DEFAULT_WARNING_THRESHOLD, ge=0, le=100)
    jawaban_teks: Dict[str, str]
    hasil: Dict

class ReportResponse(BaseModel):
    html: str

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "version": API_VERSION}

@app.get(f"/{API_VERSION}/schema", response_model=SchemaResponse)
def get_schema():
    options = ["tidak", "ringan", "sedang", "berat", "sangat berat", "kadang", "sering", "ya"]
    questions = [
        QuestionnaireItem(key=k, label=LABEL_ID[k], options=options, default="tidak")
        for k in LABEL_ID.keys()
    ]
    return {"version": API_VERSION, "questions": questions}

@app.post(f"/{API_VERSION}/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    clf = Diagnoser()
    result = clf.predict(payload.to_internal_dict(), return_details=payload.include_detail_rules)
    
    top = result.get("diagnosa_sementara")
    if not top:
        rekom = "Pantau gejala. Konsultasikan ke tenaga kesehatan bila perlu."
    else:
        skor = top.get("skor", 0)
        confidence = top.get("confidence", 0)
        
        if skor >= payload.ambang_peringatan:
            rekom = "⚠️ Skor tinggi. Disarankan segera konsultasi ke fasilitas kesehatan."
        elif skor >= 40:
            rekom = "Istirahat & hidrasi cukup. Konsultasi jika tidak membaik."
        else:
            rekom = "Pantau gejala. Jika memburuk, konsultasi ke tenaga kesehatan."
        
        # Add confidence-based recommendation
        if confidence < 0.6:
            rekom += f" (Confidence: {confidence:.1%} - Hasil kurang pasti)"
    
    from datetime import datetime
    
    return {
        "nama": payload.nama or "Pengguna",
        "diagnosa_sementara": result.get("diagnosa_sementara"),
        "skor": result.get("skor", {}),
        "confidence_per_disease": result.get("confidence_per_disease", {}),
        "overall_confidence": result.get("overall_confidence", 0.0),
        "active_rules": result.get("active_rules", 0),
        "masukan_skala_0_10": result.get("masukan_skala_0_10") or result.get("input_terbaca_skala_0_10", {}),
        "detail_aturan": result.get("detail_aturan") if payload.include_detail_rules else None,
        "rekomendasi": rekom,
        "timestamp": datetime.now().isoformat(),
        "api_version": "enhanced_v1"
    }

@app.post(f"/{API_VERSION}/report", response_model=ReportResponse)
def report(req: ReportRequest):
    try:
        html = render_report_html(req.nama, req.jawaban_teks, req.hasil, ambang_peringanan=req.ambang_peringatan)
        return {"html": html}
    except TypeError:
        # fallback untuk typo arg name
        html = render_report_html(req.nama, req.jawaban_teks, req.hasil, ambang_peringatan=req.ambang_peringatan)
        return {"html": html}
    except Exception as e:
        raise HTTPException(400, f"Gagal buat laporan: {e}")
# Example to run the app: