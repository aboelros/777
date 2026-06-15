"""
Predictive Analytics Service
Machine learning models for forecasting, churn prediction, and recommendations.
"""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)


class SalesForecaster:
    """
    Predicts future sales using time series analysis and ML.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or 'models/sales_forecaster.pkl'
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk."""
        try:
            if Path(self.model_path).exists():
                self.model = joblib.load(self.model_path)
                logger.info("Sales forecasting model loaded")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self.model = None
    
    def save_model(self):
        """Save trained model to disk."""
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info("Sales forecasting model saved")
    
    def prepare_features(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for forecasting.
        
        Args:
            sales_data: DataFrame with 'date' and 'amount' columns
            
        Returns:
            DataFrame with engineered features
        """
        df = sales_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            df[f'sales_lag_{lag}'] = df['amount'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'sales_rolling_mean_{window}'] = df['amount'].rolling(window).mean()
            df[f'sales_rolling_std_{window}'] = df['amount'].rolling(window).std()
        
        # Drop NaN rows from feature engineering
        df = df.dropna()
        
        return df
    
    def train(self, sales_data: pd.DataFrame):
        """
        Train forecasting model.
        
        Args:
            sales_data: Historical sales data
        """
        logger.info("Training sales forecasting model")
        
        # Prepare features
        df = self.prepare_features(sales_data)
        
        # Split features and target
        feature_cols = [col for col in df.columns if col not in ['date', 'amount']]
        X = df[feature_cols]
        y = df['amount']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        logger.info("Sales forecasting model trained successfully")
    
    def forecast(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Forecast future sales.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of forecasts with dates and predicted amounts
        """
        if not self.model:
            raise ValueError("Model not trained. Call train() first.")
        
        forecasts = []
        start_date = datetime.now()
        
        for i in range(days):
            forecast_date = start_date + timedelta(days=i)
            
            # Create features for forecast date
            features = {
                'day_of_week': forecast_date.weekday(),
                'day_of_month': forecast_date.day,
                'month': forecast_date.month,
                'quarter': (forecast_date.month - 1) // 3 + 1,
                'is_weekend': int(forecast_date.weekday() in [5, 6])
            }
            
            # Add placeholder lag features (would use actual data in production)
            for lag in [1, 7, 14, 30]:
                features[f'sales_lag_{lag}'] = 0
            for window in [7, 14, 30]:
                features[f'sales_rolling_mean_{window}'] = 0
                features[f'sales_rolling_std_{window}'] = 0
            
            # Predict
            X = pd.DataFrame([features])
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)[0]
            
            forecasts.append({
                'date': forecast_date.isoformat(),
                'predicted_amount': float(prediction),
                'confidence': 0.85  # Simplified confidence score
            })
        
        return forecasts


class ChurnPredictor:
    """
    Predicts customer churn probability using ML.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or 'models/churn_predictor.pkl'
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk."""
        try:
            if Path(self.model_path).exists():
                self.model = joblib.load(self.model_path)
                logger.info("Churn prediction model loaded")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self.model = None
    
    def save_model(self):
        """Save trained model to disk."""
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info("Churn prediction model saved")
    
    def prepare_features(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare customer features for churn prediction.
        
        Args:
            customer_data: Customer data with engagement metrics
            
        Returns:
            DataFrame with engineered features
        """
        df = customer_data.copy()
        
        # Engagement features
        df['days_since_last_order'] = (datetime.now() - pd.to_datetime(df['last_order_date'])).dt.days
        df['days_since_signup'] = (datetime.now() - pd.to_datetime(df['signup_date'])).dt.days
        df['avg_order_value'] = df['total_spent'] / df['order_count'].replace(0, 1)
        df['orders_per_month'] = df['order_count'] / (df['days_since_signup'] / 30).replace(0, 1)
        
        # Interaction features
        df['messages_per_order'] = df['message_count'] / df['order_count'].replace(0, 1)
        df['response_rate'] = df['responses_received'] / df['messages_sent'].replace(0, 1)
        
        # Recency, Frequency, Monetary (RFM)
        df['recency_score'] = pd.qcut(df['days_since_last_order'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        df['frequency_score'] = pd.qcut(df['order_count'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        df['monetary_score'] = pd.qcut(df['total_spent'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        return df
    
    def train(self, customer_data: pd.DataFrame, churn_labels: pd.Series):
        """
        Train churn prediction model.
        
        Args:
            customer_data: Customer features
            churn_labels: Binary churn labels (1 = churned, 0 = active)
        """
        logger.info("Training churn prediction model")
        
        # Prepare features
        df = self.prepare_features(customer_data)
        
        # Select numeric features
        feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        X = df[feature_cols]
        y = churn_labels
        
        # Handle missing values
        X = X.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        logger.info("Churn prediction model trained successfully")
    
    def predict_churn(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict churn probability for a customer.
        
        Args:
            customer_data: Customer features
            
        Returns:
            Churn prediction with probability and risk factors
        """
        if not self.model:
            raise ValueError("Model not trained. Call train() first.")
        
        # Prepare features
        df = pd.DataFrame([customer_data])
        df = self.prepare_features(df)
        
        # Select numeric features
        feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        X = df[feature_cols].fillna(0)
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        churn_probability = self.model.predict_proba(X_scaled)[0][1]
        
        # Identify risk factors
        risk_factors = []
        if customer_data.get('days_since_last_order', 0) > 30:
            risk_factors.append('No recent orders')
        if customer_data.get('order_count', 0) < 3:
            risk_factors.append('Low purchase frequency')
        if customer_data.get('message_count', 0) == 0:
            risk_factors.append('No engagement')
        
        return {
            'churn_probability': float(churn_probability),
            'risk_level': 'HIGH' if churn_probability > 0.7 else 'MEDIUM' if churn_probability > 0.4 else 'LOW',
            'risk_factors': risk_factors,
            'recommended_actions': self._get_retention_actions(churn_probability, risk_factors)
        }
    
    def _get_retention_actions(self, churn_prob: float, risk_factors: List[str]) -> List[str]:
        """Get recommended retention actions."""
        actions = []
        
        if churn_prob > 0.7:
            actions.append('Send personalized win-back offer')
            actions.append('Schedule personal outreach call')
        elif churn_prob > 0.4:
            actions.append('Send re-engagement email')
            actions.append('Offer loyalty discount')
        
        if 'No recent orders' in risk_factors:
            actions.append('Send product recommendations')
        if 'Low purchase frequency' in risk_factors:
            actions.append('Create subscription offer')
        if 'No engagement' in risk_factors:
            actions.append('Send survey to understand needs')
        
        return actions


class RecommendationEngine:
    """
    AI-powered product recommendation system.
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.item_similarity = None
    
    def collaborative_filtering(
        self,
        customer_id: int,
        purchase_history: pd.DataFrame,
        n_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate product recommendations using collaborative filtering.
        
        Args:
            customer_id: Customer ID
            purchase_history: Purchase history data
            n_recommendations: Number of recommendations
            
        Returns:
            List of recommended products
        """
        # Simplified collaborative filtering
        # In production, use more sophisticated algorithms
        
        recommendations = []
        
        # Find similar customers
        customer_purchases = purchase_history[purchase_history['customer_id'] == customer_id]['product_id'].tolist()
        
        # Find products bought by similar customers
        similar_customer_purchases = purchase_history[
            purchase_history['product_id'].isin(customer_purchases)
        ]['customer_id'].unique()
        
        # Get products they bought that this customer hasn't
        recommended_products = purchase_history[
            (purchase_history['customer_id'].isin(similar_customer_purchases)) &
            (~purchase_history['product_id'].isin(customer_purchases))
        ]['product_id'].value_counts().head(n_recommendations)
        
        for product_id, count in recommended_products.items():
            recommendations.append({
                'product_id': int(product_id),
                'score': float(count / len(similar_customer_purchases)),
                'reason': 'Customers like you also bought this'
            })
        
        return recommendations
