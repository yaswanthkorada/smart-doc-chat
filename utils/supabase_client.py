"""
Supabase Client Configuration
"""
import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    try:
        # Try to get from Streamlit secrets first (for deployed app)
        if hasattr(st, 'secrets') and 'supabase' in st.secrets:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
        else:
            # Fallback to environment variables (for local development)
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Supabase credentials not found! Please configure SUPABASE_URL and SUPABASE_KEY")
        
        return create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        raise

# Initialize global client
try:
    supabase: Client = get_supabase_client()
except Exception as e:
    print(f"Warning: Could not initialize Supabase client: {e}")
    supabase = None
