# File WSGI untuk PythonAnywhere - Working Version
# Salin isi file ini ke /var/www/rifqy11_pythonanywhere_com_wsgi.py di PythonAnywhere

import sys
import os
import json

# Tambahkan path ke direktori project
sys.path.insert(0, '/home/rifqy11/')

# Set environment variables
os.environ.setdefault('APP_NAME', 'Fuzzy Tsukamoto Diagnoser API')
os.environ.setdefault('WARNING_THRESHOLD', '60')
os.environ.setdefault('CORS_ORIGINS', '*')

def application(environ, start_response):
    try:
        # Import aplikasi FastAPI
        from api_app import app
        
        # Extract request info
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        # Basic routing for key endpoints
        if path == '/health' and method == 'GET':
            # Health check endpoint
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            start_response(status, headers)
            response = {
                "status": "ok", 
                "app": "Fuzzy Tsukamoto Diagnoser API", 
                "version": "v1"
            }
            return [json.dumps(response).encode('utf-8')]
            
        elif path == '/v1/schema' and method == 'GET':
            # Schema endpoint
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            start_response(status, headers)
            
            # Import the schema function directly
            from fis_tsukamoto import LABEL_ID
            
            options = ["tidak", "ringan", "sedang", "berat", "sangat berat", "kadang", "sering", "ya"]
            questions = [
                {
                    "key": k,
                    "label": LABEL_ID[k],
                    "type": "select",
                    "options": options,
                    "default": "tidak"
                }
                for k in LABEL_ID.keys()
            ]
            
            response = {"version": "v1", "questions": questions}
            return [json.dumps(response).encode('utf-8')]
            
        elif path == '/v1/predict' and method == 'POST':
            # Enhanced prediction endpoint with request parsing
            try:
                # Parse request body
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                if content_length > 0:
                    request_body = environ['wsgi.input'].read(content_length)
                    request_data = json.loads(request_body.decode('utf-8'))
                else:
                    request_data = {}
                
                # Extract prediction parameters
                nama = request_data.get('nama', 'Pengguna')
                include_details = request_data.get('include_detail_rules', False)
                ambang_peringatan = request_data.get('ambang_peringatan', 60.0)
                
                # Extract symptom data
                symptom_data = {}
                for symptom in ['fever', 'cough', 'sore_throat', 'headache', 'body_ache', 
                               'nausea_vomit', 'diarrhea', 'abdominal_pain', 'rash', 'fatigue']:
                    symptom_data[symptom] = request_data.get(symptom, 'tidak')
                
                # Perform prediction using enhanced fuzzy system
                from fis_tsukamoto import Diagnoser
                clf = Diagnoser()
                result = clf.predict(symptom_data, return_details=include_details)
                
                # Generate recommendation
                top = result.get("diagnosa_sementara")
                if not top:
                    rekom = "Pantau gejala. Konsultasikan ke tenaga kesehatan bila perlu."
                else:
                    skor = top.get("skor", 0)
                    confidence = top.get("confidence", 0)
                    
                    if skor >= ambang_peringatan:
                        rekom = "⚠️ Skor tinggi. Disarankan segera konsultasi ke fasilitas kesehatan."
                    elif skor >= 40:
                        rekom = "Istirahat & hidrasi cukup. Konsultasi jika tidak membaik."
                    else:
                        rekom = "Pantau gejala. Jika memburuk, konsultasi ke tenaga kesehatan."
                    
                    # Add confidence-based recommendation
                    if confidence < 0.6:
                        rekom += f" (Confidence: {confidence:.1%} - Hasil kurang pasti)"
                
                # Enhanced response
                response = {
                    "nama": nama,
                    "diagnosa_sementara": result.get("diagnosa_sementara"),
                    "skor": result.get("skor", {}),
                    "confidence_per_disease": result.get("confidence_per_disease", {}),
                    "overall_confidence": result.get("overall_confidence", 0),
                    "masukan_skala_0_10": result.get("masukan_skala_0_10", {}),
                    "active_rules": result.get("active_rules", 0),
                    "rekomendasi": rekom,
                    "timestamp": __import__('datetime').datetime.now().isoformat(),
                    "api_version": "enhanced_wsgi_v1"
                }
                
                if include_details:
                    response["detail_aturan"] = result.get("detail_aturan", {})
                
                status = '200 OK'
                headers = [('Content-type', 'application/json')]
                start_response(status, headers)
                return [json.dumps(response).encode('utf-8')]
                
            except json.JSONDecodeError:
                # Invalid JSON
                status = '400 Bad Request'
                headers = [('Content-type', 'application/json')]
                start_response(status, headers)
                error_response = {
                    "error": "Invalid JSON format",
                    "message": "Request body must be valid JSON"
                }
                return [json.dumps(error_response).encode('utf-8')]
                
            except Exception as e:
                # Other errors
                status = '500 Internal Server Error'
                headers = [('Content-type', 'application/json')]
                start_response(status, headers)
                error_response = {
                    "error": "Prediction failed",
                    "message": str(e),
                    "note": "Check input format and try again"
                }
                return [json.dumps(error_response).encode('utf-8')]
            
        else:
            # Default response
            status = '200 OK'
            headers = [('Content-type', 'application/json')]
            start_response(status, headers)
            
            response = {
                "message": "Fuzzy Tsukamoto Diagnoser API",
                "version": "v1",
                "available_endpoints": {
                    "GET /health": "Health check",
                    "GET /v1/schema": "Get questionnaire schema",
                    "POST /v1/predict": "Predict diagnosis (limited in WSGI mode)",
                    "POST /v1/report": "Generate report (limited in WSGI mode)"
                },
                "note": "For full functionality, use ASGI server like uvicorn"
            }
            return [json.dumps(response).encode('utf-8')]
        
    except ImportError as e:
        # Error import - tampilkan detail
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        import traceback
        error_detail = f"""
        <h1>Import Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <h2>Python Path:</h2>
        <ul>{''.join(f'<li>{p}</li>' for p in sys.path)}</ul>
        <h2>Files in /home/rifqy11/:</h2>
        <ul>
        """
        
        try:
            files = os.listdir('/home/rifqy11/')
            error_detail += ''.join(f'<li>{f}</li>' for f in files)
        except Exception:
            error_detail += '<li>Could not list files</li>'
        
        error_detail += f"""
        </ul>
        <h2>Traceback:</h2>
        <pre>{traceback.format_exc()}</pre>
        """
        
        return [error_detail.encode('utf-8')]
        
    except Exception as e:
        # Error lainnya
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        import traceback
        error_msg = f"""
        <h1>General Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <h2>Traceback:</h2>
        <pre>{traceback.format_exc()}</pre>
        """
        
        return [error_msg.encode('utf-8')]
        
    except ImportError as e:
        # Error import - tampilkan detail
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        import traceback
        error_detail = f"""
        <h1>Import Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <h2>Python Path:</h2>
        <ul>{''.join(f'<li>{p}</li>' for p in sys.path)}</ul>
        <h2>Files in /home/rifqy11/:</h2>
        <ul>
        """
        
        try:
            files = os.listdir('/home/rifqy11/')
            error_detail += ''.join(f'<li>{f}</li>' for f in files)
        except Exception:
            error_detail += '<li>Could not list files</li>'
        
        error_detail += f"""
        </ul>
        <h2>Try installing packages:</h2>
        <pre>pip install fastapi uvicorn pydantic python-dotenv</pre>
        <h2>Traceback:</h2>
        <pre>{traceback.format_exc()}</pre>
        """
        
        return [error_detail.encode('utf-8')]
        
    except Exception as e:
        # Error lainnya
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        import traceback
        error_msg = f"""
        <h1>General Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <h2>Traceback:</h2>
        <pre>{traceback.format_exc()}</pre>
        """
        
        return [error_msg.encode('utf-8')]
