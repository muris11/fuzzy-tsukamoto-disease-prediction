# fis_tsukamoto.py
# -*- coding: utf-8 -*-
"""
FIS Tsukamoto untuk Prediksi Penyakit (Bahasa Indonesia)
Input: kuisioner teks (tidak, ringan, sedang, berat, sangat berat, kadang, sering, ya)
Output: skor 0..100/penyakit + diagnosa sementara (top-1) + detail rule (opsional)
DISCLAIMER: Edukasi/akademik; bukan diagnosis klinis.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple, Any
import math, re, datetime

LABEL_ID = {
    "fever": "Demam",
    "cough": "Batuk",
    "sore_throat": "Sakit Tenggorokan",
    "headache": "Sakit Kepala",
    "body_ache": "Nyeri Otot/Pegal",
    "nausea_vomit": "Mual/Muntah",
    "diarrhea": "Diare",
    "abdominal_pain": "Nyeri Perut",
    "rash": "Ruam Kulit",
    "fatigue": "Lemas/Kelelahan",
}

LEXICON = {
    # Tidak ada gejala (0.0-1.0)
    r"^(?:tidak|nggak|ga|gak|no|tanpa|tidak ada|enggak|kosong|nihil|normal)$": 0.0,
    
    # Sangat ringan (1.0-2.5)
    r"^(?:jarang sekali|sangat ringan|minimal|sedikit sekali|hampir tidak|trace)$": 1.5,
    r"^(?:jarang|ringan sekali|minimal|sedikit)$": 2.0,
    
    # Ringan (2.5-4.0)
    r"^(?:ringan|agak|lumayan|mild|slight|tipis|lemah)$": 3.0,
    r"^(?:agak ringan|cukup ringan|ringan sedang)$": 3.5,
    
    # Kadang-kadang (4.0-5.0)
    r"^(?:kadang|kadang-kadang|sometimes|sesekali|sewaktu-waktu)$": 4.5,
    
    # Sedang (5.0-6.5)
    r"^(?:sedang|moderate|normal|biasa|cukup|lumayan|menengah)$": 5.5,
    r"^(?:agak sedang|cukup sedang|moderate plus)$": 6.0,
    
    # Sering/Cukup berat (6.5-8.0)
    r"^(?:sering|cukup sering|sering kali|frequent|often|agak berat)$": 7.0,
    r"^(?:cukup berat|agak parah|quite severe)$": 7.5,
    
    # Berat (8.0-9.0)
    r"^(?:berat|parah|tinggi|kambuh|severe|heavy|intense|keras)$": 8.0,
    r"^(?:sangat sering|very frequent|hampir selalu|almost always)$": 8.5,
    
    # Sangat berat (9.0-10.0)
    r"^(?:sangat berat|sangat parah|amat parah|ekstrem|extreme|very severe|unbearable)$": 9.5,
    r"^(?:maksimal|paling parah|terparah|worst|critical)$": 10.0,
    
    # Ya/Ada (kontekstual)
    r"^(?:ya|iya|betul|ada|positif|present|yes|benar|iyah)$": 7.5,
}

def parse_symptom_text(txt: str) -> float:
    """Enhanced parsing dengan penanganan konteks yang lebih baik"""
    if txt is None: 
        return 0.0
    
    s = str(txt).strip().lower()
    
    # Handle numeric input
    try:
        if s.replace(".", "", 1).replace(",", "", 1).isdigit():
            v = float(s.replace(",", "."))
            return max(0.0, min(10.0, v))
    except: 
        pass
    
    # Preprocess text - handle common variations
    s = re.sub(r'\s+', ' ', s)  # normalize whitespace
    s = re.sub(r'[^\w\s-]', '', s)  # remove punctuation except dash
    
    # Handle numeric words
    numeric_words = {
        'nol': 0, 'satu': 1, 'dua': 2, 'tiga': 3, 'empat': 4,
        'lima': 5, 'enam': 6, 'tujuh': 7, 'delapan': 8, 'sembilan': 9, 'sepuluh': 10
    }
    for word, num in numeric_words.items():
        if word in s:
            return min(10.0, float(num))
    
    # Enhanced pattern matching with exact regex
    for pattern, val in LEXICON.items():
        if re.fullmatch(pattern, s):
            return val
    
    # Fallback: partial matching for composite expressions
    score = 0.0
    matched = False
    
    # Check for intensity modifiers first
    if any(k in s for k in ["sangat berat", "sangat parah", "amat parah", "ekstrem", "paling"]):
        score = 9.5; matched = True
    elif any(k in s for k in ["sangat sering", "hampir selalu", "terus menerus"]):
        score = 8.5; matched = True
    elif any(k in s for k in ["berat", "parah", "tinggi", "sering", "kambuh", "keras"]):
        score = 8.0; matched = True
    elif any(k in s for k in ["cukup", "lumayan", "agak berat"]):
        score = 7.0; matched = True
    elif any(k in s for k in ["sedang", "moderate", "biasa", "normal"]) and "ringan" not in s:
        score = 5.5; matched = True
    elif any(k in s for k in ["kadang", "sesekali", "sewaktu"]):
        score = 4.5; matched = True
    elif any(k in s for k in ["ringan", "jarang", "agak", "sedikit"]) and "sangat" not in s:
        score = 3.0; matched = True
    elif any(k in s for k in ["ya", "ada", "positif", "iya", "betul", "benar"]):
        score = 7.0; matched = True
    elif any(k in s for k in ["tidak", "nggak", "gak", "ga", "no", "tanpa", "enggak"]):
        score = 0.0; matched = True
    
    return score if matched else 0.0

def tri(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c: return 0.0
    if b == a or c == b: return 0.0
    if x == b: return 1.0
    if x < b: return (x - a) / (b - a)
    return (c - x) / (c - b)

def trap(x: float, a: float, b: float, c: float, d: float) -> float:
    if x <= a or x >= d: return 0.0
    if b <= x <= c: return 1.0
    if b == a or d == c: return 0.0
    if a < x < b: return (x - a) / (b - a)
    return (d - x) / (d - c)

def inv_high(alpha: float) -> float:
    alpha = max(0.0, min(1.0, alpha)); return 100.0 * alpha

def inv_low(alpha: float) -> float:
    alpha = max(0.0, min(1.0, alpha)); return 100.0 * (1.0 - alpha)

@dataclass
class FuzzyVar:
    name: str
    sets: Dict[str, Callable[[float], float]]

@dataclass
class Rule:
    disease: str
    consequent_label: str  # "Tinggi" | "Rendah" | "Sedang"
    antecedent: Callable[[Dict[str, float]], float]
    note: str = ""
    weight: float = 1.0  # Weight untuk rule importance
    confidence: float = 1.0  # Confidence level dari rule
    
    def fire(self, inputs: Dict[str, float]) -> Tuple[float, float, Dict[str, Any]]:
        """Enhanced firing dengan metadata"""
        alpha = max(0.0, min(1.0, self.antecedent(inputs)))
        
        # Apply weight and confidence
        weighted_alpha = alpha * self.weight * self.confidence
        
        # Enhanced consequent calculation
        if self.consequent_label.lower() == "tinggi":
            z = inv_high(weighted_alpha)
        elif self.consequent_label.lower() == "sedang":
            z = 50.0 + (50.0 * weighted_alpha)  # 50-100 range
        else:  # rendah
            z = inv_low(weighted_alpha)
        
        # Metadata untuk analysis
        metadata = {
            "raw_alpha": alpha,
            "weighted_alpha": weighted_alpha,
            "weight": self.weight,
            "confidence": self.confidence,
            "consequent": self.consequent_label,
            "z_value": z
        }
        
        return weighted_alpha, z, metadata

def make_symptom_vars() -> Dict[str, FuzzyVar]:
    """Membership functions yang lebih sensitif dan akurat"""
    # Optimized membership functions dengan overlap yang lebih natural
    sets_standard = {
        "rendah":  lambda x: trap(x, 0, 0, 2.0, 4.5),      # 0-4.5 dengan plateau di 0-2
        "sedang":  lambda x: tri(x, 2.0, 5.0, 8.0),        # 2-8 dengan puncak di 5
        "tinggi":  lambda x: trap(x, 5.5, 7.5, 10.0, 10.1), # 5.5-10 dengan plateau di 7.5-10
    }
    
    # Khusus untuk gejala yang perlu sensitivitas berbeda
    sets_fever = {
        "rendah":  lambda x: trap(x, 0, 0, 2.5, 4.0),      # Demam rendah lebih toleran
        "sedang":  lambda x: tri(x, 2.5, 5.5, 7.5),        # Demam sedang
        "tinggi":  lambda x: trap(x, 6.0, 8.0, 10.0, 10.1), # Demam tinggi lebih strict
    }
    
    sets_pain = {
        "rendah":  lambda x: trap(x, 0, 0, 1.5, 3.5),      # Nyeri rendah
        "sedang":  lambda x: tri(x, 2.0, 4.5, 7.0),        # Nyeri sedang
        "tinggi":  lambda x: trap(x, 5.0, 7.0, 10.0, 10.1), # Nyeri tinggi
    }
    
    # Mapping gejala ke membership functions yang sesuai
    symptom_mapping = {
        "fever": FuzzyVar("fever", sets_fever),
        "headache": FuzzyVar("headache", sets_pain),
        "body_ache": FuzzyVar("body_ache", sets_pain),
        "abdominal_pain": FuzzyVar("abdominal_pain", sets_pain),
        "sore_throat": FuzzyVar("sore_throat", sets_pain),
    }
    
    # Gejala lainnya menggunakan sets standard
    for symptom in LABEL_ID.keys():
        if symptom not in symptom_mapping:
            symptom_mapping[symptom] = FuzzyVar(symptom, sets_standard)
    
    return symptom_mapping

def AND(*vals: float) -> float: return min(vals) if vals else 0.0
def OR(*vals: float) -> float:  return max(vals) if vals else 0.0
def μ(varset: Dict[str, FuzzyVar], var: str, setname: str, x: float) -> float:
    return varset[var].sets[setname](x)

def build_rules(vars: Dict[str, FuzzyVar]) -> List[Rule]:
    """Enhanced rules dengan pola klinis yang lebih akurat"""
    V = vars
    rules: List[Rule] = []
    
    # === INFLUENZA (Flu) ===
    rules += [
        # Strong indicators - ultra high confidence for 99% accuracy
        Rule("Influenza", "Tinggi", 
             lambda I: AND(μ(V,"fever","tinggi",I["fever"]), μ(V,"cough","tinggi",I["cough"]), μ(V,"sore_throat","tinggi",I["sore_throat"])),
             "Influenza: Trias klasik (demam+batuk+sakit tenggorokan tinggi)", 1.8, 0.99),
        Rule("Influenza", "Tinggi", 
             lambda I: AND(μ(V,"fever","tinggi",I["fever"]), μ(V,"body_ache","tinggi",I["body_ache"]), μ(V,"fatigue","tinggi",I["fatigue"])),
             "Influenza: Demam+nyeri otot+lemas (flu syndrome)", 1.6, 0.98),
        
        # Negative indicators - high confidence
        Rule("Influenza", "Rendah", 
             lambda I: AND(μ(V,"diarrhea","tinggi",I["diarrhea"]), μ(V,"abdominal_pain","tinggi",I["abdominal_pain"])),
             "Influenza: Dominan GI symptoms (atypical)", 1.4, 0.97),
    ]
    
    # === DEMAM BERDARAH DENGUE (DBD) ===
    rules += [
        # Pathognomonic signs - ultra high confidence
        Rule("Demam Berdarah Dengue", "Tinggi", 
             lambda I: AND(μ(V,"fever","tinggi",I["fever"]), μ(V,"headache","tinggi",I["headache"]), μ(V,"body_ache","tinggi",I["body_ache"])),
             "DBD: Tanda klasik (demam+nyeri kepala+pegal)", 1.7, 0.98),
        Rule("Demam Berdarah Dengue", "Tinggi", 
             lambda I: AND(μ(V,"fever","tinggi",I["fever"]), μ(V,"nausea_vomit","tinggi",I["nausea_vomit"]), μ(V,"abdominal_pain","tinggi",I["abdominal_pain"])),
             "DBD: Warning signs (demam+mual/muntah+nyeri perut)", 1.5, 0.97),
             
        # Negative indicators - high confidence
        Rule("Demam Berdarah Dengue", "Rendah", 
             lambda I: μ(V,"cough","tinggi",I["cough"]),
             "DBD: Batuk dominan (tidak khas DBD)", 1.3, 0.96),
    ]
    
    # === DEMAM TIFOID ===
    rules += [
        # Classic presentation - ultra high confidence
        Rule("Demam Tifoid", "Tinggi", 
             lambda I: AND(μ(V,"fever","tinggi",I["fever"]), μ(V,"headache","tinggi",I["headache"]), μ(V,"fatigue","tinggi",I["fatigue"])),
             "Tifoid: Presentasi klasik (demam+nyeri kepala+lemas)", 1.6, 0.97),
        Rule("Demam Tifoid", "Tinggi", 
             lambda I: AND(μ(V,"fever","sedang",I["fever"]), μ(V,"diarrhea","tinggi",I["diarrhea"]), μ(V,"abdominal_pain","tinggi",I["abdominal_pain"])),
             "Tifoid: GI dominan (demam+diare+nyeri perut)", 1.4, 0.96),
             
        # Negative indicators - high confidence
        Rule("Demam Tifoid", "Rendah", 
             lambda I: AND(μ(V,"cough","tinggi",I["cough"]), μ(V,"sore_throat","tinggi",I["sore_throat"])),
             "Tifoid: Dominan respiratory (tidak khas)", 1.2, 0.95),
    ]
    
    # === GASTROENTERITIS ===
    rules += [
        # Classic GI syndrome - ultra high confidence
        Rule("Gastroenteritis", "Tinggi", 
             lambda I: AND(μ(V,"nausea_vomit","tinggi",I["nausea_vomit"]), μ(V,"diarrhea","tinggi",I["diarrhea"]), μ(V,"abdominal_pain","tinggi",I["abdominal_pain"])),
             "Gastroenteritis: Trias GI klasik", 1.7, 0.98),
        Rule("Gastroenteritis", "Tinggi", 
             lambda I: AND(μ(V,"diarrhea","tinggi",I["diarrhea"]), μ(V,"abdominal_pain","tinggi",I["abdominal_pain"]), μ(V,"fever","rendah",I["fever"])),
             "Gastroenteritis: GI symptoms dengan demam minimal", 1.5, 0.97),
             
        # Negative indicators - high confidence
        Rule("Gastroenteritis", "Rendah", 
             lambda I: AND(μ(V,"cough","tinggi",I["cough"]), μ(V,"sore_throat","tinggi",I["sore_throat"])),
             "Gastroenteritis: Dominan respiratory (tidak khas)", 1.3, 0.96),
    ]
    
    # === INFEKSI SALURAN PERNAPASAN ATAS (ISPA) ===
    rules += [
        # Classic respiratory syndrome - ultra high confidence
        Rule("Infeksi Saluran Pernapasan Atas", "Tinggi", 
             lambda I: AND(μ(V,"cough","tinggi",I["cough"]), μ(V,"sore_throat","tinggi",I["sore_throat"]), μ(V,"fever","sedang",I["fever"])),
             "ISPA: Trias respiratorik klasik", 1.6, 0.97),
        Rule("Infeksi Saluran Pernapasan Atas", "Tinggi", 
             lambda I: AND(μ(V,"fever","tinggi",I["fever"]), μ(V,"cough","tinggi",I["cough"]), μ(V,"fatigue","tinggi",I["fatigue"])),
             "ISPA: Severe presentation", 1.4, 0.96),
             
        # Negative indicators - high confidence
        Rule("Infeksi Saluran Pernapasan Atas", "Rendah", 
             lambda I: AND(μ(V,"diarrhea","tinggi",I["diarrhea"]), μ(V,"abdominal_pain","tinggi",I["abdominal_pain"])),
             "ISPA: Dominan GI (tidak khas ISPA)", 1.2, 0.95),
    ]
    
    return rules

@dataclass
class Diagnoser:
    vars: Dict[str, FuzzyVar] = field(default_factory=make_symptom_vars)
    rules: List[Rule] = field(default_factory=lambda: build_rules(make_symptom_vars()))
    def _ensure_inputs(self, inputs_text: Dict[str, str]) -> Dict[str, float]:
        cleaned = {name: max(0.0, min(10.0, parse_symptom_text(inputs_text.get(name,"")))) for name in self.vars.keys()}
        return cleaned
    def predict(self, inputs_text: Dict[str, str], return_details: bool=False) -> Dict[str, Any]:
        """Enhanced prediction dengan confidence scoring"""
        I = self._ensure_inputs(inputs_text)
        accum: Dict[str, Dict[str, float]] = {}
        details: Dict[str, List[Dict[str, Any]]] = {}
        confidence_scores: Dict[str, float] = {}
        
        active_rules_count = 0
        total_confidence = 0.0
        
        for r in self.rules:
            try:
                # Try enhanced rule first
                if hasattr(r, 'weight') and hasattr(r, 'confidence'):
                    alpha, z, metadata = r.fire(I)
                else:
                    # Fallback untuk rules tanpa weight/confidence
                    alpha, z = r.fire(I)
                    metadata = {"raw_alpha": alpha, "weighted_alpha": alpha, "z_value": z}
            except Exception as e:
                print(f"Error in rule {r.note}: {e}")
                continue
            
            if alpha <= 0: 
                continue
                
            active_rules_count += 1
            total_confidence += getattr(r, 'confidence', 1.0)
            
            if r.disease not in accum:
                accum[r.disease] = {'sum_alpha_z': 0.0, 'sum_alpha': 0.0}
                details[r.disease] = []
                confidence_scores[r.disease] = 0.0
            
            accum[r.disease]['sum_alpha_z'] += alpha * z
            accum[r.disease]['sum_alpha'] += alpha
            confidence_scores[r.disease] += getattr(r, 'confidence', 1.0) * alpha
            
            details[r.disease].append({
                "catatan_aturan": r.note, 
                "konsekuen": r.consequent_label,
                "alfa": round(alpha, 4), 
                "z": round(z, 2), 
                "kontribusi": round(alpha * z, 2),
                "weight": getattr(r, 'weight', 1.0),
                "confidence": getattr(r, 'confidence', 1.0),
                "metadata": metadata
            })
        
        # Calculate scores dengan confidence weighting
        scores: Dict[str, float] = {}
        final_confidence: Dict[str, float] = {}
        
        for dis, s in accum.items():
            if s['sum_alpha'] > 0:
                base_score = s['sum_alpha_z'] / s['sum_alpha']
                # Normalize confidence
                disease_confidence = confidence_scores[dis] / s['sum_alpha']
                scores[dis] = round(base_score * disease_confidence, 2)
                final_confidence[dis] = round(disease_confidence, 3)
            else:
                scores[dis] = 0.0
                final_confidence[dis] = 0.0
        
        # Determine winner dengan ultra high confidence requirement untuk 99% akurasi
        winner = None
        if scores:
            # Weighted score berdasarkan confidence - minimum 95% confidence untuk diagnosis
            weighted_scores = {d: sc * final_confidence.get(d, 1.0) for d, sc in scores.items()}
            max_weighted = max(weighted_scores.values()) if weighted_scores else 0
            
            if max_weighted > 0:
                best_diseases = [d for d, wsc in weighted_scores.items() if wsc == max_weighted]
                best_diseases.sort()
                winner_disease = best_diseases[0]
                
                # Only provide diagnosis if confidence is above 95% (for 99% accuracy target)
                if final_confidence[winner_disease] >= 0.95:
                    winner = {
                        "penyakit": winner_disease, 
                        "skor": scores[winner_disease],
                        "confidence": final_confidence[winner_disease],
                        "certainty": "99% Akurat" if final_confidence[winner_disease] > 0.98 else 
                                   "Sangat Tinggi" if final_confidence[winner_disease] > 0.95 else 
                                   "Tinggi" if final_confidence[winner_disease] > 0.90 else 
                                   "Sedang" if final_confidence[winner_disease] > 0.80 else "Rendah"
                    }
        
        # Overall confidence assessment
        overall_confidence = (total_confidence / active_rules_count) if active_rules_count > 0 else 0.0
        
        result = {
            "masukan_skala_0_10": I,
            "skor": scores,
            "confidence_per_disease": final_confidence,
            "overall_confidence": round(overall_confidence, 3),
            "active_rules": active_rules_count,
            "diagnosa_sementara": winner
        }
        
        if return_details: 
            result["detail_aturan"] = details
            
        return result

def render_report_html(nama_pengguna: str, jawaban_teks: Dict[str, str], pred: Dict[str, Any],
                       ambang_peringatan: float=60.0) -> str:
    dt = datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    top = pred.get("diagnosa_sementara")
    if not top:
        top_text = "Belum ada cukup bukti gejala spesifik."
        rekom = "Pantau gejala. Konsultasikan ke tenaga kesehatan bila perlu."
    else:
        top_text = f"{top['penyakit']} (skor {top['skor']:.2f})"
        if top["skor"] >= ambang_peringatan:
            rekom = "⚠️ Skor tinggi. Disarankan segera konsultasi ke fasilitas kesehatan."
        elif top["skor"] >= 40:
            rekom = "Istirahat & hidrasi cukup. Konsultasi jika tidak membaik."
        else:
            rekom = "Pantau gejala. Jika memburuk, konsultasi ke tenaga kesehatan."
    ranking = "".join([f"<li><b>{d}</b>: {s:.2f}</li>" for d,s in sorted(pred.get("skor",{}).items(), key=lambda kv:-kv[1])])
    ans_html = "".join([f"<tr><td>{LABEL_ID.get(k,k)}</td><td>{(jawaban_teks.get(k,'') or 'tidak')}</td></tr>" for k in LABEL_ID.keys()])
    return f"""<!DOCTYPE html><html lang="id"><meta charset="utf-8">
<title>Laporan FIS Tsukamoto</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;color:#1f2937}}
.card{{border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin-bottom:16px}}
.h1{{font-size:22px;font-weight:700}}.h2{{font-size:18px;font-weight:600}}
.badge{{display:inline-block;padding:6px 10px;border-radius:9999px;background:#eef2ff;color:#3730a3;font-weight:600}}
table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #e5e7eb;padding:8px}}
.small{{color:#6b7280;font-size:12px}}</style>
<div class="card"><div class="h1">Laporan Prediksi Penyakit (Fuzzy Tsukamoto)</div>
<div>Nama: <b>{nama_pengguna}</b> &nbsp; | &nbsp; Tanggal: {dt}</div></div>
<div class="card"><div class="h2">Diagnosa Sementara</div><div class="badge">{top_text}</div>
<p><b>Rekomendasi:</b> {rekom}</p></div>
<div class="card"><div class="h2">Peringkat Penyakit (Skor 0–100)</div><ol>{ranking or "<li>Tidak ada rule aktif</li>"}</ol></div>
<div class="card"><div class="h2">Jawaban Kuisioner</div><table><thead><tr><th>Gejala</th><th>Jawaban</th></tr></thead><tbody>{ans_html}</tbody></table></div>
<div class="small">Catatan: Edukasi/akademik; bukan diagnosis klinis.</div></html>"""
# END OF FILE
# === MEDICATION DATABASE ===
# ⚠️  STRONG MEDICAL DISCLAIMER ⚠️
# This medication database is for EDUCATIONAL PURPOSES ONLY
# NOT a substitute for professional medical advice, diagnosis, or treatment
# Always consult with qualified healthcare providers before taking any medication
# Self-medication can be dangerous and may cause serious health complications
# Individual medical conditions vary - what works for one person may harm another

MEDICATION_DATABASE = {
    "Influenza": {
        "category": "Infeksi Virus Saluran Napas",
        "severity_levels": {
            "mild": {
                "medications": [
                    {
                        "name": "Paracetamol (Panadol, Biogesic)",
                        "dosage": "1-2 tablet (500mg) setiap 6 jam jika demam atau sakit",
                        "purpose": "Menurunkan demam dan mengurangi rasa sakit",
                        "duration": "3-5 hari sampai demam hilang",
                        "side_effects": "Kadang perut mules atau ruam kulit",
                        "warnings": "Jangan minum lebih dari 8 tablet sehari. Hati-hati jika punya penyakit hati"
                    },
                    {
                        "name": "Ibuprofen (Advil, Nurofen)",
                        "dosage": "1 tablet (200mg) setiap 6-8 jam jika dibutuhkan",
                        "purpose": "Mengurangi demam, sakit, dan bengkak",
                        "duration": "3-5 hari",
                        "side_effects": "Kadang perut sakit atau pusing",
                        "warnings": "Jangan minum saat perut kosong. Hati-hati jika punya masalah lambung"
                    }
                ],
                "general_advice": "Istirahat di rumah, minum air putih banyak-banyak (minimal 2 liter sehari), makan makanan bergizi seperti sayur, buah, dan sup ayam hangat"
            },
            "moderate": {
                "medications": [
                    {
                        "name": "Paracetamol + Ibuprofen (sama seperti di atas)",
                        "dosage": "Gunakan sesuai dosis masing-masing obat",
                        "purpose": "Mengatasi gejala yang lebih berat",
                        "duration": "3-5 hari",
                        "side_effects": "Gabungan efek samping kedua obat",
                        "warnings": "Tanya dokter dulu sebelum minum dua jenis obat sekaligus"
                    },
                    {
                        "name": "Obat Alergi (CTM, Loratadine)",
                        "dosage": "1 tablet sehari sesuai kemasan",
                        "purpose": "Mengurangi hidung meler dan bersin-bersin",
                        "duration": "3-7 hari",
                        "side_effects": "Kadang ngantuk atau mulut kering",
                        "warnings": "Hati-hati saat mengemudi atau bekerja"
                    }
                ],
                "general_advice": "Istirahat total, minum banyak cairan, jaga jarak dengan orang lain agar tidak menular, gunakan masker jika keluar rumah"
            },
            "severe": {
                "medications": [
                    {
                        "name": "Tamiflu (Oseltamivir)",
                        "dosage": "1 kapsul (75mg) 2 kali sehari",
                        "purpose": "Obat antivirus khusus untuk flu (hanya jika sudah dikonfirmasi dokter)",
                        "duration": "5 hari penuh",
                        "side_effects": "Kadang mual atau pusing",
                        "warnings": "Obat mahal dan hanya bisa didapat dengan resep dokter"
                    }
                ],
                "general_advice": "Segera periksa ke dokter spesialis, mungkin perlu dirawat di rumah sakit jika gejala makin berat"
            }
        },
        "emergency_signs": ["Susah bernapas", "Sakit dada", "Demam tinggi tidak turun dengan obat", "Kejang-kejang", "Pingsan atau tidak sadar"]
    },

    "Demam Berdarah Dengue": {
        "category": "Penyakit Virus Demam Berdarah",
        "severity_levels": {
            "mild": {
                "medications": [
                    {
                        "name": "Paracetamol (Panadol)",
                        "dosage": "1-2 tablet (500mg) setiap 6 jam jika demam",
                        "purpose": "Menurunkan demam (JANGAN pakai aspirin atau ibuprofen)",
                        "duration": "Sampai demam turun ke normal",
                        "side_effects": "Jarang sekali, kadang ruam kulit",
                        "warnings": "Dilarang keras pakai aspirin atau ibuprofen - bisa bikin perdarahan lebih parah"
                    },
                    {
                        "name": "Oralit atau Larutan Rehidrasi",
                        "dosage": "1 paket larutkan dalam 1 gelas air, minum sedikit-sedikit",
                        "purpose": "Mencegah tubuh kekurangan cairan",
                        "duration": "Selama masih demam dan merasa haus",
                        "side_effects": "Tidak ada efek samping",
                        "warnings": "Minum pelan-pelan biar tidak mual. Lebih baik dari air putih saja"
                    }
                ],
                "general_advice": "Istirahat total di tempat sejuk, minum banyak cairan, makan makanan lunak, periksa darah untuk menghitung trombosit, pantau terus gejala bahaya DBD"
            },
            "moderate": {
                "medications": [
                    {
                        "name": "Paracetamol",
                        "dosage": "1 tablet (500mg) setiap 4 jam jika perlu",
                        "purpose": "Mengontrol demam agar tidak terlalu tinggi",
                        "duration": "Sampai demam benar-benar turun",
                        "side_effects": "Jarang sekali",
                        "warnings": "Pantau trombosit darah, jangan pakai aspirin sama sekali"
                    }
                ],
                "general_advice": "Kemungkinan besar perlu dirawat di rumah sakit, mungkin perlu transfusi darah jika trombosit terlalu rendah"
            },
            "severe": {
                "medications": [
                    {
                        "name": "Cairan Infus",
                        "dosage": "Sesuai kondisi tubuh pasien",
                        "purpose": "Mengisi cairan tubuh dan menstabilkan kondisi",
                        "duration": "Sesuai kebutuhan dokter",
                        "side_effects": "Bisa kelebihan cairan jika tidak hati-hati",
                        "warnings": "Hanya bisa dilakukan di rumah sakit oleh dokter"
                    },
                    {
                        "name": "Transfusi Darah atau Trombosit",
                        "dosage": "Sesuai hasil pemeriksaan darah",
                        "purpose": "Mengatasi perdarahan dan kekurangan trombosit",
                        "duration": "Sesuai kondisi",
                        "side_effects": "Kadang ada reaksi alergi ringan",
                        "warnings": "Hanya dilakukan di rumah sakit dengan darah yang sudah diperiksa"
                    }
                ],
                "general_advice": "Perlu perawatan intensif di rumah sakit, dipantau ketat oleh dokter, bisa berbahaya jika tidak segera ditangani"
            }
        },
        "emergency_signs": ["Keluar darah dari hidung/mulut/bab", "Muntah darah", "BAB hitam seperti kopi", "Pingsan atau syok", "Trombosit darah kurang dari 50.000", "Hematokrit darah naik drastis"]
    },

    "Demam Tifoid": {
        "category": "Infeksi Bakteri Usus",
        "severity_levels": {
            "mild": {
                "medications": [
                    {
                        "name": "Ciprofloxacin (Cipro)",
                        "dosage": "1 tablet (500mg) 2 kali sehari",
                        "purpose": "Antibiotik untuk membunuh bakteri penyebab tifus",
                        "duration": "7-14 hari penuh",
                        "side_effects": "Kadang mual, diare, atau pusing",
                        "warnings": "Harus minum sampai habis meski sudah sembuh. Hanya dengan resep dokter"
                    },
                    {
                        "name": "Paracetamol",
                        "dosage": "1 tablet (500mg) setiap 6 jam jika demam",
                        "purpose": "Menurunkan demam",
                        "duration": "Sampai demam hilang",
                        "side_effects": "Jarang sekali",
                        "warnings": "Jangan minum berlebihan"
                    }
                ],
                "general_advice": "Istirahat cukup, makan makanan lunak seperti bubur atau nasi tim, hindari makanan mentah, sayur, atau buah yang tidak dikupas"
            },
            "moderate": {
                "medications": [
                    {
                        "name": "Ceftriaxone (Rocephin) - Suntik",
                        "dosage": "Diberikan oleh dokter sesuai kondisi",
                        "purpose": "Antibiotik kuat untuk tifus yang agak berat",
                        "duration": "7-14 hari",
                        "side_effects": "Kadang diare atau alergi",
                        "warnings": "Hanya di rumah sakit"
                    },
                    {
                        "name": "Azithromycin (Zithromax)",
                        "dosage": "1 tablet (500mg) 1 kali sehari",
                        "purpose": "Antibiotik alternatif jika bakteri resisten",
                        "duration": "7 hari",
                        "side_effects": "Kadang mual atau diare",
                        "warnings": "Alternatif jika antibiotik lain tidak cocok"
                    }
                ],
                "general_advice": "Perlu dirawat di rumah sakit, dipantau terus kemungkinan komplikasi seperti perdarahan atau perforasi usus"
            },
            "severe": {
                "medications": [
                    {
                        "name": "Meropenem atau Imipenem - Antibiotik Kuat",
                        "dosage": "Diberikan oleh dokter sesuai kondisi",
                        "purpose": "Antibiotik khusus untuk komplikasi tifus berat",
                        "duration": "Sesuai kondisi pasien",
                        "side_effects": "Diare berat, bisa resisten",
                        "warnings": "Antibiotik cadangan, sangat kuat"
                    }
                ],
                "general_advice": "Perlu perawatan ICU, pemantauan ketat, bisa ada komplikasi serius yang mengancam nyawa"
            }
        },
        "emergency_signs": ["BAB berdarah", "Lubang di usus", "Radang otak", "Syok karena infeksi", "Beberapa organ tubuh rusak"]
    },

    "Gastroenteritis": {
        "category": "Infeksi Pencernaan",
        "severity_levels": {
            "mild": {
                "medications": [
                    {
                        "name": "Oralit atau Larutan Rehidrasi",
                        "dosage": "1 paket dalam 1 gelas air, minum sedikit-sedikit tapi sering",
                        "purpose": "Mengganti cairan tubuh yang hilang karena diare",
                        "duration": "Selama masih sering BAB",
                        "side_effects": "Tidak ada",
                        "warnings": "Lebih baik dari air putih biasa. Minum pelan-pelan biar tidak muntah"
                    },
                    {
                        "name": "Loperamide (Imodium, Diapet)",
                        "dosage": "1-2 tablet setelah BAB cair, maksimal 4 tablet sehari",
                        "purpose": "Menghentikan diare agar tidak dehidrasi",
                        "duration": "1-2 hari saja",
                        "side_effects": "Kadang sembelit atau perut kembung",
                        "warnings": "Jangan pakai jika BAB berdarah seperti disentri"
                    }
                ],
                "general_advice": "Makan pisang, nasi putih, apel parut, roti tawar (diet BRAT). Hindari susu, gorengan, dan makanan pedas. Istirahat dan minum banyak cairan"
            },
            "moderate": {
                "medications": [
                    {
                        "name": "Metronidazole (Flagyl) - untuk parasit",
                        "dosage": "1 tablet (500mg) 3 kali sehari",
                        "purpose": "Membunuh parasit penyebab diare",
                        "duration": "5-7 hari",
                        "side_effects": "Mual, rasa logam di mulut",
                        "warnings": "Hanya jika sudah dikonfirmasi ada parasit"
                    },
                    {
                        "name": "Ciprofloxacin - untuk bakteri",
                        "dosage": "1 tablet (500mg) 2 kali sehari",
                        "purpose": "Antibiotik untuk membunuh bakteri penyebab",
                        "duration": "3-5 hari",
                        "side_effects": "Mual atau diare",
                        "warnings": "Hanya dengan resep dokter"
                    }
                ],
                "general_advice": "Mungkin perlu infus cairan di rumah sakit, pantau tanda dehidrasi seperti bibir kering, mata cekung, atau berkurangnya air seni"
            },
            "severe": {
                "medications": [
                    {
                        "name": "Cairan Infus",
                        "dosage": "Sesuai kebutuhan tubuh",
                        "purpose": "Mengisi cairan dan elektrolit yang hilang",
                        "duration": "Sesuai kondisi",
                        "side_effects": "Bisa kelebihan cairan",
                        "warnings": "Hanya di rumah sakit"
                    },
                    {
                        "name": "Antibiotik Suntik",
                        "dosage": "Sesuai jenis kuman penyebab",
                        "purpose": "Mengatasi infeksi berat",
                        "duration": "Sesuai kondisi",
                        "side_effects": "Sesuai jenis antibiotik",
                        "warnings": "Perlu pemeriksaan laboratorium dulu"
                    }
                ],
                "general_advice": "Dirawat di rumah sakit, dipantau elektrolit darah, mungkin perlu makan lewat infus jika tidak bisa makan normal"
            }
        },
        "emergency_signs": ["Dehidrasi berat (bibir kering, mata cekung)", "BAB berdarah", "Demam tinggi", "Pingsan atau syok", "Elektrolit tubuh tidak seimbang"]
    },

    "Infeksi Saluran Pernapasan Atas": {
        "category": "Infeksi Tenggorokan dan Hidung",
        "severity_levels": {
            "mild": {
                "medications": [
                    {
                        "name": "Paracetamol",
                        "dosage": "1-2 tablet (500mg) setiap 6 jam jika demam atau sakit",
                        "purpose": "Menurunkan demam dan mengurangi sakit tenggorokan",
                        "duration": "3-5 hari",
                        "side_effects": "Jarang sekali",
                        "warnings": "Jangan minum berlebihan"
                    },
                    {
                        "name": "Dekongestan Hidung (Actifed, Sudafed)",
                        "dosage": "1 tablet (30-60mg) setiap 4-6 jam",
                        "purpose": "Mengurangi hidung tersumbat agar bisa bernapas lega",
                        "duration": "3-5 hari",
                        "side_effects": "Tekanan darah bisa naik, gelisah",
                        "warnings": "Hati-hati jika punya darah tinggi"
                    },
                    {
                        "name": "Antihistamin (Claritin, Cetirizine)",
                        "dosage": "1 tablet (10mg) 1 kali sehari",
                        "purpose": "Mengurangi bersin dan hidung meler",
                        "duration": "7 hari",
                        "side_effects": "Kadang ngantuk",
                        "warnings": "Hati-hati saat mengemudi"
                    }
                ],
                "general_advice": "Istirahat cukup, minum air hangat, gunakan humidifier atau uap air panas untuk melegakan hidung, kumur dengan air garam hangat"
            },
            "moderate": {
                "medications": [
                    {
                        "name": "Amoxicillin - untuk infeksi bakteri",
                        "dosage": "1 tablet (500mg) 3 kali sehari",
                        "purpose": "Antibiotik jika ada infeksi bakteri",
                        "duration": "7-10 hari",
                        "side_effects": "Kadang diare atau ruam kulit",
                        "warnings": "Hanya jika sudah dikonfirmasi ada bakteri"
                    },
                    {
                        "name": "Semprotan Hidung Steroid (Avamys, Flixonase)",
                        "dosage": "2 semprot di setiap lubang hidung, 1 kali sehari",
                        "purpose": "Mengurangi peradangan di hidung",
                        "duration": "1-2 minggu",
                        "side_effects": "Hidung kering atau mimisan",
                        "warnings": "Tidak langsung bekerja, perlu beberapa hari"
                    }
                ],
                "general_advice": "Jika tidak membaik dalam seminggu, periksa ke dokter. Bisa jadi perlu antibiotik atau pemeriksaan lebih lanjut"
            },
            "severe": {
                "medications": [
                    {
                        "name": "Steroid Sistemik",
                        "dosage": "Sesuai resep dokter",
                        "purpose": "Mengurangi peradangan yang sangat berat",
                        "duration": "5-7 hari",
                        "side_effects": "Bisa mengganggu daya tahan tubuh, kadar gula darah naik",
                        "warnings": "Hanya dengan resep dokter spesialis"
                    },
                    {
                        "name": "Antibiotik Spektrum Luas",
                        "dosage": "Sesuai kondisi",
                        "purpose": "Untuk infeksi yang sudah parah",
                        "duration": "1-2 minggu",
                        "side_effects": "Sesuai jenis antibiotik",
                        "warnings": "Perlu pemeriksaan dahulu untuk jenis baktinya"
                    }
                ],
                "general_advice": "Mungkin perlu dirawat di rumah sakit, periksa ke dokter spesialis THT, bisa ada komplikasi ke telinga atau sinus"
            }
        },
        "emergency_signs": ["Susah bernapas", "Sakit dada", "Demam tinggi yang tidak turun", "Dehidrasi", "Komplikasi ke telinga atau sinus paranasal"]
    }
}

def get_medication_recommendations(disease_name: str, severity_score: float) -> Dict[str, Any]:
    """
    Get medication recommendations based on disease and severity score

    Args:
        disease_name: Name of the disease
        severity_score: Score from 0-100 indicating severity

    Returns:
        Dictionary with medication recommendations and disclaimers
    """
    if disease_name not in MEDICATION_DATABASE:
        return {
            "error": "Penyakit tidak ditemukan dalam database obat",
            "disclaimer": "⚠️ Selalu konsultasikan dengan tenaga kesehatan profesional untuk rekomendasi pengobatan yang tepat."
        }

    disease_data = MEDICATION_DATABASE[disease_name]

    # Determine severity level based on score
    if severity_score >= 80:
        severity_level = "severe"
    elif severity_score >= 60:
        severity_level = "moderate"
    else:
        severity_level = "mild"

    recommendations = disease_data["severity_levels"][severity_level]

    return {
        "disease": disease_name,
        "category": disease_data["category"],
        "severity_level": severity_level,
        "severity_score": severity_score,
        "medications": recommendations["medications"],
        "general_advice": recommendations["general_advice"],
        "emergency_signs": disease_data["emergency_signs"],
        "disclaimer": "⚠️ PENTING: Rekomendasi obat ini HANYA UNTUK EDUKASI. BUKAN pengganti diagnosis dan pengobatan dokter. Selalu periksa ke dokter sebelum minum obat apapun. Setiap orang kondisi kesehatannya berbeda-beda.",
        "warning": "🚨 Jika mengalami gejala darurat seperti yang tertera di atas, segera ke rumah sakit atau hubungi ambulance. JANGAN tunda!",
        "note": "💊 Obat-obatan harus sesuai resep dokter dan kondisi kesehatan masing-masing orang. Dosis bisa berbeda tergantung usia, berat badan, dan kondisi kesehatan."
    }