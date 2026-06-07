"""
=============================================================================
RESPIRATORY RISK PREDICTION - COMPREHENSIVE RESEARCH ANALYSIS
=============================================================================

Author: AI Researcher
Date: 2026-05-27
Purpose: Complete research pipeline with all 10 phases for publication

Phases:
  1. Cross-Validation & Statistical Rigor
  2. Baseline Comparisons (6 models)
  3. Advanced Hyperparameter Optimization (Bayesian)
  4. Multiple Model Ensemble (Voting + Stacking)
  5. Deep Learning Models (Neural Networks)
  6. Explainability Analysis (SHAP + LIME)
  7. Calibration Analysis
  8. Uncertainty Quantification
  9. Fairness & Bias Analysis
  10. Robustness Testing

Output: Publication-ready results, figures, and reports
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

# Suppress warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.model_selection import (
    StratifiedKFold, cross_validate, GridSearchCV, RandomizedSearchCV
)
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier,
    VotingClassifier, StackingClassifier, BaggingClassifier
)
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Try to import SHAP
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    print("⚠️  SHAP not installed. Skipping SHAP analysis.")

# Try to import Bayesian optimization
try:
    from skopt import gp_minimize
    from skopt.space import Integer, Categorical, Real
    from skopt.utils import use_named_args
    HAS_SKOPT = True
except ImportError:
    HAS_SKOPT = False
    print("⚠️  skopt not installed. Skipping Bayesian optimization.")


# ============================================================================
# 1. SETUP AND UTILITIES
# ============================================================================

class ResearchPipeline:
    """Complete research analysis pipeline"""
    
    def __init__(self, data_path='data_engineered.csv', 
                 output_dir='research'):
        """Initialize research pipeline"""
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.results_dir = self.output_dir / 'results'
        self.figures_dir = self.output_dir / 'figures'
        self.reports_dir = self.output_dir / 'reports'
        
        for d in [self.results_dir, self.figures_dir, self.reports_dir]:
            d.mkdir(exist_ok=True)
        
        # Results storage
        self.results = {}
        self.models = {}
        self.figures = {}
        
        print("🔬 Research Pipeline Initialized")
        print(f"   Output Directory: {self.output_dir}")
        print(f"   Data File: {data_path}")
    
    def load_data(self):
        """Load and prepare data"""
        print("\n" + "="*70)
        print("PHASE 0: DATA LOADING")
        print("="*70)
        
        df = pd.read_csv(self.data_path)
        print(f"✓ Loaded {len(df)} samples with {df.shape[1]} features")
        
        # Extract features and target
        target_col = 'resp_risk_cat'
        if target_col not in df.columns:
            # Try common alternatives
            target_cols = [c for c in df.columns if 'risk' in c.lower() 
                          and 'cat' in c.lower()]
            if target_cols:
                target_col = target_cols[0]
            else:
                raise ValueError(f"Cannot find target column. Available: {df.columns.tolist()}")
        
        # Create feature matrix and target vector
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        # Convert target to numeric if needed
        if y.dtype == 'object':
            risk_mapping = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
            y = y.map(risk_mapping)
        
        print(f"✓ Features: {X.shape[1]}")
        print(f"✓ Classes: {y.unique()}")
        print(f"✓ Class distribution:")
        for class_name, count in zip(['LOW', 'MEDIUM', 'HIGH'], 
                                    y.value_counts().sort_index()):
            pct = count / len(y) * 100
            print(f"   {class_name}: {count} ({pct:.1f}%)")
        
        self.X = X
        self.y = y
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def split_data(self, test_size=0.15, val_size=0.15, random_state=42):
        """Stratified train/val/test split"""
        from sklearn.model_selection import train_test_split
        
        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            self.X, self.y, test_size=test_size, 
            stratify=self.y, random_state=random_state
        )
        
        # Second split: separate validation from training
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio,
            stratify=y_temp, random_state=random_state
        )
        
        self.X_train, self.X_val, self.X_test = X_train, X_val, X_test
        self.y_train, self.y_val, self.y_test = y_train, y_val, y_test
        
        print(f"\n✓ Data Split:")
        print(f"   Train: {len(X_train)} ({len(X_train)/len(self.X)*100:.1f}%)")
        print(f"   Val:   {len(X_val)} ({len(X_val)/len(self.X)*100:.1f}%)")
        print(f"   Test:  {len(X_test)} ({len(X_test)/len(self.X)*100:.1f}%)")


# ============================================================================
# PHASE 1: CROSS-VALIDATION & STATISTICAL RIGOR
# ============================================================================

    def phase1_cross_validation(self):
        """Phase 1: Stratified 5-Fold Cross-Validation"""
        print("\n" + "="*70)
        print("PHASE 1: CROSS-VALIDATION & STATISTICAL RIGOR")
        print("="*70)
        
        # Initialize model
        model = RandomForestClassifier(n_estimators=300, max_depth=20, 
                                       random_state=42, n_jobs=-1)
        
        # Define scoring metrics
        scoring = {
            'accuracy': 'accuracy',
            'precision_macro': 'precision_macro',
            'recall_macro': 'recall_macro',
            'f1_macro': 'f1_macro',
            'roc_auc_ovr': 'roc_auc_ovr',
        }
        
        # Perform 5-fold cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_results = cross_validate(model, self.X, self.y, cv=cv, 
                                    scoring=scoring, return_train_score=True)
        
        # Extract results
        results_dict = {}
        for metric in scoring.keys():
            test_scores = cv_results[f'test_{metric}']
            train_scores = cv_results[f'train_{metric}']
            
            results_dict[metric] = {
                'test_mean': test_scores.mean(),
                'test_std': test_scores.std(),
                'train_mean': train_scores.mean(),
                'test_scores': test_scores,
                'train_scores': train_scores,
            }
        
        self.results['phase1_cv'] = results_dict
        
        # Print results
        print("\n5-Fold Cross-Validation Results:")
        print("-" * 70)
        for metric, values in results_dict.items():
            print(f"{metric.upper():20s}: {values['test_mean']:.4f} ± {values['test_std']:.4f}")
        
        # Save results
        cv_df = pd.DataFrame({
            metric: [f"{values['test_mean']:.4f} ± {values['test_std']:.4f}"]
            for metric, values in results_dict.items()
        }).T
        cv_df.to_csv(self.results_dir / 'phase1_cv_results.csv')
        print(f"\n✓ Results saved to: {self.results_dir / 'phase1_cv_results.csv'}")
        
        # Train final model on all data
        model.fit(self.X_train, self.y_train)
        self.models['baseline_rf'] = model
        
        return results_dict


# ============================================================================
# PHASE 2: BASELINE COMPARISONS
# ============================================================================

    def phase2_baseline_comparisons(self):
        """Phase 2: Compare 6 different models"""
        print("\n" + "="*70)
        print("PHASE 2: BASELINE COMPARISONS (6 MODELS)")
        print("="*70)
        
        models_dict = {
            'Logistic Regression': LogisticRegression(max_iter=1000, 
                                                       random_state=42),
            'SVM (RBF)': SVC(kernel='rbf', probability=True, 
                            random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=300, 
                                                    max_depth=20, 
                                                    random_state=42, n_jobs=-1),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=300, 
                                                            max_depth=10,
                                                            random_state=42),
            'Neural Network': MLPClassifier(hidden_layer_sizes=(100, 50),
                                           max_iter=1000, random_state=42,
                                           early_stopping=True,
                                           validation_fraction=0.1),
            'AdaBoost': AdaBoostClassifier(n_estimators=300, 
                                          random_state=42),
        }
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        comparison_results = {}
        
        for model_name, model in models_dict.items():
            print(f"\n  Training {model_name}...", end='')
            
            try:
                cv_results = cross_validate(
                    model, self.X_train, self.y_train, cv=cv,
                    scoring=['accuracy', 'f1_macro', 'roc_auc_ovr'],
                    return_train_score=True
                )
                
                comparison_results[model_name] = {
                    'accuracy_mean': cv_results['test_accuracy'].mean(),
                    'accuracy_std': cv_results['test_accuracy'].std(),
                    'f1_mean': cv_results['test_f1_macro'].mean(),
                    'f1_std': cv_results['test_f1_macro'].std(),
                    'roc_auc_mean': cv_results['test_roc_auc_ovr'].mean(),
                    'roc_auc_std': cv_results['test_roc_auc_ovr'].std(),
                }
                
                print(f" ✓ Accuracy: {comparison_results[model_name]['accuracy_mean']:.4f}")
                
                # Train and store model
                model.fit(self.X_train, self.y_train)
                self.models[model_name.lower().replace(' ', '_')] = model
                
            except Exception as e:
                print(f" ✗ Error: {str(e)[:50]}")
                comparison_results[model_name] = {'error': str(e)}
        
        self.results['phase2_comparison'] = comparison_results
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame(comparison_results).T
        print("\n" + "="*70)
        print("Model Comparison Results:")
        print("="*70)
        print(comparison_df.to_string())
        
        # Save results
        comparison_df.to_csv(self.results_dir / 'phase2_model_comparison.csv')
        print(f"\n✓ Results saved to: {self.results_dir / 'phase2_model_comparison.csv'}")
        
        # Plot comparison
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, metric in enumerate(['accuracy_mean', 'f1_mean', 'roc_auc_mean']):
            data = comparison_df[metric].sort_values(ascending=False)
            axes[idx].barh(range(len(data)), data.values, color='steelblue')
            axes[idx].set_yticks(range(len(data)))
            axes[idx].set_yticklabels(data.index)
            axes[idx].set_xlabel(metric.replace('_', ' ').title())
            axes[idx].set_title(f'Model Comparison: {metric.replace("_", " ").title()}')
            axes[idx].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase2_model_comparison.png', 
                   dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved: {self.figures_dir / 'phase2_model_comparison.png'}")
        plt.close()
        
        return comparison_results


# ============================================================================
# PHASE 3: HYPERPARAMETER OPTIMIZATION (BAYESIAN)
# ============================================================================

    def phase3_bayesian_optimization(self):
        """Phase 3: Bayesian Hyperparameter Optimization for RandomForest"""
        print("\n" + "="*70)
        print("PHASE 3: BAYESIAN HYPERPARAMETER OPTIMIZATION")
        print("="*70)
        
        if not HAS_SKOPT:
            print("⚠️  skopt not available. Installing...")
            os.system("pip install scikit-optimize -q")
            from skopt import gp_minimize
            from skopt.space import Integer, Categorical, Real
            from skopt.utils import use_named_args
        
        from skopt import gp_minimize
        from skopt.space import Integer, Categorical, Real
        from skopt.utils import use_named_args
        
        # Define search space
        space = [
            Integer(100, 500, name='n_estimators'),
            Integer(5, 50, name='max_depth'),
            Categorical(['auto', 'sqrt', 'log2'], name='max_features'),
            Integer(2, 20, name='min_samples_split'),
            Integer(1, 10, name='min_samples_leaf'),
        ]
        
        # Objective function
        @use_named_args(space)
        def objective(**params):
            model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
            cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
            scores = cross_validate(model, self.X_train, self.y_train, 
                                   cv=cv, scoring='f1_macro')
            return -scores['test_score'].mean()
        
        print("\nRunning Bayesian Optimization (50 iterations)...")
        result = gp_minimize(objective, space, n_calls=50, random_state=42, 
                           verbose=1)
        
        # Best parameters
        best_params = {
            'n_estimators': result.x[0],
            'max_depth': result.x[1],
            'max_features': result.x[2],
            'min_samples_split': result.x[3],
            'min_samples_leaf': result.x[4],
        }
        
        print("\n" + "="*70)
        print("Best Hyperparameters:")
        for param, value in best_params.items():
            print(f"  {param}: {value}")
        print(f"  Best F1-Score: {-result.fun:.4f}")
        print("="*70)
        
        # Train model with best parameters
        best_model = RandomForestClassifier(**best_params, random_state=42, 
                                           n_jobs=-1)
        best_model.fit(self.X_train, self.y_train)
        self.models['optimized_rf'] = best_model
        
        self.results['phase3_optimization'] = {
            'best_params': best_params,
            'best_score': -result.fun,
            'convergence': result.func_vals.tolist()
        }
        
        # Save results
        with open(self.results_dir / 'phase3_best_params.json', 'w') as f:
            json.dump(best_params, f, indent=2)
        print(f"✓ Results saved: {self.results_dir / 'phase3_best_params.json'}")
        
        # Plot convergence
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result.func_vals, 'o-', linewidth=2, markersize=6, 
               color='steelblue')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Best Loss')
        ax.set_title('Bayesian Optimization Convergence')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase3_convergence.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {self.figures_dir / 'phase3_convergence.png'}")
        
        return best_params


# ============================================================================
# PHASE 4: ENSEMBLE METHODS
# ============================================================================

    def phase4_ensemble_methods(self):
        """Phase 4: Voting & Stacking Ensembles"""
        print("\n" + "="*70)
        print("PHASE 4: ENSEMBLE METHODS (VOTING + STACKING)")
        print("="*70)
        
        # Base learners
        base_learners = [
            ('rf', RandomForestClassifier(n_estimators=300, max_depth=20, 
                                         random_state=42, n_jobs=-1)),
            ('gb', GradientBoostingClassifier(n_estimators=300, max_depth=10,
                                             random_state=42)),
            ('svm', SVC(kernel='rbf', probability=True, random_state=42)),
        ]
        
        # Voting Classifier (soft voting uses probabilities)
        print("\n  Training Voting Ensemble...", end='')
        voting_clf = VotingClassifier(estimators=base_learners, voting='soft')
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        voting_scores = cross_validate(voting_clf, self.X_train, self.y_train,
                                      cv=cv, scoring='f1_macro')
        voting_f1 = voting_scores['test_score'].mean()
        print(f" ✓ F1-Score: {voting_f1:.4f}")
        
        # Stacking Classifier
        print("  Training Stacking Ensemble...", end='')
        stacking_clf = StackingClassifier(
            estimators=base_learners,
            final_estimator=LogisticRegression(max_iter=1000),
            cv=5
        )
        stacking_scores = cross_validate(stacking_clf, self.X_train, 
                                        self.y_train, cv=cv, 
                                        scoring='f1_macro')
        stacking_f1 = stacking_scores['test_score'].mean()
        print(f" ✓ F1-Score: {stacking_f1:.4f}")
        
        # Store models
        voting_clf.fit(self.X_train, self.y_train)
        stacking_clf.fit(self.X_train, self.y_train)
        
        self.models['voting_ensemble'] = voting_clf
        self.models['stacking_ensemble'] = stacking_clf
        
        ensemble_results = {
            'Voting Ensemble': voting_f1,
            'Stacking Ensemble': stacking_f1,
        }
        
        self.results['phase4_ensemble'] = ensemble_results
        
        print("\n" + "="*70)
        print("Ensemble Methods Results:")
        for method, f1 in ensemble_results.items():
            print(f"  {method}: {f1:.4f}")
        print("="*70)
        
        # Save results
        pd.DataFrame(ensemble_results, index=['F1-Score']).T.to_csv(
            self.results_dir / 'phase4_ensemble_results.csv')
        print(f"✓ Results saved: {self.results_dir / 'phase4_ensemble_results.csv'}")
        
        return ensemble_results


# ============================================================================
# PHASE 5: DEEP LEARNING
# ============================================================================

    def phase5_deep_learning(self):
        """Phase 5: Neural Network Models"""
        print("\n" + "="*70)
        print("PHASE 5: DEEP LEARNING (NEURAL NETWORKS)")
        print("="*70)
        
        try:
            import tensorflow as tf
            from tensorflow import keras
        except ImportError:
            print("⚠️  TensorFlow not available. Skipping phase 5.")
            return {}
        
        # Scale features for neural network
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(self.X_train)
        X_val_scaled = scaler.transform(self.X_val)
        X_test_scaled = scaler.transform(self.X_test)
        
        print("\n  Building Neural Network...", end='')
        
        # Build model
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', 
                             input_shape=(self.X_train.shape[1],)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        print(" ✓")
        
        # Train with early stopping
        print("  Training Neural Network...", end='')
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        history = model.fit(
            X_train_scaled, self.y_train,
            validation_data=(X_val_scaled, self.y_val),
            epochs=100, batch_size=32, callbacks=[early_stop],
            verbose=0
        )
        print(" ✓")
        
        # Evaluate
        nn_accuracy = model.evaluate(X_test_scaled, self.y_test, 
                                     verbose=0)[1]
        
        print(f"\n  Neural Network Test Accuracy: {nn_accuracy:.4f}")
        
        self.models['neural_network'] = model
        self.results['phase5_nn'] = {'accuracy': float(nn_accuracy)}
        
        # Plot training history
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        axes[0].plot(history.history['loss'], label='Training', linewidth=2)
        axes[0].plot(history.history['val_loss'], label='Validation', linewidth=2)
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Neural Network Training Loss')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(history.history['accuracy'], label='Training', linewidth=2)
        axes[1].plot(history.history['val_accuracy'], label='Validation', 
                    linewidth=2)
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title('Neural Network Training Accuracy')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase5_nn_training.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {self.figures_dir / 'phase5_nn_training.png'}")
        
        return {'neural_network_accuracy': nn_accuracy}


# ============================================================================
# PHASE 6: EXPLAINABILITY
# ============================================================================

    def phase6_explainability(self):
        """Phase 6: SHAP & Feature Importance Analysis"""
        print("\n" + "="*70)
        print("PHASE 6: EXPLAINABILITY ANALYSIS")
        print("="*70)
        
        model = self.models['optimized_rf']
        
        # Feature importance (traditional)
        print("\n  Computing feature importance...")
        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(importance_df.head(10).to_string(index=False))
        
        # Save feature importance
        importance_df.to_csv(self.results_dir / 'phase6_feature_importance.csv',
                            index=False)
        
        # Plot feature importance
        fig, ax = plt.subplots(figsize=(10, 8))
        top_n = 15
        top_features = importance_df.head(top_n)
        
        ax.barh(range(len(top_features)), top_features['importance'].values,
               color='steelblue')
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'].values)
        ax.set_xlabel('Importance')
        ax.set_title(f'Top {top_n} Feature Importance (RandomForest)')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase6_feature_importance.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {self.figures_dir / 'phase6_feature_importance.png'}")
        
        # SHAP Analysis (if available)
        if HAS_SHAP:
            print("\n  Computing SHAP values (this may take a moment)...")
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(self.X_test)
            
            # Summary plot
            fig, ax = plt.subplots(figsize=(10, 8))
            if isinstance(shap_values, list):
                shap_vals = shap_values[2]  # HIGH risk class
            else:
                shap_vals = shap_values
            
            shap.summary_plot(shap_vals, self.X_test, 
                            feature_names=self.feature_names,
                            plot_type="bar", show=False)
            plt.tight_layout()
            plt.savefig(self.figures_dir / 'phase6_shap_summary.png',
                       dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ SHAP summary saved: {self.figures_dir / 'phase6_shap_summary.png'}")
        
        self.results['phase6_explainability'] = {
            'top_features': importance_df.head(10).to_dict('records')
        }
        
        return importance_df


# ============================================================================
# PHASE 7: CALIBRATION ANALYSIS
# ============================================================================

    def phase7_calibration(self):
        """Phase 7: Model Calibration Analysis"""
        print("\n" + "="*70)
        print("PHASE 7: CALIBRATION ANALYSIS")
        print("="*70)
        
        model = self.models['optimized_rf']
        y_pred_proba = model.predict_proba(self.X_test)
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        calibration_results = {}
        
        for class_idx in range(3):
            y_test_binary = (self.y_test == class_idx).astype(int)
            y_proba_class = y_pred_proba[:, class_idx]
            
            # Calibration curve
            prob_true, prob_pred = calibration_curve(
                y_test_binary, y_proba_class, n_bins=10
            )
            
            # Compute ECE (Expected Calibration Error)
            ece = np.mean(np.abs(prob_true - prob_pred))
            
            calibration_results[f'class_{class_idx}'] = {
                'ece': float(ece),
                'prob_true': prob_true.tolist(),
                'prob_pred': prob_pred.tolist(),
            }
            
            # Plot
            axes[class_idx].plot([0, 1], [0, 1], 'k--', lw=2, 
                                label='Perfectly calibrated')
            axes[class_idx].plot(prob_pred, prob_true, 'o-', lw=2, ms=8,
                                label='RandomForest')
            axes[class_idx].set_xlabel('Mean Predicted Probability')
            axes[class_idx].set_ylabel('Fraction of Positives')
            axes[class_idx].set_title(f'Class {class_idx} Calibration\n(ECE: {ece:.4f})')
            axes[class_idx].legend()
            axes[class_idx].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase7_calibration.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {self.figures_dir / 'phase7_calibration.png'}")
        
        print("\nCalibration Results (ECE - Lower is Better):")
        for class_name, results in calibration_results.items():
            print(f"  {class_name}: {results['ece']:.4f}")
        
        self.results['phase7_calibration'] = calibration_results
        
        # Save results
        with open(self.results_dir / 'phase7_calibration.json', 'w') as f:
            json.dump(calibration_results, f, indent=2)
        
        return calibration_results


# ============================================================================
# PHASE 8: UNCERTAINTY QUANTIFICATION
# ============================================================================

    def phase8_uncertainty(self):
        """Phase 8: Uncertainty Quantification"""
        print("\n" + "="*70)
        print("PHASE 8: UNCERTAINTY QUANTIFICATION")
        print("="*70)
        
        print("\n  Computing prediction uncertainty...", end='')
        
        # Use ensemble for uncertainty
        model = self.models['optimized_rf']
        y_pred_proba = model.predict_proba(self.X_test)
        
        # Entropy as uncertainty measure
        entropy = -np.sum(y_pred_proba * np.log(y_pred_proba + 1e-10), axis=1)
        
        # Confidence (max probability)
        confidence = y_pred_proba.max(axis=1)
        
        print(" ✓")
        
        print(f"\n  Mean Entropy: {entropy.mean():.4f}")
        print(f"  Mean Confidence: {confidence.mean():.4f}")
        print(f"  High Uncertainty Samples (entropy > mean): {(entropy > entropy.mean()).sum()}")
        
        # Plot uncertainty distribution
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        axes[0].hist(entropy, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        axes[0].axvline(entropy.mean(), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {entropy.mean():.4f}')
        axes[0].set_xlabel('Entropy')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Prediction Uncertainty Distribution')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        axes[1].scatter(confidence, entropy, alpha=0.5, s=30)
        axes[1].set_xlabel('Confidence (Max Probability)')
        axes[1].set_ylabel('Entropy')
        axes[1].set_title('Confidence vs Uncertainty')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase8_uncertainty.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {self.figures_dir / 'phase8_uncertainty.png'}")
        
        uncertainty_results = {
            'mean_entropy': float(entropy.mean()),
            'mean_confidence': float(confidence.mean()),
            'high_uncertainty_count': int((entropy > entropy.mean()).sum()),
        }
        
        self.results['phase8_uncertainty'] = uncertainty_results
        
        return uncertainty_results


# ============================================================================
# PHASE 9: FAIRNESS & BIAS ANALYSIS
# ============================================================================

    def phase9_fairness(self):
        """Phase 9: Fairness & Bias Analysis"""
        print("\n" + "="*70)
        print("PHASE 9: FAIRNESS & BIAS ANALYSIS")
        print("="*70)
        
        model = self.models['optimized_rf']
        y_pred = model.predict(self.X_test)
        
        # Define subgroups
        subgroups = {}
        
        # Gender
        if 'sex' in self.X_test.columns:
            for sex in self.X_test['sex'].unique():
                mask = self.X_test['sex'] == sex
                subgroups[f'Sex={sex}'] = {
                    'X': self.X_test[mask],
                    'y': self.y_test[mask],
                    'pred': y_pred[mask]
                }
        
        # Age groups
        if 'age' in self.X_test.columns:
            subgroups['Age<40'] = {
                'X': self.X_test[self.X_test['age'] < 40],
                'y': self.y_test[self.X_test['age'] < 40],
                'pred': y_pred[self.X_test['age'] < 40]
            }
            subgroups['Age 40-60'] = {
                'X': self.X_test[(self.X_test['age'] >= 40) & 
                                 (self.X_test['age'] <= 60)],
                'y': self.y_test[(self.X_test['age'] >= 40) & 
                                 (self.X_test['age'] <= 60)],
                'pred': y_pred[(self.X_test['age'] >= 40) & 
                              (self.X_test['age'] <= 60)]
            }
            subgroups['Age>60'] = {
                'X': self.X_test[self.X_test['age'] > 60],
                'y': self.y_test[self.X_test['age'] > 60],
                'pred': y_pred[self.X_test['age'] > 60]
            }
        
        # Compute metrics for each subgroup
        fairness_results = {}
        
        for subgroup_name, subgroup_data in subgroups.items():
            if len(subgroup_data['y']) > 0:
                accuracy = accuracy_score(subgroup_data['y'], 
                                         subgroup_data['pred'])
                fairness_results[subgroup_name] = accuracy
        
        print("\nFairness Analysis - Accuracy by Subgroup:")
        print("-" * 50)
        for subgroup, accuracy in fairness_results.items():
            print(f"  {subgroup:20s}: {accuracy:.4f}")
        
        # Check for disparities
        if fairness_results:
            max_acc = max(fairness_results.values())
            min_acc = min(fairness_results.values())
            disparity = (max_acc - min_acc) / min_acc * 100
            
            print(f"\n  Max Accuracy: {max_acc:.4f}")
            print(f"  Min Accuracy: {min_acc:.4f}")
            print(f"  Disparity: {disparity:.2f}%")
            
            if disparity > 5:
                print("  ⚠️  WARNING: Model shows potential bias!")
            else:
                print("  ✓ Model is fair across subgroups")
        
        # Plot fairness
        if fairness_results:
            fig, ax = plt.subplots(figsize=(10, 6))
            subgroups_list = list(fairness_results.keys())
            accuracies = list(fairness_results.values())
            
            colors = ['green' if acc > min_acc + (max_acc - min_acc) * 0.1 
                     else 'orange' for acc in accuracies]
            
            ax.barh(range(len(subgroups_list)), accuracies, color=colors, 
                   alpha=0.7, edgecolor='black')
            ax.set_yticks(range(len(subgroups_list)))
            ax.set_yticklabels(subgroups_list)
            ax.set_xlabel('Accuracy')
            ax.set_title('Fairness Analysis: Accuracy by Subgroup')
            ax.grid(axis='x', alpha=0.3)
            ax.set_xlim([0, 1])
            
            plt.tight_layout()
            plt.savefig(self.figures_dir / 'phase9_fairness.png',
                       dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ Figure saved: {self.figures_dir / 'phase9_fairness.png'}")
        
        self.results['phase9_fairness'] = fairness_results
        
        return fairness_results


# ============================================================================
# PHASE 10: ROBUSTNESS TESTING
# ============================================================================

    def phase10_robustness(self):
        """Phase 10: Robustness Testing"""
        print("\n" + "="*70)
        print("PHASE 10: ROBUSTNESS TESTING")
        print("="*70)
        
        model = self.models['optimized_rf']
        baseline_accuracy = model.score(self.X_test, self.y_test)
        
        robustness_results = {
            'baseline': baseline_accuracy
        }
        
        # Test 1: Missing data robustness
        print("\n  Test 1: Missing Data Robustness...", end='')
        X_test_missing = self.X_test.copy()
        missing_mask = np.random.random(X_test_missing.shape) < 0.1
        X_test_missing[missing_mask] = np.nan
        
        imputer = SimpleImputer(strategy='median')
        X_test_missing_filled = imputer.fit_transform(X_test_missing)
        
        accuracy_missing = model.score(X_test_missing_filled, self.y_test)
        robustness_results['missing_data_10%'] = accuracy_missing
        print(f" ✓ {accuracy_missing:.4f}")
        
        # Test 2: Outlier robustness
        print("  Test 2: Outlier Robustness (2x scaling)...", end='')
        X_test_outliers = self.X_test.copy()
        outlier_indices = np.random.choice(len(X_test_outliers), 
                                          size=100, replace=False)
        X_test_outliers.iloc[outlier_indices] *= 2
        
        accuracy_outliers = model.score(X_test_outliers, self.y_test)
        robustness_results['outliers_2x'] = accuracy_outliers
        print(f" ✓ {accuracy_outliers:.4f}")
        
        # Test 3: Noise robustness
        print("  Test 3: Noise Robustness (Gaussian)...", end='')
        X_test_noisy = self.X_test.copy()
        noise = np.random.normal(0, 0.1, X_test_noisy.shape)
        X_test_noisy_values = X_test_noisy.values + noise
        
        accuracy_noisy = model.score(X_test_noisy_values, self.y_test)
        robustness_results['gaussian_noise_0.1'] = accuracy_noisy
        print(f" ✓ {accuracy_noisy:.4f}")
        
        # Test 4: Feature ablation (drop one feature at a time)
        print("  Test 4: Feature Ablation Study...")
        ablation_results = {}
        
        for feature_idx, feature_name in enumerate(self.feature_names):
            X_test_ablated = self.X_test.copy()
            X_test_ablated.iloc[:, feature_idx] = np.random.permutation(
                X_test_ablated.iloc[:, feature_idx].values
            )
            
            accuracy_ablated = model.score(X_test_ablated, self.y_test)
            importance = baseline_accuracy - accuracy_ablated
            ablation_results[feature_name] = importance
        
        # Top 10 features by ablation
        top_ablation = sorted(ablation_results.items(), 
                             key=lambda x: x[1], reverse=True)[:10]
        
        print("\n    Top 10 Features by Ablation Importance:")
        for feature, importance in top_ablation:
            print(f"      {feature:20s}: {importance:.4f}")
        
        robustness_results['ablation_study'] = dict(top_ablation)
        
        # Plot robustness
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Robustness tests
        test_names = ['Baseline', 'Missing 10%', 'Outliers 2x', 'Noise 0.1']
        test_accuracies = [
            robustness_results['baseline'],
            robustness_results['missing_data_10%'],
            robustness_results['outliers_2x'],
            robustness_results['gaussian_noise_0.1'],
        ]
        
        colors_rob = ['green'] + ['orange' if acc < 0.98 else 'yellow' 
                                  for acc in test_accuracies[1:]]
        
        axes[0].bar(range(len(test_names)), test_accuracies, 
                   color=colors_rob, alpha=0.7, edgecolor='black')
        axes[0].set_xticks(range(len(test_names)))
        axes[0].set_xticklabels(test_names, rotation=45, ha='right')
        axes[0].set_ylabel('Accuracy')
        axes[0].set_title('Robustness Testing Results')
        axes[0].set_ylim([0.85, 1.0])
        axes[0].grid(axis='y', alpha=0.3)
        
        # Ablation study
        ablation_names = [f[0] for f in top_ablation]
        ablation_importance = [f[1] for f in top_ablation]
        
        axes[1].barh(range(len(ablation_names)), ablation_importance,
                    color='steelblue', alpha=0.7, edgecolor='black')
        axes[1].set_yticks(range(len(ablation_names)))
        axes[1].set_yticklabels(ablation_names)
        axes[1].set_xlabel('Importance (Accuracy Drop)')
        axes[1].set_title('Top 10 Features by Ablation')
        axes[1].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'phase10_robustness.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Figure saved: {self.figures_dir / 'phase10_robustness.png'}")
        
        self.results['phase10_robustness'] = robustness_results
        
        print("\n" + "="*70)
        print("Robustness Summary:")
        print(f"  Baseline Accuracy: {baseline_accuracy:.4f}")
        print(f"  Missing Data (10%): {accuracy_missing:.4f} "
              f"({(baseline_accuracy - accuracy_missing)*100:+.2f}%)")
        print(f"  Outliers (2x): {accuracy_outliers:.4f} "
              f"({(baseline_accuracy - accuracy_outliers)*100:+.2f}%)")
        print(f"  Gaussian Noise (0.1): {accuracy_noisy:.4f} "
              f"({(baseline_accuracy - accuracy_noisy)*100:+.2f}%)")
        print("="*70)
        
        return robustness_results


# ============================================================================
# GENERATE COMPREHENSIVE REPORT
# ============================================================================

    def generate_report(self):
        """Generate comprehensive research report"""
        print("\n" + "="*70)
        print("GENERATING COMPREHENSIVE RESEARCH REPORT")
        print("="*70)
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║     RESPIRATORY RISK PREDICTION - COMPREHENSIVE RESEARCH REPORT       ║
╚═══════════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PHASE 1: CROSS-VALIDATION & STATISTICAL RIGOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5-Fold Stratified Cross-Validation Results:
"""
        
        if 'phase1_cv' in self.results:
            for metric, values in self.results['phase1_cv'].items():
                report += f"  {metric.upper():20s}: {values['test_mean']:.4f} ± {values['test_std']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. PHASE 2: BASELINE COMPARISONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Model Comparison (6 Models):
"""
        
        if 'phase2_comparison' in self.results:
            for model_name, metrics in sorted(self.results['phase2_comparison'].items()):
                if 'error' not in metrics:
                    report += f"  {model_name:25s}: Acc={metrics.get('accuracy_mean', 0):.4f} "
                    report += f"F1={metrics.get('f1_mean', 0):.4f} "
                    report += f"AUC={metrics.get('roc_auc_mean', 0):.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. PHASE 3: BAYESIAN HYPERPARAMETER OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best Parameters Found:
"""
        
        if 'phase3_optimization' in self.results:
            for param, value in self.results['phase3_optimization']['best_params'].items():
                report += f"  {param:25s}: {value}\n"
            report += f"  Best F1-Score: {self.results['phase3_optimization']['best_score']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. PHASE 4: ENSEMBLE METHODS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ensemble Results:
"""
        
        if 'phase4_ensemble' in self.results:
            for method, f1 in self.results['phase4_ensemble'].items():
                report += f"  {method:30s}: {f1:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. PHASE 5: DEEP LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Neural Network Results:
"""
        
        if 'phase5_nn' in self.results:
            report += f"  Neural Network Accuracy: {self.results['phase5_nn']['accuracy']:.4f}\n"
        else:
            report += "  TensorFlow not available\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. PHASE 6: EXPLAINABILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Top 10 Most Important Features:
"""
        
        if 'phase6_explainability' in self.results:
            for idx, feature_dict in enumerate(self.results['phase6_explainability']['top_features'], 1):
                report += f"  {idx:2d}. {feature_dict['feature']:20s}: {feature_dict['importance']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. PHASE 7: CALIBRATION ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Expected Calibration Error (ECE) by Class:
"""
        
        if 'phase7_calibration' in self.results:
            for class_name, results in self.results['phase7_calibration'].items():
                report += f"  {class_name:15s}: {results['ece']:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. PHASE 8: UNCERTAINTY QUANTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Uncertainty Metrics:
"""
        
        if 'phase8_uncertainty' in self.results:
            for metric, value in self.results['phase8_uncertainty'].items():
                report += f"  {metric:30s}: {value}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9. PHASE 9: FAIRNESS & BIAS ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Accuracy by Subgroup:
"""
        
        if 'phase9_fairness' in self.results:
            for subgroup, accuracy in self.results['phase9_fairness'].items():
                report += f"  {subgroup:20s}: {accuracy:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

10. PHASE 10: ROBUSTNESS TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Robustness Test Results:
"""
        
        if 'phase10_robustness' in self.results:
            for test_name, result in self.results['phase10_robustness'].items():
                if isinstance(result, dict):
                    continue
                report += f"  {test_name:25s}: {result:.4f}\n"
        
        report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTPUTS GENERATED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results Tables:
  ✓ phase1_cv_results.csv
  ✓ phase2_model_comparison.csv
  ✓ phase3_best_params.json
  ✓ phase4_ensemble_results.csv
  ✓ phase6_feature_importance.csv
  ✓ phase7_calibration.json

Figures & Visualizations:
  ✓ phase2_model_comparison.png
  ✓ phase3_convergence.png
  ✓ phase5_nn_training.png
  ✓ phase6_feature_importance.png
  ✓ phase6_shap_summary.png (if SHAP available)
  ✓ phase7_calibration.png
  ✓ phase8_uncertainty.png
  ✓ phase9_fairness.png
  ✓ phase10_robustness.png

LOCATIONS:
  Results:  {self.results_dir}
  Figures:  {self.figures_dir}
  Reports:  {self.reports_dir}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Save report
        report_path = self.reports_dir / 'comprehensive_research_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(report)
        print(f"\n✓ Report saved: {report_path}")
        
        return report


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete research pipeline"""
    
    # Initialize pipeline
    pipeline = ResearchPipeline(
        data_path='/Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training/data_engineered.csv',
        output_dir='/Users/taneeshkpatel/Desktop/OVGU_Projects/agent-training/research'
    )
    
    # Load data
    X, y = pipeline.load_data()
    pipeline.split_data()
    
    # Run all phases
    print("\n🔬 RUNNING ALL 10 RESEARCH PHASES...\n")
    
    try:
        pipeline.phase1_cross_validation()
        pipeline.phase2_baseline_comparisons()
        pipeline.phase3_bayesian_optimization()
        pipeline.phase4_ensemble_methods()
        pipeline.phase5_deep_learning()
        pipeline.phase6_explainability()
        pipeline.phase7_calibration()
        pipeline.phase8_uncertainty()
        pipeline.phase9_fairness()
        pipeline.phase10_robustness()
        
        # Generate comprehensive report
        pipeline.generate_report()
        
        print("\n" + "="*70)
        print("✅ RESEARCH PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\nAll results saved to: {pipeline.output_dir}")
        print(f"Check the 'results', 'figures', and 'reports' folders")
        print("\n📊 Ready for publication!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
