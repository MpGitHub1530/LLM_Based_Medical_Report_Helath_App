# 🔐 Setting Up Authentication

The app now supports **real Supabase authentication** with a beautiful modern UI!

## Quick Start

### Option 1: Use Demo Mode (No Setup Required)
The app will automatically run in demo mode if Supabase is not configured. You can use any email/password to "login" for testing.

### Option 2: Enable Real Authentication with Supabase

1. **Create a free Supabase account** at [supabase.com](https://supabase.com)

2. **Create a new project** in Supabase dashboard

3. **Get your credentials:**
   - Go to Project Settings → API
   - Copy your `Project URL`
   - Copy your `anon/public` key

4. **Configure your app:**
   
   Create or update `.streamlit/secrets.toml`:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key-here"
   GROQ_API_KEY = "your-groq-api-key"
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the app:**
   ```bash
   streamlit run src\main.py
   ```

## Features

✅ **Split-screen modern UI** with gradient backgrounds  
✅ **Glassmorphism design** for auth forms  
✅ **Real Supabase authentication** or demo mode fallback  
✅ **Secure password validation**  
✅ **Working logout functionality**  

## UI Preview

The new authentication page features:
- Purple-to-pink gradient background
- Split-screen layout (branding left, form right)
- Glassmorphism card design
- Smooth animations and transitions
- Completely different look from the original repo!
