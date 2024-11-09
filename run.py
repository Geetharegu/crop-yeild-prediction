import streamlit as st
import pandas as pd
import joblib
import sqlite3
import hashlib
import numpy as np

# Set Streamlit theme
st.set_page_config(page_title="Crop Yield Prediction App", page_icon="🌾", layout="wide")
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #E6E6FA; /* Lavender Background */
    }
    .sidebar .sidebar-content {
        background-color: #D3D3D3; /* Light Grey Sidebar */
    }
    .stButton>button {
        background-color: #4A9CCB; /* Dark Lavender Buttons */
        color: white; /* White Button Text */
        border: None; /* Remove Button Border */
        transition: background-color 0.3s, transform 0.3s; /* Animation Effect */
        font-size: 24px; /* Increase button font size */
        padding: 15px; /* Increase button padding */
        margin: 10px 0; /* Add margin for spacing */
        border-radius: 5px; /* Add border radius for rounded corners */
    }
    .stButton>button:hover {
        background-color: #4A9CCB; /* Darker Lavender on Hover */
        transform: scale(1.05); /* Slightly enlarge on hover */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #003366; /* Deep Blue for Headings */
        transition: color 0.3s; /* Animation Effect */
    }
    .fade-in {
        animation: fadeIn 0.5s ease-in; /* Fade in effect */
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column; /* Align items in a column */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        email TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Add user to the database
def add_user(username, password, email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # User already exists
    finally:
        conn.close()

# Authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Load the XGBoost model
@st.cache_resource
def load_model():
    model = joblib.load('xgb_model1.joblib')
    return model

# Function to predict crop yield
def predict_crop_yield(input_data):
    model = load_model()
    prediction = model.predict(input_data)
    return prediction

# Function to provide recommendations based on crop yield
def get_recommendations(predicted_yield):
    recommendations = {}
    
    # Example thresholds for recommendations
    if predicted_yield < 2000:
        recommendations['Crop'] = "Low yield expected, consider increasing fertilizer and irrigation."
        recommendations['Fertilizer'] = "Use 100 kg/ha of Nitrogen and 50 kg/ha of Phosphorus."
        recommendations['Pesticide'] = "Use 5 L/ha of organic pesticide."
    elif 2000 <= predicted_yield < 5000:
        recommendations['Crop'] = "Moderate yield expected, optimal for medium crops."
        recommendations['Fertilizer'] = "Use 80 kg/ha of Nitrogen and 40 kg/ha of Phosphorus."
        recommendations['Pesticide'] = "Use 3 L/ha of integrated pest management."
    else:
        recommendations['Crop'] = "High yield expected, excellent for market value."
        recommendations['Fertilizer'] = "Use 60 kg/ha of Nitrogen and 30 kg/ha of Phosphorus."
        recommendations['Pesticide'] = "Use 2 L/ha of targeted pesticide."
    
    return recommendations

# Pages
def login_page():
    st.title("Welcome to Crop Yield Prediction App", anchor=None)
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)  # Start fade-in effect
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.page = "home"
        else:
            st.error("Invalid username or password")

    if st.button("Sign Up"):
        st.session_state.page = "signup"
    st.markdown('</div>', unsafe_allow_html=True)  # End fade-in effect

def signup_page():
    st.title("Sign Up", anchor=None)
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)  # Start fade-in effect
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    email = st.text_input("Email")

    if st.button("Register"):
        if add_user(username, password, email):
            st.success("Account created successfully. You can now log in.")
            st.session_state.page = "login"
        else:
            st.error("Username already exists. Please choose a different username.")
    st.markdown('</div>', unsafe_allow_html=True)  # End fade-in effect

def homepage():
    st.title("Welcome To Crop Yield Prediction 🌾", anchor=None)
    st.markdown('<div class="fade-in centered">', unsafe_allow_html=True)  # Start fade-in effect

    # Create a column layout for buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🌱 Predict Crop Yield"):
            st.session_state.page = "predictor"

    with col2:
        if st.button("💡 Get Recommendations"):
            st.session_state.page = "recommendations"

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

    st.markdown('</div>', unsafe_allow_html=True)  # End fade-in effect

def crop_yield_predictor():
    st.title("🌱 Crop Yield Predictor", anchor=None)
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)  # Start fade-in effect

    # Add a select box for crops
    crops = ["Wheat", "Rice", "Barley", "Maize", "Millet", "Sorghum", "Oats", "Rye"]
    selected_crop = st.selectbox("Select a crop:", options=crops)

    # Collect user input for prediction
    temperature = st.number_input("🌡️ Temperature (°C)", min_value=0.0, max_value=50.0, step=0.1)
    rainfall = st.number_input("🌧️ Rainfall (mm)", min_value=0.0, max_value=500.0, step=0.1)
    soil_ph = st.number_input("🌍 Soil pH", min_value=3.0, max_value=10.0, step=0.1)
    soil_moisture = st.number_input("💧 Soil Moisture (%)", min_value=0.0, max_value=100.0, step=0.1)
    previous_yield = st.number_input("📦 Previous Yield (kg)", min_value=0.0, max_value=10000.0, step=0.1)
    fertilizer_usage = st.number_input("💊 Fertilizer Usage (kg/ha)", min_value=0.0, max_value=1000.0, step=0.1)
    pesticide_usage = st.number_input("🧪 Pesticide Usage (L/ha)", min_value=0.0, max_value=100.0, step=0.1)

    # Prepare the input data for the model
    input_data = np.array([[temperature, rainfall, soil_ph, soil_moisture, previous_yield, fertilizer_usage, pesticide_usage]])

    # Button for making predictions
    if st.button("Predict"):
        # Make prediction
        predicted_yield = predict_crop_yield(input_data)
        st.session_state.predicted_yield = predicted_yield[0]
        st.success(f"Predicted Crop Yield for {selected_crop}: {predicted_yield[0]:.2f} kg/ha")

    # Back to home button
    if st.button("Back to Home"):
        st.session_state.page = "home"

    st.markdown('</div>', unsafe_allow_html=True)  # End fade-in effect

def recommendations_page():
    st.title("💡 Recommendations", anchor=None)
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)  # Start fade-in effect

    if 'predicted_yield' in st.session_state:
        recommendations = get_recommendations(st.session_state.predicted_yield)
        st.subheader("Recommendations")
        st.write(f"Recommended Crop Management Practices:")
        st.write(f"- Crop: {recommendations['Crop']}")
        st.write(f"- Fertilizer: {recommendations['Fertilizer']}")
        st.write(f"- Pesticide: {recommendations['Pesticide']}")
    else:
        st.error("No predictions available. Please go back to the predictor.")

    # Back to home button
    if st.button("Back to Home"):
        st.session_state.page = "home"

    st.markdown('</div>', unsafe_allow_html=True)  # End fade-in effect

# Main function to control the pages
def main():
    init_db()
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page()
    elif st.session_state.page == 'home' and st.session_state.logged_in:
        homepage()
    elif st.session_state.page == 'predictor':
        crop_yield_predictor()
    elif st.session_state.page == 'recommendations':
        recommendations_page()

if __name__ == "__main__":
    main()
