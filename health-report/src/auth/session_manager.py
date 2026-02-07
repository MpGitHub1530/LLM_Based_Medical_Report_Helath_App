import streamlit as st


class SessionManager:
    @staticmethod
    def init_session():
        """Initialize session with real authentication check"""
        # Create AuthService once
        if "auth_service" not in st.session_state:
            from auth.auth_service import AuthService
            st.session_state.auth_service = AuthService()
        
        # Check for existing authenticated user (don't auto-create)
        if "user" not in st.session_state:
            st.session_state.user = st.session_state.auth_service.get_user()

    @staticmethod
    def clear_session_state():
        """Clear all session state"""
        keys_to_keep = []
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]

    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        user = st.session_state.get("user")
        return user is not None and user.get("id") is not None

    @staticmethod
    def create_chat_session():
        """Create chat session - compatibility method"""
        return True, "local_session"

    @staticmethod
    def get_user_sessions():
        """Get user sessions - returns empty list"""
        return True, []

    @staticmethod
    def delete_session(session_id):
        """Delete session - compatibility method"""
        return True, "deleted"

    @staticmethod
    def logout():
        """Logout user and clear session"""
        if st.session_state.get("auth_service"):
            st.session_state.auth_service.sign_out()
        SessionManager.clear_session_state()

    @staticmethod
    def login(email, password):
        """Login with email and password"""
        if not st.session_state.get("auth_service"):
            SessionManager.init_session()
        
        success, result = st.session_state.auth_service.sign_in(email, password)
        
        if success:
            st.session_state.user = result
            return True, result
        else:
            return False, result
