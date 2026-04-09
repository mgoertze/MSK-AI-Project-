import streamlit as st
import google.generativeai as genai

# Setup
API_KEY = "AIzaSyC7VJBfPEIOQYYiH4qcj2rmVTQqRC2Q364"
genai.configure(api_key=API_KEY)

# This part automatically finds a working model for you
try:
    # Look for any available Gemini models
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Pick the best one (preferring 2.0 or 1.5 if they exist)
    model_name = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
    model = genai.GenerativeModel(model_name)
except Exception as e:
    st.error(f"Could not find a model: {e}")
    model = None

st.title("🏥 Marcus Simulation")

if prompt := st.chat_input("Ask Marcus..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        if model:
            try:
                # Direct call to the model
                response = model.generate_content(f"You are Marcus, a patient with back pain. Question: {prompt}")
                st.write(response.text)
            except Exception as e:
                st.error(f"API Error: {e}")
        else:
            st.error("Model not initialized. Check your API key permissions.")