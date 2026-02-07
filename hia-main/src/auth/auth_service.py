import streamlit as st
from supabase import create_client, Client

class AuthService:
    def __init__(self):
        """Initialize Supabase client for real authentication"""
        try:
            # Get Supabase credentials from Streamlit secrets
            supabase_url = st.secrets.get("SUPABASE_URL", "")
            supabase_key = st.secrets.get("SUPABASE_KEY", "")
            
            if supabase_url and supabase_key:
                self.supabase: Client = create_client(supabase_url, supabase_key)
                self.enabled = True
            else:
                # Fallback to demo mode if not configured
                self.supabase = None
                self.enabled = False
        except Exception as e:
            st.error(f"Failed to initialize Supabase: {str(e)}")
            self.supabase = None
            self.enabled = False

    def get_user(self):
        """Get current authenticated user"""
        if not self.enabled or not self.supabase:
            # Demo mode fallback
            if "local_user_id" not in st.session_state:
                return None
            return {"id": st.session_state.local_user_id, "email": None}
        
        try:
            # Get session from Supabase
            session = self.supabase.auth.get_session()
            if session and session.user:
                return {
                    "id": session.user.id,
                    "email": session.user.email,
                    "name": session.user.user_metadata.get("name")
                }
            return None
        except Exception:
            return None

    def sign_in(self, email: str, password: str):
        """Sign in with email and password"""
        if not self.enabled or not self.supabase:
            # Demo mode - accept any credentials
            user = {"id": "demo_user", "email": email, "name": "Demo User"}
            st.session_state.local_user_id = user["id"]
            st.session_state.user = user
            return True, user
        
        try:
            # Real Supabase authentication
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": response.user.user_metadata.get("name", "User")
                }
                st.session_state.user = user
                return True, user
            else:
                return False, "Invalid credentials"
        except Exception as e:
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                return False, "Invalid email or password"
            return False, f"Authentication error: {error_msg}"

    def sign_up(self, email: str, password: str, name: str):
        """Sign up new user"""
        if not self.enabled or not self.supabase:
            # Demo mode
            user = {"id": "demo_user", "email": email, "name": name}
            st.session_state.local_user_id = user["id"]
            st.session_state.user = user
            return True, user
        
        try:
            # Real Supabase signup
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if response.user:
                user = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": name
                }
                st.session_state.user = user
                return True, user
            else:
                return False, "Failed to create account"
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return False, "Email already registered"
            return False, f"Signup error: {error_msg}"

    def sign_out(self):
        """Sign out current user"""
        if self.enabled and self.supabase:
            try:
                self.supabase.auth.sign_out()
            except Exception:
                pass
        
        # Clear session state regardless
        if "user" in st.session_state:
            del st.session_state["user"]
        if "local_user_id" in st.session_state:
            del st.session_state["local_user_id"]
        if "auth_token" in st.session_state:
            del st.session_state["auth_token"]

    # Compatibility methods for existing code
    def validate_session_token(self):
        """Validate current session"""
        return self.get_user()

    def create_session(self, user_id):
        """Legacy method - not needed with Supabase Auth"""
        return True, "supabase_session"

    def get_user_sessions(self, user_id):
        """Get user sessions - returns empty for now"""
        return True, []

    def delete_session(self, session_id):
        """Delete session - not needed with Supabase Auth"""
        return True, "deleted"
