# Load environment variables from .env before anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; env vars must be set externally

from flask import Flask, request, jsonify
from flask_cors import CORS
from respiratory_agent_api import RespiratoryAgent
from general_agent_api_xgboost import GeneralHealthAgent
from cardiac_agent_api import CardiacAgent
from sepsis_agent_api import SepsisAgent
import logging
from datetime import datetime
import json
import os
import csv
import numpy as np
import sqlite3
import uuid

# HCAI agents and report generator
try:
    from agents.summary_agent import SummaryAgent
    from reports.report_generator import ReportGenerator
    _HCAI_AVAILABLE = True
except ImportError as _e:
    _HCAI_AVAILABLE = False
    _HCAI_IMPORT_ERROR = str(_e)

app = Flask(__name__)
CORS(app)  # Enable React frontend to call this API

# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles NumPy data types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super().default(obj)

app.json_encoder = NumpyEncoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load agents once (on startup)
respiratory_agent = None
general_agent = None
cardiac_agent = None
sepsis_agent = None

try:
    respiratory_agent = RespiratoryAgent()
    logger.info("✓ Respiratory Agent loaded successfully")
except Exception as e:
    logger.error(f"Failed to load respiratory agent: {e}")

try:
    general_agent = GeneralHealthAgent()
    logger.info("✓ General Health Agent loaded successfully")
except Exception as e:
    logger.error(f"Failed to load general agent: {e}")

try:
    cardiac_agent = CardiacAgent()
    logger.info("✓ Cardiac Agent loaded successfully")
except Exception as e:
    logger.error(f"Failed to load cardiac agent: {e}")

try:
    sepsis_agent = SepsisAgent()
    logger.info("✓ Sepsis Agent loaded successfully")
except Exception as e:
    logger.error(f"Failed to load sepsis agent: {e}")

# ── HCAI agents (lazy-initialised, safe if agents/ not yet present) ──
_summary_agent = None
_report_generator = None

if _HCAI_AVAILABLE:
    try:
        _summary_agent = SummaryAgent()
        _report_generator = ReportGenerator()
        logger.info("✓ HCAI SummaryAgent + ReportGenerator loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load HCAI agents: {e}")
else:
    logger.warning(f"HCAI agents not available: {_HCAI_IMPORT_ERROR if '_HCAI_IMPORT_ERROR' in dir() else 'import error'}")

# ==================== RESPIRATORY ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': {
            'respiratory': respiratory_agent is not None,
            'general': general_agent is not None,
            'cardiac': cardiac_agent is not None,
            'sepsis': sepsis_agent is not None
        }
    }), 200

@app.route('/respiratory/predict', methods=['POST'])
def respiratory_predict():
    """
    Single respiratory patient prediction
    
    POST /respiratory/predict
    Body: {
        "spo2": 95,
        "respiratory_rate": 18,
        "temperature": 37.2,
        "heart_rate": 72,
        "age": 45,
        "sex": "M",
        "age_group": "30-50"
    }
    
    Note: Risk scores and respiratory distress index are calculated 
    automatically by the backend from raw vital signs.
    """
    try:
        if respiratory_agent is None:
            return jsonify({'error': 'Respiratory Agent not loaded'}), 503
        
        patient_data = request.get_json()
        
        # Get prediction (agent validates inputs and calculates risk scores)
        result = respiratory_agent.predict(patient_data)
        
        # Convert NumPy types to native Python types for JSON serialization
        result = json.loads(json.dumps(result, cls=NumpyEncoder))
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        result['patient_data'] = patient_data
        
        logger.info(f"Respiratory Prediction: {result['risk_level']} (conf: {result['confidence']:.2%})")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Respiratory prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/respiratory/batch', methods=['POST'])
def respiratory_batch_predict():
    """
    Multiple respiratory patients prediction
    
    POST /respiratory/batch
    Body: [
        {patient1_data},
        {patient2_data},
        ...
    ]
    """
    try:
        if respiratory_agent is None:
            return jsonify({'error': 'Respiratory Agent not loaded'}), 503
        
        patients = request.get_json()
        
        if not isinstance(patients, list):
            return jsonify({'error': 'Body must be a JSON array'}), 400
        
        results = []
        for i, patient in enumerate(patients):
            try:
                result = respiratory_agent.predict(patient)
                # Convert NumPy types to native Python types
                result = json.loads(json.dumps(result, cls=NumpyEncoder))
                result['patient_index'] = i
                result['timestamp'] = datetime.now().isoformat()
                results.append(result)
            except Exception as e:
                results.append({
                    'patient_index': i,
                    'error': str(e),
                    'status': 'error'
                })
        
        logger.info(f"Respiratory batch prediction: {len(results)} patients processed")
        
        return jsonify({
            'total': len(results),
            'predictions': results
        }), 200
        
    except Exception as e:
        logger.error(f"Respiratory batch prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/respiratory/model-info', methods=['GET'])
def respiratory_model_info():
    """Get respiratory model metadata"""
    return jsonify({
        'model_type': 'RandomForest',
        'n_estimators': 300,
        'test_accuracy': 0.9915,
        'classes': {
            0: 'LOW',
            1: 'MEDIUM',
            2: 'HIGH'
        },
        'features': [
            'spo2', 'respiratory_rate', 'respiratory_distress_index',
            'spo2_risk_score', 'rr_risk_score', 'temp_risk_score',
            'temperature', 'heart_rate', 'age', 'sex', 'age_group'
        ],
        'thresholds': {
            'confidence_high': 0.85,
            'confidence_medium': 0.60,
            'uncertainty_alert': 0.02
        }
    }), 200

@app.route('/respiratory/example-patients', methods=['GET'])
def respiratory_example_patients():
    """Get example respiratory patients for testing"""
    try:
        with open('data/example_patient_healthy.json') as f:
            healthy = json.load(f)
        
        with open('data/example_patient_high_risk.json') as f:
            high_risk = json.load(f)
        
        return jsonify({
            'healthy': {
                'data': healthy,
                'expected_risk': 'LOW'
            },
            'high_risk': {
                'data': high_risk,
                'expected_risk': 'HIGH'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== GENERAL HEALTH ENDPOINTS ====================

@app.route('/general/predict', methods=['POST'])
def general_predict():
    """
    Single general health patient prediction
    
    POST /general/predict
    Body: {
        "age": 45,
        "systolic_bp": 140,
        "diastolic_bp": 90,
        "heart_rate": 95,
        "respiratory_rate": 18,
        "temperature": 37.5,
        "spo2": 96,
        "pain_score": 3,
        "wbc": 7.5,
        "hemoglobin": 13.5,
        "platelet_count": 250,
        "sodium": 138,
        "potassium": 4.0,
        "creatinine": 0.9,
        "glucose": 100,
        "troponin": 0.01,
        "bnp": 50,
        "lactate": 1.5,
        "inr": 1.0,
        "sex": "M",
        "country": "USA",
        "clinical_notes": "Patient presents with chest pain..."  // Optional
    }
    
    Note: Clinical embeddings are generated automatically from clinical_notes
    using ClinicalBERT. Lab values and vital signs are combined for prediction.
    """
    try:
        if general_agent is None:
            return jsonify({'error': 'General Health Agent not loaded'}), 503
        
        patient_data = request.get_json()
        
        # Get prediction (agent validates inputs and generates embeddings)
        result = general_agent.predict(patient_data)
        
        # Convert NumPy types to native Python types for JSON serialization
        result = json.loads(json.dumps(result, cls=NumpyEncoder))
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        result['model_type'] = 'multimodal_lightgbm'
        
        logger.info(f"General Health Prediction: {result['risk_level']} (conf: {result['confidence']:.2%})")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"General health prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/general/batch', methods=['POST'])
def general_batch_predict():
    """
    Multiple general health patients prediction
    
    POST /general/batch
    Body: [
        {patient1_data},
        {patient2_data},
        ...
    ]
    """
    try:
        if general_agent is None:
            return jsonify({'error': 'General Health Agent not loaded'}), 503
        
        patients = request.get_json()
        
        if not isinstance(patients, list):
            return jsonify({'error': 'Body must be a JSON array'}), 400
        
        results = []
        for i, patient in enumerate(patients):
            try:
                result = general_agent.predict(patient)
                # Convert NumPy types to native Python types
                result = json.loads(json.dumps(result, cls=NumpyEncoder))
                result['patient_index'] = i
                result['timestamp'] = datetime.now().isoformat()
                result['model_type'] = 'multimodal_lightgbm'
                results.append(result)
            except Exception as e:
                results.append({
                    'patient_index': i,
                    'error': str(e),
                    'status': 'error'
                })
        
        logger.info(f"General health batch prediction: {len(results)} patients processed")
        
        return jsonify({
            'total': len(results),
            'predictions': results
        }), 200
        
    except Exception as e:
        logger.error(f"General health batch prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/general/model-info', methods=['GET'])
def general_model_info():
    """Get general health model metadata"""
    if general_agent is None:
        return jsonify({'error': 'General Health Agent not loaded'}), 503
    
    info = general_agent.get_model_info()
    return jsonify(info), 200

@app.route('/general/example-patient', methods=['GET'])
def general_example_patient():
    """Get example general health patient for testing"""
    example = {
        'age': 45,
        'systolic_bp': 140,
        'diastolic_bp': 90,
        'heart_rate': 95,
        'respiratory_rate': 18,
        'temperature': 37.5,
        'spo2': 96,
        'pain_score': 3,
        'wbc': 7.5,
        'hemoglobin': 13.5,
        'platelet_count': 250,
        'sodium': 138,
        'potassium': 4.0,
        'creatinine': 0.9,
        'glucose': 100,
        'troponin': 0.01,
        'bnp': 50,
        'lactate': 1.5,
        'inr': 1.0,
        'sex': 'M',
        'country': 'USA',
        'clinical_notes': 'Patient presents with chest pain and elevated blood pressure. No acute distress.'
    }
    return jsonify({
        'example': example,
        'description': 'Medium-risk patient with hypertension and chest pain'
    }), 200

# ==================== LEGACY ENDPOINTS (for backward compatibility) ====================

@app.route('/predict', methods=['POST'])
def legacy_predict():
    """Legacy endpoint - routes to respiratory model"""
    return respiratory_predict()

@app.route('/batch', methods=['POST'])
def legacy_batch():
    """Legacy endpoint - routes to respiratory model"""
    return respiratory_batch_predict()

@app.route('/model-info', methods=['GET'])
def legacy_model_info():
    """Legacy endpoint - routes to respiratory model"""
    return respiratory_model_info()

@app.route('/example-patients', methods=['GET'])
def legacy_example_patients():
    """Legacy endpoint - routes to respiratory model"""
    return respiratory_example_patients()

# ==================== RULE-BASED SAFETY & AGGREGATOR ====================

class RuleBasedSafetyLayer:
    @staticmethod
    def check_vitals(data: dict) -> dict:
        alerts = []
        is_critical = False
        
        spo2 = float(data.get('spo2', 100))
        if spo2 < 90:
            alerts.append(f"CRITICAL SpO2: {spo2}%")
            is_critical = True
            
        hr = float(data.get('heart_rate', 80))
        if hr > 130 or hr < 40:
            alerts.append(f"CRITICAL Heart Rate: {hr} bpm")
            is_critical = True
            
        sbp = float(data.get('systolic_bp', 120))
        if sbp < 90 or sbp > 200:
            alerts.append(f"CRITICAL Systolic BP: {sbp} mmHg")
            is_critical = True
            
        rr = float(data.get('respiratory_rate', 16))
        if rr > 30 or rr < 8:
            alerts.append(f"CRITICAL Respiratory Rate: {rr}")
            is_critical = True
            
        return {
            'is_critical': is_critical,
            'alerts': alerts
        }

class OutputAggregator:
    @staticmethod
    def aggregate(predictions: dict, safety_rules: dict) -> dict:
        risk_scores = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
        reverse_scores = {0: 'LOW', 1: 'MEDIUM', 2: 'HIGH'}
        
        max_risk_score = 0
        confidences = []
        
        # 1. Rule-based layer overrides
        if safety_rules.get('is_critical'):
            max_risk_score = 2
            
        # 2. Check each agent
        for agent_name, result in predictions.items():
            if result.get('status') == 'success':
                risk = result.get('risk_level', 'LOW')
                if 'HIGH' in risk: r = 'HIGH'
                elif 'MID' in risk or 'MEDIUM' in risk: r = 'MEDIUM'
                else: r = 'LOW'
                
                score = risk_scores.get(r, 0)
                if score > max_risk_score:
                    max_risk_score = score
                    
                confidences.append(result.get('confidence', 0.5))
                
        final_risk = reverse_scores[max_risk_score]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        uncertainty_high = avg_confidence < 0.70
        
        explanation = "Patient is stable across all systems."
        if final_risk == 'HIGH':
            explanation = "Critical risk identified! "
            if safety_rules.get('alerts'):
                explanation += "Safety alerts: " + ", ".join(safety_rules['alerts']) + ". "
            explanation += "Immediate intervention required."
        elif final_risk == 'MEDIUM':
            explanation = "Elevated risk detected. Please review agent sub-reports and monitor."
            
        if uncertainty_high:
            explanation += " (Note: AI confidence is low. Please review SHAP feature impacts carefully)."
            
        return {
            'final_risk': final_risk,
            'overall_confidence': round(avg_confidence, 4),
            'uncertainty_high': uncertainty_high,
            'explanation': explanation,
            'safety_alerts': safety_rules.get('alerts', [])
        }

# ==================== UNIFIED ENDPOINT ====================

@app.route('/unified/predict', methods=['POST'])
def unified_predict():
    """
    Unified endpoint predicting risk across all 4 models.
    Now enriched with hcai_lite (confidence category + symptom context)
    from the HCAI agent pipeline — no LLM call, stays fast.
    """
    try:
        patient_data = request.get_json()

        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'predictions': {}
        }

        if respiratory_agent:
            resp_res = respiratory_agent.predict(patient_data)
            results['predictions']['respiratory'] = json.loads(json.dumps(resp_res, cls=NumpyEncoder))

        if general_agent:
            gen_res = general_agent.predict(patient_data)
            results['predictions']['general'] = json.loads(json.dumps(gen_res, cls=NumpyEncoder))

        if cardiac_agent:
            card_res = cardiac_agent.predict(patient_data)
            results['predictions']['cardiac'] = json.loads(json.dumps(card_res, cls=NumpyEncoder))

        if sepsis_agent:
            sep_res = sepsis_agent.predict(patient_data)
            results['predictions']['sepsis'] = json.loads(json.dumps(sep_res, cls=NumpyEncoder))

        # Step 1: Rule-Based Safety Layer (unchanged)
        safety_rules = RuleBasedSafetyLayer.check_vitals(patient_data)

        # Step 2: Output Aggregation (unchanged)
        aggregation = OutputAggregator.aggregate(results['predictions'], safety_rules)
        results['aggregation'] = aggregation

        # Step 3: HCAI Lite enrichment (confidence + symptom context, no LLM)
        if _summary_agent:
            try:
                hcai_lite = _summary_agent.build_lite(
                    patient_data,
                    results['predictions'],
                    aggregation,
                )
                results['hcai_lite'] = json.loads(json.dumps(hcai_lite, cls=NumpyEncoder))
            except Exception as hcai_err:
                logger.warning(f"HCAI lite enrichment failed: {hcai_err}")
                results['hcai_lite'] = None
        else:
            results['hcai_lite'] = None

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Unified prediction error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/unified/batch', methods=['POST'])
def unified_batch_predict():
    """
    Batch unified prediction for sensitivity analysis (fast, no LLM)
    """
    try:
        patients = request.get_json()
        if not isinstance(patients, list):
            return jsonify({'error': 'Body must be a JSON array'}), 400
        
        results = []
        for patient_data in patients:
            res = {
                'predictions': {}
            }
            if respiratory_agent:
                resp_res = respiratory_agent.predict(patient_data)
                res['predictions']['respiratory'] = json.loads(json.dumps(resp_res, cls=NumpyEncoder))
            if general_agent:
                gen_res = general_agent.predict(patient_data)
                res['predictions']['general'] = json.loads(json.dumps(gen_res, cls=NumpyEncoder))
            if cardiac_agent:
                card_res = cardiac_agent.predict(patient_data)
                res['predictions']['cardiac'] = json.loads(json.dumps(card_res, cls=NumpyEncoder))
            if sepsis_agent:
                sep_res = sepsis_agent.predict(patient_data)
                res['predictions']['sepsis'] = json.loads(json.dumps(sep_res, cls=NumpyEncoder))
                
            safety_rules = RuleBasedSafetyLayer.check_vitals(patient_data)
            aggregation = OutputAggregator.aggregate(res['predictions'], safety_rules)
            res['aggregation'] = aggregation
            results.append(res)
            
        return jsonify({'status': 'success', 'results': results}), 200
    except Exception as e:
        logger.error(f"Unified batch prediction error: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== HCAI ENDPOINTS ====================

@app.route('/hcai/analyze', methods=['POST'])
def hcai_analyze():
    """
    Full HCAI analysis endpoint.

    Runs all 4 model predictions + full HCAI pipeline:
        ConfidenceAgent + SymptomAgent + LLMAgent (Groq) + ReportGenerator

    Returns the complete HCAI report as JSON and saves it to hcai_reports/.

    Optional request body fields:
        patient_id : str  — identifier for the report (default: ANONYMOUS)
        save_report: bool — whether to persist the report (default: true)
    """
    if not _summary_agent or not _report_generator:
        return jsonify({'error': 'HCAI agents not initialised. Check server logs.'}), 503

    try:
        body = request.get_json()
        patient_id = body.pop('patient_id', 'ANONYMOUS') if body else 'ANONYMOUS'
        patient_name = body.pop('patient_name', 'Anonymous') if body else 'Anonymous'
        save_report = body.pop('save_report', True) if body else True
        patient_data = body

        # ── Step 1: Run all 4 model predictions ──────────────────────────
        predictions: dict = {}

        if respiratory_agent:
            r = respiratory_agent.predict(patient_data)
            predictions['respiratory'] = json.loads(json.dumps(r, cls=NumpyEncoder))

        if general_agent:
            r = general_agent.predict(patient_data)
            predictions['general'] = json.loads(json.dumps(r, cls=NumpyEncoder))

        if cardiac_agent:
            r = cardiac_agent.predict(patient_data)
            predictions['cardiac'] = json.loads(json.dumps(r, cls=NumpyEncoder))

        if sepsis_agent:
            r = sepsis_agent.predict(patient_data)
            predictions['sepsis'] = json.loads(json.dumps(r, cls=NumpyEncoder))

        # ── Step 2: Safety layer + aggregation ───────────────────────────
        safety_rules = RuleBasedSafetyLayer.check_vitals(patient_data)
        aggregation = OutputAggregator.aggregate(predictions, safety_rules)

        # ── Step 3: Full HCAI pipeline (includes LLM) ────────────────────
        hcai_full = _summary_agent.build_full(patient_data, predictions, aggregation)
        hcai_full = json.loads(json.dumps(hcai_full, cls=NumpyEncoder))

        # ── Step 4: Generate structured report ───────────────────────────
        report = _report_generator.generate(
            patient_data=patient_data,
            hcai_full_context=hcai_full,
            aggregation=aggregation,
            patient_id=patient_id,
            save=save_report,
        )
        report['patient_name'] = patient_name  # Store name alongside the generated ID
        report = json.loads(json.dumps(report, cls=NumpyEncoder))

        logger.info(f"HCAI analysis complete: {report['report_id']} | Risk: {report['risk_prediction']}")

        # Auto-log to SQLite database
        try:
            save_assessment_to_db(patient_id, patient_name, patient_data, predictions, aggregation, report)
        except Exception as db_err:
            logger.error(f"Failed to auto-log assessment: {db_err}")

        return jsonify({
            'status': 'success',
            'report_id': report['report_id'],
            'timestamp': report['timestamp'],
            'predictions': predictions,
            'aggregation': aggregation,
            'hcai_full': hcai_full,
            'hcai_report': report,
        }), 200

    except Exception as e:
        logger.error(f"HCAI analyze error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/hcai/reports', methods=['GET'])
def hcai_reports_list():
    """
    List the most recent HCAI reports saved to hcai_reports/.

    Query parameters:
        limit : int — max number of reports to return (default: 20)
    """
    if not _report_generator:
        return jsonify({'error': 'ReportGenerator not initialised.'}), 503

    try:
        limit = int(request.args.get('limit', 20))
        reports = _report_generator.list_reports(limit=limit)
        return jsonify({'status': 'success', 'count': len(reports), 'reports': reports}), 200
    except Exception as e:
        logger.error(f"HCAI reports list error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/hcai/reports/<report_id>', methods=['GET'])
def hcai_report_detail(report_id: str):
    """Load a specific HCAI report by ID."""
    if not _report_generator:
        return jsonify({'error': 'ReportGenerator not initialised.'}), 503
    try:
        report = _report_generator.load_report(report_id)
        if report is None:
            return jsonify({'error': f'Report {report_id} not found.'}), 404
        return jsonify({'status': 'success', 'report': report}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== FEEDBACK / HITL ENDPOINT ====================

@app.route('/feedback', methods=['POST'])
def feedback():
    """
    Log clinician feedback for continuous learning.
    """
    try:
        data = request.get_json()
        file_exists = os.path.isfile('data/feedback_log.csv')
        
        with open('data/feedback_log.csv', 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'patient_age', 'patient_sex', 'ai_final_risk', 'clinician_override', 'action']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
                
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'patient_age': data.get('patient_data', {}).get('age', ''),
                'patient_sex': data.get('patient_data', {}).get('sex', ''),
                'ai_final_risk': data.get('ai_final_risk', ''),
                'clinician_override': data.get('clinician_override', ''),
                'action': data.get('action', '')  # 'accept' or 'override'
            })
            
        return jsonify({'status': 'success', 'message': 'Feedback logged successfully'}), 200
    except Exception as e:
        logger.error(f"Feedback logging error: {e}")
        return jsonify({'error': str(e)}), 400


# ==================== PATIENT REGISTRY DB SETUP & ENDPOINTS ====================

DATABASE_PATH = 'data/triage_registry.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            age_group TEXT,
            altered_mentation INTEGER,
            chest_pain INTEGER,
            diabetes INTEGER,
            spo2 INTEGER,
            respiratory_rate INTEGER,
            temperature REAL,
            heart_rate INTEGER,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            pain_score INTEGER,
            wbc REAL,
            hemoglobin REAL,
            platelet_count REAL,
            sodium REAL,
            potassium REAL,
            creatinine REAL,
            glucose REAL,
            troponin REAL,
            bnp REAL,
            lactate REAL,
            inr REAL,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            assessment_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            risk_prediction TEXT NOT NULL,
            confidence_pct TEXT,
            llm_summary TEXT,
            report_data TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("SQLite registry database initialized successfully.")

def save_assessment_to_db(patient_id, patient_name, patient_data, predictions, aggregation, report):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute('SELECT 1 FROM patients WHERE patient_id = ?', (patient_id,))
    exists = cursor.fetchone() is not None
    
    now = datetime.now().isoformat()
    age = int(patient_data.get('age', 35))
    
    if age < 18:
        age_group = 'pediatric'
    elif age < 65:
        age_group = 'adult'
    elif age < 80:
        age_group = 'senior'
    else:
        age_group = 'elderly'
        
    if exists:
        cursor.execute('''
            UPDATE patients SET
                patient_name = ?, age = ?, sex = ?, age_group = ?, altered_mentation = ?,
                chest_pain = ?, diabetes = ?, spo2 = ?, respiratory_rate = ?, temperature = ?,
                heart_rate = ?, systolic_bp = ?, diastolic_bp = ?, pain_score = ?,
                wbc = ?, hemoglobin = ?, platelet_count = ?, sodium = ?, potassium = ?,
                creatinine = ?, glucose = ?, troponin = ?, bnp = ?, lactate = ?, inr = ?,
                updated_at = ?
            WHERE patient_id = ?
        ''', (
            patient_name, age, patient_data.get('sex', 'M'), age_group,
            int(patient_data.get('altered_mentation', 0)), int(patient_data.get('chest_pain', 0)), int(patient_data.get('diabetes', 0)),
            int(patient_data.get('spo2', 97)), int(patient_data.get('respiratory_rate', 16)), float(patient_data.get('temperature', 36.8)),
            int(patient_data.get('heart_rate', 70)), int(patient_data.get('systolic_bp', 120)), int(patient_data.get('diastolic_bp', 80)), int(patient_data.get('pain_score', 2)),
            float(patient_data.get('wbc', 7.5)), float(patient_data.get('hemoglobin', 14.0)), float(patient_data.get('platelet_count', 250)),
            float(patient_data.get('sodium', 140)), float(patient_data.get('potassium', 4.0)), float(patient_data.get('creatinine', 0.9)),
            float(patient_data.get('glucose', 100)), float(patient_data.get('troponin', 0.01)), float(patient_data.get('bnp', 50)),
            float(patient_data.get('lactate', 1.2)), float(patient_data.get('inr', 1.0)),
            now, patient_id
        ))
    else:
        cursor.execute('''
            INSERT INTO patients (
                patient_id, patient_name, age, sex, age_group, altered_mentation,
                chest_pain, diabetes, spo2, respiratory_rate, temperature,
                heart_rate, systolic_bp, diastolic_bp, pain_score,
                wbc, hemoglobin, platelet_count, sodium, potassium,
                creatinine, glucose, troponin, bnp, lactate, inr,
                created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?
            )
        ''', (
            patient_id, patient_name, age, patient_data.get('sex', 'M'), age_group,
            int(patient_data.get('altered_mentation', 0)), int(patient_data.get('chest_pain', 0)), int(patient_data.get('diabetes', 0)),
            int(patient_data.get('spo2', 97)), int(patient_data.get('respiratory_rate', 16)), float(patient_data.get('temperature', 36.8)),
            int(patient_data.get('heart_rate', 70)), int(patient_data.get('systolic_bp', 120)), int(patient_data.get('diastolic_bp', 80)), int(patient_data.get('pain_score', 2)),
            float(patient_data.get('wbc', 7.5)), float(patient_data.get('hemoglobin', 14.0)), float(patient_data.get('platelet_count', 250)),
            float(patient_data.get('sodium', 140)), float(patient_data.get('potassium', 4.0)), float(patient_data.get('creatinine', 0.9)),
            float(patient_data.get('glucose', 100)), float(patient_data.get('troponin', 0.01)), float(patient_data.get('bnp', 50)),
            float(patient_data.get('lactate', 1.2)), float(patient_data.get('inr', 1.0)),
            now, now
        ))
        
    cursor.execute('''
        INSERT OR REPLACE INTO assessments (
            assessment_id, patient_id, timestamp, risk_prediction, confidence_pct, llm_summary, report_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        report.get('report_id'),
        patient_id,
        report.get('timestamp', now),
        report.get('risk_prediction', 'LOW'),
        str(report.get('confidence_pct', 'N/A')),
        report.get('llm_interpretation', 'N/A'),
        json.dumps({
            'predictions': predictions,
            'aggregation': aggregation,
            'report': report
        })
    ))
    
    conn.commit()
    conn.close()
    logger.info(f"Successfully saved assessment {report.get('report_id')} to DB for patient {patient_id}.")

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """List all patients with latest risk assessment."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, a.risk_prediction, a.timestamp as last_assessment_time
            FROM patients p
            LEFT JOIN assessments a ON a.timestamp = (
                SELECT MAX(timestamp) FROM assessments WHERE patient_id = p.patient_id
            )
            ORDER BY p.updated_at DESC
        ''')
        rows = cursor.fetchall()
        patients = [dict(row) for row in rows]
        conn.close()
        return jsonify({'status': 'success', 'patients': patients}), 200
    except Exception as e:
        logger.error(f"Error listing patients: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient telemetry details and assessment history."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
        patient_row = cursor.fetchone()
        if not patient_row:
            conn.close()
            return jsonify({'error': f'Patient {patient_id} not found.'}), 404
            
        patient = dict(patient_row)
        
        cursor.execute('''
            SELECT assessment_id, timestamp, risk_prediction, confidence_pct, llm_summary, report_data
            FROM assessments 
            WHERE patient_id = ? 
            ORDER BY timestamp DESC
        ''', (patient_id,))
        rows = cursor.fetchall()
        
        assessments = []
        for r in rows:
            assess_dict = dict(r)
            try:
                assess_dict['report_data'] = json.loads(assess_dict['report_data'])
            except Exception:
                pass
            assessments.append(assess_dict)
            
        patient['assessments'] = assessments
        conn.close()
        return jsonify({'status': 'success', 'patient': patient}), 200
    except Exception as e:
        logger.error(f"Error getting patient detail: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def save_patient():
    """Upsert a patient profile parameters to the database without forcing assessment."""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        patient_name = data.get('patient_name', 'Anonymous')
        
        if not patient_id:
            patient_id = 'PT-' + uuid.uuid4().hex[:8].upper()
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM patients WHERE patient_id = ?', (patient_id,))
        exists = cursor.fetchone() is not None
        
        now = datetime.now().isoformat()
        age = int(data.get('age', 35))
        
        if age < 18:
            age_group = 'pediatric'
        elif age < 65:
            age_group = 'adult'
        elif age < 80:
            age_group = 'senior'
        else:
            age_group = 'elderly'
            
        if exists:
            cursor.execute('''
                UPDATE patients SET
                    patient_name = ?, age = ?, sex = ?, age_group = ?, altered_mentation = ?,
                    chest_pain = ?, diabetes = ?, spo2 = ?, respiratory_rate = ?, temperature = ?,
                    heart_rate = ?, systolic_bp = ?, diastolic_bp = ?, pain_score = ?,
                    wbc = ?, hemoglobin = ?, platelet_count = ?, sodium = ?, potassium = ?,
                    creatinine = ?, glucose = ?, troponin = ?, bnp = ?, lactate = ?, inr = ?,
                    updated_at = ?
                WHERE patient_id = ?
            ''', (
                patient_name, age, data.get('sex', 'M'), age_group,
                int(data.get('altered_mentation', 0)), int(data.get('chest_pain', 0)), int(data.get('diabetes', 0)),
                int(data.get('spo2', 97)), int(data.get('respiratory_rate', 16)), float(data.get('temperature', 36.8)),
                int(data.get('heart_rate', 70)), int(data.get('systolic_bp', 120)), int(data.get('diastolic_bp', 80)), int(data.get('pain_score', 2)),
                float(data.get('wbc', 7.5)), float(data.get('hemoglobin', 14.0)), float(data.get('platelet_count', 250)),
                float(data.get('sodium', 140)), float(data.get('potassium', 4.0)), float(data.get('creatinine', 0.9)),
                float(data.get('glucose', 100)), float(data.get('troponin', 0.01)), float(data.get('bnp', 50)),
                float(data.get('lactate', 1.2)), float(data.get('inr', 1.0)),
                now, patient_id
            ))
        else:
            cursor.execute('''
                INSERT INTO patients (
                    patient_id, patient_name, age, sex, age_group, altered_mentation,
                    chest_pain, diabetes, spo2, respiratory_rate, temperature,
                    heart_rate, systolic_bp, diastolic_bp, pain_score,
                    wbc, hemoglobin, platelet_count, sodium, potassium,
                    creatinine, glucose, troponin, bnp, lactate, inr,
                    created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?
                )
            ''', (
                patient_id, patient_name, age, data.get('sex', 'M'), age_group,
                int(data.get('altered_mentation', 0)), int(data.get('chest_pain', 0)), int(data.get('diabetes', 0)),
                int(data.get('spo2', 97)), int(data.get('respiratory_rate', 16)), float(data.get('temperature', 36.8)),
                int(data.get('heart_rate', 70)), int(data.get('systolic_bp', 120)), int(data.get('diastolic_bp', 80)), int(data.get('pain_score', 2)),
                float(data.get('wbc', 7.5)), float(data.get('hemoglobin', 14.0)), float(data.get('platelet_count', 250)),
                float(data.get('sodium', 140)), float(data.get('potassium', 4.0)), float(data.get('creatinine', 0.9)),
                float(data.get('glucose', 100)), float(data.get('troponin', 0.01)), float(data.get('bnp', 50)),
                float(data.get('lactate', 1.2)), float(data.get('inr', 1.0)),
                now, now
            ))
            
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'patient_id': patient_id, 'message': 'Patient record saved successfully.'}), 200
    except Exception as e:
        logger.error(f"Error saving patient: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete patient and their assessment history from the registry."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
        cursor.execute('DELETE FROM assessments WHERE patient_id = ?', (patient_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': f'Patient {patient_id} and associated history deleted.'}), 200
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Initialize the local SQLite database on startup
    init_db()
    
    print("\n" + "="*70)
    print("🩺 OmniHealth Diagnostics — HCAI Multi-Agent API Server")
    print("="*70)

    print("\n🔵 UNIFIED ENDPOINT (React Dashboard):")
    print("  POST http://localhost:8000/unified/predict   ← enriched with hcai_lite")

    print("\n🧠 HCAI ENDPOINTS (Full Clinical Decision Support):")
    print("  POST http://localhost:8000/hcai/analyze      ← full pipeline + LLM + report")
    print("  GET  http://localhost:8000/hcai/reports      ← list saved reports")
    print("  GET  http://localhost:8000/hcai/reports/<id> ← load specific report")

    print("\n📊 INDIVIDUAL AGENT ENDPOINTS:")
    print("  POST http://localhost:8000/respiratory/predict")
    print("  POST http://localhost:8000/general/predict")
    print("  POST http://localhost:8000/cardiac/predict")
    print("  POST http://localhost:8000/sepsis/predict")

    print("\n✅ HEALTH CHECK:")
    print("  GET  http://localhost:8000/health")

    print("\n" + "="*70)
    print(f"  HCAI Pipeline: {'✓ Active' if _summary_agent else '✗ Not loaded'}")
    print(f"  Groq LLM:      {'✓ Active' if _summary_agent and _summary_agent.llm_agent._client else '⚠ Fallback (rule-based)'}")
    print("="*70)
    print("  Starting server on http://localhost:8000 ...")
    print("="*70 + "\n")

    app.run(debug=False, host='0.0.0.0', port=8000)
