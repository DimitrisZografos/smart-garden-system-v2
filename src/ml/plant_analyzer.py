"""
Plant analyzer module for the Smart Garden System.
Uses machine learning to analyze plant images for growth tracking and disease detection.
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class PlantAnalyzer:
    """
    Analyzes plant images using machine learning.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the plant analyzer.
        
        Args:
            config: ML configuration from config.yaml
        """
        self.config = config
        self.model_dir = config.get('model_dir', 'models')
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initialize ML model
        self._init_model()
        
        logger.info("Plant analyzer initialized")
    
    def _init_model(self) -> None:
        """Initialize the ML model."""
        try:
            # Check if we have a saved model
            model_path = os.path.join(self.model_dir, 'plant_model.pkl')
            
            if os.path.exists(model_path):
                self._load_model(model_path)
            else:
                # Create a simple model
                self._create_simple_model()
                
        except Exception as e:
            logger.error(f"Error initializing ML model: {str(e)}")
            # Create a fallback model
            self._create_simple_model()
    
    def _load_model(self, model_path: str) -> None:
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
        """
        try:
            from sklearn.externals import joblib
            self.model = joblib.load(model_path)
            logger.info(f"ML model loaded from {model_path}")
        except ImportError:
            logger.warning("scikit-learn not available, using simple model")
            self._create_simple_model()
        except Exception as e:
            logger.error(f"Error loading ML model: {str(e)}")
            self._create_simple_model()
    
    def _create_simple_model(self) -> None:
        """Create a simple rule-based model."""
        # This is a placeholder for a real ML model
        # In a real implementation, you would train a model on plant images
        
        # For now, we'll just use a simple rule-based system
        self.model = {
            'type': 'rule_based',
            'created_at': time.time()
        }
        
        logger.info("Simple rule-based model created")
    
    def _save_model(self, model_path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            model_path: Path to save the model to
        """
        try:
            from sklearn.externals import joblib
            joblib.dump(self.model, model_path)
            logger.info(f"ML model saved to {model_path}")
        except ImportError:
            logger.warning("scikit-learn not available, model not saved")
        except Exception as e:
            logger.error(f"Error saving ML model: {str(e)}")
    
    def _extract_features(self, image_path: str) -> Dict[str, Any]:
        """
        Extract features from an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary of extracted features
        """
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract simple features
            # In a real implementation, you would extract meaningful features
            # For now, we'll just use simple color statistics
            
            # Calculate average color
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Calculate color histograms
            r_hist, _ = np.histogram(img_array[:, :, 0], bins=10, range=(0, 256))
            g_hist, _ = np.histogram(img_array[:, :, 1], bins=10, range=(0, 256))
            b_hist, _ = np.histogram(img_array[:, :, 2], bins=10, range=(0, 256))
            
            # Calculate green ratio (for plant health)
            if avg_color[0] + avg_color[1] + avg_color[2] > 0:
                green_ratio = avg_color[1] / (avg_color[0] + avg_color[1] + avg_color[2])
            else:
                green_ratio = 0
            
            features = {
                'avg_color': avg_color.tolist(),
                'r_hist': r_hist.tolist(),
                'g_hist': g_hist.tolist(),
                'b_hist': b_hist.tolist(),
                'green_ratio': green_ratio
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {}
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a plant image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Analysis results
        """
        try:
            logger.info(f"Analyzing image: {image_path}")
            
            # Extract features
            features = self._extract_features(image_path)
            
            if not features:
                logger.warning(f"Failed to extract features from {image_path}")
                return {'error': 'Failed to extract features'}
            
            # Analyze using our model
            if self.model['type'] == 'rule_based':
                # Simple rule-based analysis
                results = self._rule_based_analysis(features)
            else:
                # ML-based analysis
                results = self._ml_analysis(features)
            
            # Add timestamp
            results['timestamp'] = time.time()
            
            # Save results
            self._save_analysis_results(image_path, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {'error': str(e)}
    
    def _rule_based_analysis(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform rule-based analysis on image features.
        
        Args:
            features: Extracted image features
            
        Returns:
            Analysis results
        """
        # Simple rules for plant health based on color
        green_ratio = features.get('green_ratio', 0)
        
        # Determine plant health
        if green_ratio > 0.4:
            health = 'good'
        elif green_ratio > 0.3:
            health = 'fair'
        else:
            health = 'poor'
        
        # Check for potential issues
        issues = []
        
        # Check for yellowing (low green, high red and blue)
        avg_color = features.get('avg_color', [0, 0, 0])
        if avg_color[1] < 100 and avg_color[0] > 100 and avg_color[2] > 100:
            issues.append('yellowing')
        
        # Check for browning (high red, low green and blue)
        if avg_color[0] > 100 and avg_color[1] < 80 and avg_color[2] < 80:
            issues.append('browning')
        
        # Estimate growth stage based on green intensity
        if green_ratio > 0.45:
            growth_stage = 'mature'
        elif green_ratio > 0.35:
            growth_stage = 'developing'
        else:
            growth_stage = 'early'
        
        return {
            'health': health,
            'issues': issues,
            'growth_stage': growth_stage,
            'confidence': 0.6  # Low confidence for rule-based analysis
        }
    
    def _ml_analysis(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform ML-based analysis on image features.
        
        Args:
            features: Extracted image features
            
        Returns:
            Analysis results
        """
        # This is a placeholder for real ML-based analysis
        # In a real implementation, you would use your trained model
        
        # For now, we'll just return the rule-based results
        return self._rule_based_analysis(features)
    
    def _save_analysis_results(self, image_path: str, results: Dict[str, Any]) -> None:
        """
        Save analysis results.
        
        Args:
            image_path: Path to the analyzed image
            results: Analysis results
        """
        try:
            # Save results as JSON
            results_path = f"{os.path.splitext(image_path)[0]}_analysis.json"
            
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Analysis results saved to {results_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")
    
    def train(self, image_dir: Optional[str] = None) -> bool:
        """
        Train the ML model on plant images.
        
        Args:
            image_dir: Directory containing training images (optional)
            
        Returns:
            True if training was successful, False otherwise
        """
        try:
            logger.info("Training plant analyzer model")
            
            # In a real implementation, you would:
            # 1. Load training images
            # 2. Extract features
            # 3. Train a model (e.g., using scikit-learn or TensorFlow)
            # 4. Save the trained model
            
            # For now, we'll just update our simple model
            self.model = {
                'type': 'rule_based',
                'created_at': time.time(),
                'version': self.model.get('version', 0) + 1
            }
            
            # Save the model
            model_path = os.path.join(self.model_dir, 'plant_model.pkl')
            self._save_model(model_path)
            
            logger.info("Model training completed")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False