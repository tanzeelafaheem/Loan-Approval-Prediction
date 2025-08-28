import streamlit as st
import requests
import json

st.markdown(
    """
    <style>
    .main {
        background-color: #1a252f;
        color: #d3d8de;
        padding: 10px;
    }
    .stApp {
        background-color: #1a252f;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: scale(1.05);
    }
    .stTextInput>input, .stNumberInput>input, .stSelectbox>select {
        background-color: #2c3e50;
        color: #d3d8de;
        border: 1px solid #34495e;
        border-radius: 5px;
    }
    .stExpander {
        background-color: #2c3e50;
        border: 1px solid #34495e;
        border-radius: 5px;
    }
    .success {
        color: #2ecc71;
        font-weight: bold;
    }
    .error {
        color: #e74c3c;
        font-weight: bold;
    }
    .stProgress > div > div > div {
        background-color: #1a252f;
    }
    .stProgress > div > div {
        background-color: #34495e;
    }
    .button-container {
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("<h1 style='text-align: center; color: #3498db;'>Loan Approval Prediction</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("About")
st.sidebar.text("This app predicts loan approval based on your financial profile. Enter the details below and click 'Predict' to see the result!")

if 'form_state' not in st.session_state:
    st.session_state.form_state = {
        'CreditScore': 600,
        'DebtToIncomeRatio': 0.2,
        'PreviousLoanDefaults': 0,
        'BankruptcyHistory': 0,
        'EmploymentStatus': 'Employed',
        'AnnualIncome': 50000.0,
        'LoanAmount': 10000.0,
        'LoanDuration': 36,
        'MonthlyIncome': 4166.67,
        'TotalAssets': 50000.0,
        'NetWorth': 40000.0
    }

# Main content with sections
with st.container():
    # Personal and Financial Information
    with st.expander("Personal and Financial Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=st.session_state.form_state['CreditScore'], key="CreditScore")
            employment_status = st.selectbox("Employment Status", ["Employed", "Unemployed", "Self-Employed"], index=["Employed", "Unemployed", "Self-Employed"].index(st.session_state.form_state['EmploymentStatus']), key="EmploymentStatus")
            annual_income = st.number_input("Annual Income", min_value=0.0, value=st.session_state.form_state['AnnualIncome'], key="AnnualIncome")
            monthly_income = st.number_input("Monthly Income", min_value=0.0, value=st.session_state.form_state['MonthlyIncome'], key="MonthlyIncome")
        with col2:
            debt_to_income_ratio = st.number_input("Debt to Income Ratio", min_value=0.0, value=st.session_state.form_state['DebtToIncomeRatio'], key="DebtToIncomeRatio")
            bankruptcy_history = st.number_input("Bankruptcy History (0 or 1)", min_value=0, max_value=1, value=st.session_state.form_state['BankruptcyHistory'], key="BankruptcyHistory")
            net_worth = st.number_input("Net Worth", min_value=-1000000.0, value=st.session_state.form_state['NetWorth'], key="NetWorth")
            total_assets = st.number_input("Total Assets", min_value=0.0, value=st.session_state.form_state['TotalAssets'], key="TotalAssets")

    # Loan Details
    with st.expander("Loan Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            loan_amount = st.number_input("Loan Amount", min_value=0.0, value=st.session_state.form_state['LoanAmount'], key="LoanAmount")
            loan_duration = st.number_input("Loan Duration (months)", min_value=0, value=st.session_state.form_state['LoanDuration'], key="LoanDuration")
        with col2:
            previous_loan_defaults = st.number_input("Previous Loan Defaults", min_value=0, value=st.session_state.form_state['PreviousLoanDefaults'], key="PreviousLoanDefaults")

    # Button container for Predict and Reset buttons
    with st.container():
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Predict"):
                with st.spinner("Analyzing your loan application..."):
                    data = {
                        'CreditScore': credit_score,
                        'DebtToIncomeRatio': debt_to_income_ratio,
                        'PreviousLoanDefaults': previous_loan_defaults,
                        'BankruptcyHistory': bankruptcy_history,
                        'EmploymentStatus': employment_status,
                        'AnnualIncome': annual_income,
                        'LoanAmount': loan_amount,
                        'LoanDuration': loan_duration,
                        'MonthlyIncome': monthly_income,
                        'TotalAssets': total_assets,
                        'NetWorth': net_worth
                    }
                    url = 'https://loan-approval-prediction-m59u.onrender.com/predict' 
                    try:
                        response = requests.post(url, json=data)
                        if response.status_code == 200:
                            result = response.json()
                            pred = result['LoanApproved']
                            if pred == 1:
                                st.markdown('<p class="success">Loan likely to be approved</p>', unsafe_allow_html=True)
                            else:
                                st.markdown('<p class="error">Loan not likely to be approved</p>', unsafe_allow_html=True)
                        else:
                            st.error(f'Error in prediction: {response.text}')
                    except requests.exceptions.RequestException as e:
                        st.error(f'Failed to connect to API: {str(e)}')
        with col2:
            if st.button("Reset Form"):
                st.session_state.form_state = {
                    'CreditScore': 600,
                    'DebtToIncomeRatio': 0.2,
                    'PreviousLoanDefaults': 0,
                    'BankruptcyHistory': 0,
                    'EmploymentStatus': 'Employed',
                    'AnnualIncome': 50000.0,
                    'LoanAmount': 10000.0,
                    'LoanDuration': 36,
                    'MonthlyIncome': 4166.67,
                    'TotalAssets': 50000.0,
                    'NetWorth': 40000.0
                }
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)