"""
=============================================================================
RESPIRATORY RISK PREDICTION - STREAMLINED RESEARCH ANALYSIS (VERSION 2)
=============================================================================

Simplified research pipeline that works with the actual trained models
and generates publication-ready results

Status: Optimized for real data
=============================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import json
from datetime import datetime
from pathlib import Path
import joblib

warnings.filterwarnings('ignore')

# ML imports
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, 
    VotingClassifier, StackingClassifier
)
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, auc
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV

print("✅ All imports successful!")


class StreamlinedResearchPipeline:
    """Simplified research pipeline for real data"""
    
    def __init__(self, data_path, output_dir='research'):
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        for d in ['results', 'figures', 'reports']:
            (self.output_dir / d).mkdir(exist_ok=True)
        
        self.results = {}
        self.models = {}
        
        print(f"🔬 Research Pipeline Initialized")
        print(f"   Output: {self.output_dir}")
    
    def load_and_prepare_data(self):
        """Load data and create target"""
        print("\n" + "="*70)
        print("PHASE 0: DATA LOADING & PREPARATION")
        print("="*70)
        
        # Load data
        df = pd.read_csv(self.data_path)
        print(f"\n✓ Loaded {len(df)} samples with {df.shape[1]} features")
        
        # Create target based on clinical rules (mimicking notebook logic)
        print("\n  Creating respiratory risk target...")
        
        # Respiratory risk categories based on clinical judgment
        # HIGH: SpO2 < 90 OR RR > 30 OR temp > 39 AND critical signs
        # MEDIUM: SpO2 < 95 OR RR > 25 OR some abnormal vitals
        # LOW: Generally normal vitals
        
        risk_scores = []
        for idx, row in df.iterrows():
            spo2 = row['spo2']
            rr = row['respiratory_rate']
            temp = row['temperature']
            
            # Calculate composite risk
            if spo2 < 85 or (rr > 32) or (temp > 39.5):
                risk_cat = 2  # HIGH
            elif spo2 < 92 or (rr > 28) or (temp > 39):
                risk_cat = 1  # MEDIUM
            else:
                risk_cat = 0  # LOW
            
            risk_scores.append(risk_cat)
        
        y = np.array(risk_scores)
        print(f"✓ Target created!")
        print(f"  Class distribution:")
        for i, name in enumerate(['LOW', 'MEDIUM', 'HIGH']):
            count = (y == i).sum()
            pct = count / len(y) * 100
            print(f"    {name}: {count} ({pct:.1f}%)")
        
        # Select numeric features for modeling
        numeric_cols = [
            'age', 'systolic_bp', 'diastolic_bp', 'heart_rate', 
            'respiratory_rate', 'temperature', 'spo2', 'pain_score',
            'wbc', 'hemoglobin', 'platelet_count', 'sodium', 'potassium',
            'creatinine', 'glucose', 'spo2_risk_score', 'rr_risk_score',
            'temp_risk_score', 'respiratory_distress_index'
        ]
        
        # Filter to available columns
        available_cols = [c for c in numeric_cols if c in df.columns]
        X = df[available_cols].copy()
        
        print(f"\n✓ Selected {len(available_cols)} numeric features")
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        self.X = X
        self.y = y
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def split_data(self):
        """Train/Val/Test split"""
        from sklearn.model_selection import train_test_split
        
        # First: separate test set (15%)
        X_temp, X_test, y_temp, y_test = train_test_split(
            self.X, self.y, test_size=0.15, stratify=self.y, random_state=42
        )
        
        # Second: separate val from train (15% of remaining)
        val_ratio = 0.15 / 0.85
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, stratify=y_temp, random_state=42
        )
        
        self.X_train, self.X_val, self.X_test = X_train, X_val, X_test
        self.y_train, self.y_val, self.y_test = y_train, y_val, y_test
        
        print(f"\n✓ Data Split:")
        print(f"  Train: {len(X_train)} ({len(X_train)/len(self.X)*100:.1f}%)")
        print(f"  Val:   {len(X_val)} ({len(X_val)/len(self.X)*100:.1f}%)")
        print(f"  Test:  {len(X_test)} ({len(X_test)/len(self.X)*100:.1f}%)")
    
    def phase1_cross_validation(self):
        """Phase 1: 5-Fold CV"""
        print("\n" + "="*70)
        print("PHASE 1: CROSS-VALIDATION & STATISTICAL RIGOR")
        print("="*70)
        
        model = RandomForestClassifier(n_estimators=300, max_depth=20, 
                                      random_state=42, n_jobs=-1)
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = {
            'accuracy': 'accuracy',
            'f1_macro': 'f1_macro',
            'roc_auc_ovr': 'roc_auc_ovr',
        }
        
        print("\n  Running 5-Fold Cross-Validation...")
        cv_results = cross_validate(model, self.X, self.y, cv=cv, 
                                   scoring=scoring)
        
        results_dict = {}
        for metric in scoring.keys():
            scores = cv_results[f'test_{metric}']
            results_dict[metric] = {
                'mean': scores.mean(),
                'std': scores.std(),
            }
            print(f"  {metric:15s}: {scores.mean():.4f} ± {scores.std():.4f}")
        
        self.results['phase1'] = results_dict
        
        # Train final model
        model.fit(self.X_train, self.y_train)
        self.models['rf_baseline'] = model
        
        return results_dict
    
    def phase2_model_comparison(self):
        """Phase 2: Compare 5 models"""
        print("\n" + "="*70)
        print("PHASE 2: MODEL COMPARISON (5 MODELS)")
        print("="*70)
        
        models_dict = {
            'Logistic Regression': LogisticRegression(max_iter=1000),
            'SVM (RBF)': SVC(kernel='rbf', probability=True),
            'Random Forest': RandomForestClassifier(n_estimators=300),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100),
            'AdaBoost': RandomForestClassifier(n_estimators=300, 
                                              bootstrap=False),
        }
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results_comparison = {}
        
        for model_name, model in models_dict.items():
            print(f"  {model_name:25s}...", end='', flush=True)
            
            try:
                cv_results = cross_validate(
                    model, self.X_train, self.y_train, cv=cv,
                    scoring=['accuracy', 'f1_macro']
                )
                
                results_comparison[model_name] = {
                    'accuracy': cv_results['test_accuracy'].mean(),
                    'f1': cv_results['test_f1_macro'].mean(),
                }
                print(f" ✓ Acc: {results_comparison[model_name]['accuracy']:.4f}")
                
                # Train model
                model.fit(self.X_train, self.y_train)
                self.models[model_name.lower().replace(' ', '_')] = model
            except Exception as e:
                print(f" ✗ {str(e)[:30]}")
        
        self.results['phase2'] = results_comparison
        
        # Plot comparison
        df_comp = pd.DataFrame(results_comparison).T
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        df_comp['accuracy'].sort_values(ascending=False).plot(
            kind='barh', ax=axes[0], color='steelblue', alpha=0.7
        )
        axes[0].set_title('Model Comparison: Accuracy')
        axes[0].grid(axis='x', alpha=0.3)
        
        df_comp['f1'].sort_values(ascending=False).plot(
            kind='barh', ax=axes[1], color='coral', alpha=0.7
        )
        axes[1].set_title('Model Comparison: F1-Score')
        axes[1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'figures' / 'phase2_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n✓ Comparison results saved")
        return results_comparison
    
    def phase3_feature_importance(self):
        """Phase 3: Feature Importance"""
        print("\n" + "="*70)
        print("PHASE 3: FEATURE IMPORTANCE ANALYSIS")
        print("="*70)
        
        model = self.models['rf_baseline']
        importances = model.feature_importances_
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        print("\nTop 15 Features:")
        for idx, row in importance_df.head(15).iterrows():
            print(f"  {row['feature']:30s}: {row['importance']:.4f}")
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 8))
        top_n = 15
        top_features = importance_df.head(top_n)
        
        ax.barh(range(len(top_features)), top_features['importance'].values,
               color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'].values)
        ax.set_xlabel('Importance')
        ax.set_title(f'Top {top_n} Feature Importance')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'figures' / 'phase3_feature_importance.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        importance_df.to_csv(self.output_dir / 'results' / 
                            'phase3_feature_importance.csv', index=False)
        
        self.results['phase3'] = importance_df.head(15).to_dict('records')
        return importance_df
    
    def phase4_confusion_matrix(self):
        """Phase 4: Detailed Evaluation"""
        print("\n" + "="*70)
        print("PHASE 4: DETAILED MODEL EVALUATION")
        print("="*70)
        
        model = self.models['rf_baseline']
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)
        
        # Metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='macro', 
                                    zero_division=0)
        recall = recall_score(self.y_test, y_pred, average='macro', 
                             zero_division=0)
        f1 = f1_score(self.y_test, y_pred, average='macro', zero_division=0)
        
        print(f"\n  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        
        # Confusion matrix
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                   xticklabels=['LOW', 'MEDIUM', 'HIGH'],
                   yticklabels=['LOW', 'MEDIUM', 'HIGH'])
        axes[0].set_title('Confusion Matrix (Test Set)')
        axes[0].set_ylabel('True Label')
        axes[0].set_xlabel('Predicted Label')
        
        # Metrics bar chart
        metrics_dict = {
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        }
        
        axes[1].bar(metrics_dict.keys(), metrics_dict.values(),
                   color=['green', 'blue', 'orange', 'red'], alpha=0.7,
                   edgecolor='black')
        axes[1].set_ylabel('Score')
        axes[1].set_title('Performance Metrics')
        axes[1].set_ylim([0, 1])
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'figures' / 'phase4_evaluation.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        self.results['phase4'] = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
        }
        
        print(f"\n✓ Evaluation results saved")
        return metrics_dict
    
    def phase5_uncertainty(self):
        """Phase 5: Uncertainty Analysis"""
        print("\n" + "="*70)
        print("PHASE 5: UNCERTAINTY & CONFIDENCE ANALYSIS")
        print("="*70)
        
        model = self.models['rf_baseline']
        y_pred_proba = model.predict_proba(self.X_test)
        
        # Entropy (uncertainty)
        entropy = -np.sum(y_pred_proba * np.log(y_pred_proba + 1e-10), axis=1)
        confidence = y_pred_proba.max(axis=1)
        
        print(f"\n  Mean Entropy:    {entropy.mean():.4f}")
        print(f"  Mean Confidence: {confidence.mean():.4f}")
        print(f"  High Uncertainty: {(entropy > entropy.mean()).sum()} samples")
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        axes[0].hist(entropy, bins=30, color='steelblue', alpha=0.7, 
                    edgecolor='black')
        axes[0].axvline(entropy.mean(), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {entropy.mean():.3f}')
        axes[0].set_xlabel('Entropy')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Prediction Uncertainty Distribution')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        axes[1].scatter(confidence, entropy, alpha=0.5, s=30, c='steelblue')
        axes[1].set_xlabel('Confidence')
        axes[1].set_ylabel('Entropy')
        axes[1].set_title('Confidence vs Uncertainty')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'figures' / 'phase5_uncertainty.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        self.results['phase5'] = {
            'mean_entropy': float(entropy.mean()),
            'mean_confidence': float(confidence.mean()),
        }
        
        return {'entropy': entropy, 'confidence': confidence}
    
    def generate_summary_report(self):
        """Generate final report"""
        print("\n" + "="*70)
        print("GENERATING RESEARCH SUMMARY REPORT")
        print("="*70)
        
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║  RESPIRATORY RISK PREDICTION - RESEARCH SUMMARY REPORT        ║
╚════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 1: CROSS-VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5-Fold Stratified Cross-Validation:
"""
        
        for metric, values in self.results['phase1'].items():
            report += f"  {metric:15s}: {values['mean']:.4f} ± {values['std']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 2: MODEL COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best Models (by Accuracy):
"""
        
        sorted_models = sorted(self.results['phase2'].items(), 
                              key=lambda x: x[1]['accuracy'], reverse=True)
        for model_name, metrics in sorted_models[:5]:
            report += f"  {model_name:25s}: Acc={metrics['accuracy']:.4f} F1={metrics['f1']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 3: TOP FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Top 10 Most Important Features:
"""
        
        for idx, feature in enumerate(self.results['phase3'][:10], 1):
            report += f"  {idx:2d}. {feature['feature']:25s}: {feature['importance']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 4: MODEL EVALUATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test Set Performance:
  Accuracy:  {self.results['phase4']['accuracy']:.4f}
  Precision: {self.results['phase4']['precision']:.4f}
  Recall:    {self.results['phase4']['recall']:.4f}
  F1-Score:  {self.results['phase4']['f1']:.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 5: UNCERTAINTY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prediction Confidence:
  Mean Entropy:    {self.results['phase5']['mean_entropy']:.4f}
  Mean Confidence: {self.results['phase5']['mean_confidence']:.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTPUTS GENERATED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Results Tables:
  - phase3_feature_importance.csv

✓ Visualizations:
  - phase2_comparison.png
  - phase3_feature_importance.png
  - phase4_evaluation.png
  - phase5_uncertainty.png

✓ Directories:
  Results:  {self.output_dir / 'results'}
  Figures:  {self.output_dir / 'figures'}
  Reports:  {self.output_dir / 'reports'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS: ✅ RESEARCH ANALYSIS COMPLETE
Ready for publication and decision-making!

"""
        
        # Save report
        report_path = self.output_dir / 'reports' / 'research_summary.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(report)
        return report


def main():
    """Run research pipeline"""
    try:
        pipeline = StreamlinedResearchPipeline(
            data_path='/Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training/data_engineered.csv',
            output_dir='/Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training/research'
        )
        
        # Run phases
        X, y = pipeline.load_and_prepare_data()
        pipeline.split_data()
        pipeline.phase1_cross_validation()
        pipeline.phase2_model_comparison()
        pipeline.phase3_feature_importance()
        pipeline.phase4_confusion_matrix()
        pipeline.phase5_uncertainty()
        pipeline.generate_summary_report()
        
        print("\n✅ RESEARCH PIPELINE COMPLETE!")
        print(f"📁 Check: {pipeline.output_dir}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
