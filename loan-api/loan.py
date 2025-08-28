from flask import Flask, request, jsonify
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import logging
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model
try:
    model = joblib.load('loan_model.pkl')
except FileNotFoundError:
    logger.error("Error: loan_model.pkl not found")
    exit(1)
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    exit(1)


categorical_cols = ['EmploymentStatus', 'BankruptcyHistory']  # Updated categorical columns
label_encoders = {}
for col in categorical_cols:
    try:
        label_encoders[col] = joblib.load(f'{col}_encoder.pkl')
    except FileNotFoundError:
        logger.warning(f"Encoder for {col} not found, using dynamic encoding")
        label_encoders[col] = None

# Define model features
try:
    model_features = model.feature_names_in_
except AttributeError:
    model_features = [
        'CreditScore',
        'DebtToIncomeRatio',
        'PreviousLoanDefaults',
        'BankruptcyHistory',
        'EmploymentStatus',
        'AnnualIncome',
        'LoanAmount',
        'LoanDuration',
        'MonthlyIncome',
        'TotalAssets',
        'NetWorth'
    ]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        
        # Validate required fields
        required_fields = ['CreditScore', 'AnnualIncome', 'LoanAmount']  # Updated required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Validate numerical ranges
        if data['CreditScore'] < 300 or data['CreditScore'] > 850:
            return jsonify({'status': 'error', 'message': 'CreditScore must be between 300 and 850'}), 400

        df = pd.DataFrame([data])
        
        # Align features with defaults
        for feature in model_features:
            if feature not in df.columns:
                if feature in categorical_cols:
                    df[feature] = 'Unknown'  # Default for categorical features
                else:
                    df[feature] = 0  # Default for numerical features
        df = df[model_features]  # Ensure correct column order
        
        # Handle categorical columns
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
                if label_encoders[col] is not None:
                    try:
                        df[col] = label_encoders[col].transform(df[col])
                    except ValueError as e:
                        logger.warning(f"Unseen category in {col}: {str(e)}, setting to -1")
                        df[col] = -1  # Handle unseen categories
                else:
                    # Fallback to dynamic encoding
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col])
                    logger.warning(f"Using dynamic encoding for {col}, this may lead to inconsistent predictions")
        
        # Make prediction
        prediction = model.predict(df)[0]
        logger.info(f"Prediction made: {prediction}")
        return jsonify({'status': 'success', 'LoanApproved': int(prediction)})
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
