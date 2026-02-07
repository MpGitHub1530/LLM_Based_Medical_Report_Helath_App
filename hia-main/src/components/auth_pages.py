import streamlit as st
from auth.session_manager import SessionManager
from config.app_config import APP_ICON, APP_NAME, APP_TAGLINE, APP_DESCRIPTION
from utils.validators import validate_signup_fields
import time

def show_login_page():
    """Modern split-screen authentication page with gradient background"""
    
    # Initialize form type
    if 'form_type' not in st.session_state:
        st.session_state['form_type'] = 'login'
    
    current_form = st.session_state['form_type']
    
    # Custom CSS for modern design
    st.markdown("""
        <style>
        /* Hide Streamlit branding and sidebar */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Full page gradient background */
        .stApp {
            background: linear-gradient(135deg, #f5f1e8 0%, #faf8f3 50%, #ffffff 100%);
            background-attachment: fixed;
        }
        
        /* Hide form helper text */
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
        
        /* Custom input styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 12px 16px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        /* Glassmorphism card */
        .auth-card {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 3rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(200, 200, 200, 0.2);
        }
        
        .branding-panel {
            background: linear-gradient(135deg, rgba(139, 115, 85, 0.08) 0%, rgba(101, 67, 33, 0.08) 100%);
            border-radius: 24px;
            padding: 3rem;
            text-align: center;
        }
        
        .feature-item {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .feature-item:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main layout - single column centered
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Centered panel - Branding + Form
    with col2:
        # App branding
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 3rem;'>
                <h1 style='font-size: 5rem; margin-bottom: 0;'>{APP_ICON}</h1>
                <h1 style='color: #8b7355; font-size: 3.5rem; margin-top: 0.5rem; font-weight: 700;'>{APP_NAME}</h1>
                <p style='font-size: 1.5rem; color: #a0826d; margin-bottom: 1rem; font-weight: 500;'>{APP_TAGLINE}</p>
                <p style='font-size: 1.2rem; color: #988675; line-height: 1.8;'>{APP_DESCRIPTION}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Auth form card
        
        
        st.markdown(f"""
            <h2 style='text-align: center; color: #8b7355; margin-bottom: 0.5rem; font-size: 2.2rem; font-weight: 700;'>
                {'Welcome Back!' if current_form == 'login' else 'Create Account'}
            </h2>
            <p style='text-align: center; color: #a0826d; margin-bottom: 2rem; font-size: 1.1rem;'>
                {'Sign in to continue your health journey' if current_form == 'login' else 'Join us to start analyzing your health data'}
            </p>
        """, unsafe_allow_html=True)
        
        if current_form == 'login':
            show_login_form()
        else:
            show_signup_form()
        
        # Toggle between login/signup
        
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if current_form == 'login':
                if st.button("🆕 Create new account", use_container_width=True, type="secondary"):
                    st.session_state['form_type'] = 'signup'
                    st.rerun()
            else:
                if st.button("🔑 Already have an account?", use_container_width=True, type="secondary"):
                    st.session_state['form_type'] = 'login'
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def show_login_form():
    """Modern login form"""
    with st.form("login_form"):
        email = st.text_input("📧 Email Address", key="login_email", placeholder="you@example.com")
        password = st.text_input("🔒 Password", type="password", key="login_password", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("Sign In", type="primary"):
            if not email or not password:
                st.error("⚠️ Please enter both email and password")
                return
            
            with st.spinner("🔐 Authenticating..."):
                success, result = SessionManager.login(email, password)
                
                if success:
                    st.success("✅ Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Login failed: {result}")


def show_signup_form():
    """Modern signup form"""
    with st.form("signup_form"):
        new_name = st.text_input("👤 Full Name", key="signup_name", placeholder="John Doe")
        new_email = st.text_input("📧 Email Address", key="signup_email", placeholder="you@example.com")
        new_password = st.text_input("🔒 Password", type="password", key="signup_password", placeholder="Create a strong password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", key="signup_password2", placeholder="Re-enter your password")
        
        st.markdown("""
            <div style='background: #f0f4ff; padding: 1rem; border-radius: 12px; margin: 1rem 0;'>
                <p style='margin: 0; color: #667eea; font-size: 0.9rem;'><strong>Password must have:</strong></p>
                <p style='margin: 0.5rem 0 0 0; color: #666; font-size: 0.85rem;'>
                    ✓ At least 8 characters<br>
                    ✓ One uppercase letter<br>
                    ✓ One lowercase letter<br>
                    ✓ One number
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.form_submit_button("Create Account", type="primary"):
            validation_result = validate_signup_fields(
                new_name, new_email, new_password, confirm_password
            )
            
            if not validation_result[0]:
                st.error(f"⚠️ {validation_result[1]}")
                return
            
            with st.spinner("🚀 Creating your account..."):
                success, response = st.session_state.auth_service.sign_up(
                    new_email, new_password, new_name
                )
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = response
                    st.success("✅ Account created successfully! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Sign up failed: {response}")
