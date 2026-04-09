import streamlit as st
import google.generativeai as genai

# Setup API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- INITIAL STATE ---
if "ccid" not in st.session_state:
    st.session_state.ccid = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN GATE ---
if not st.session_state.ccid:
    st.title("🏥 MSK Clinical Simulator")
    ccid_input = st.text_input("Enter your Student/Instructor CCID to begin:")
    if st.button("Enter Clinic"):
        if ccid_input:
            st.session_state.ccid = ccid_input
            st.rerun()
        else:
            st.warning("Please enter a valid CCID.")
    st.stop()

# --- NAVIGATION ---
st.sidebar.title(f"User: {st.session_state.ccid}")
role = st.sidebar.radio("Select Role:", ["Student", "Instructor"])
if st.sidebar.button("Logout"):
    st.session_state.ccid = None
    st.rerun()

# --- INSTRUCTOR DASHBOARD ---
if role == "Instructor":
    st.title("🛠️ Case Management & Faculty Notes")
    
    case_to_edit = st.selectbox("Select Case to Modify:", ["Marcus (Spine)", "Elena (Knee)", "New Case..."])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Patient Persona")
        persona = st.text_area("Patient Background (AI Instructions)", 
                              value="Marcus, 42, stoic foreman, low back pain for 3 weeks...")
    
    with col2:
        st.subheader("Faculty Clinical Notes")
        subjective_notes = st.text_area("Subjective Key Findings")
        objective_notes = st.text_area("Objective Expectations (ROM/Tests)")
        diff_dx = st.text_area("Differential Diagnosis")

    if st.button("Save & Update Case"):
        st.success("Case updated! (Note: In this version, changes last as long as the app is running).")

# --- STUDENT CLINIC ---
else:
    st.title("🎓 Student Assessment")
    st.info(f"Student: {st.session_state.ccid} | Case: Marcus (Spine)")

    # Chat Display
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Begin your assessment..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            # The AI context uses the 'Instructor' persona logic
            context = "You are Marcus, a patient. Do not break character. Be concise."
            response = model.generate_content(f"{context}. Student asks: {prompt}")
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    # --- TRANSCRIPT EXPORT ---
    st.sidebar.divider()
    if st.sidebar.button("Generate Final Transcript"):
        transcript = f"Student CCID: {st.session_state.ccid}\n"
        transcript += "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        
        st.sidebar.download_button(
            label="Download Transcript for Instructor",
            data=transcript,
            file_name=f"Assessment_{st.session_state.ccid}.txt",
            mime="text/plain"
        )