import streamlit as st
import google.generativeai as genai

# Setup API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CASE LIBRARY ---
# You can add as many joints/cases here as you like!
CASES = {
    "Spine": {
        "name": "Marcus (Low Back)",
        "context": "You are Marcus, a 42yo foreman with lower back pain and sciatica. You are stoic and frustrated."
    },
    "Knee": {
        "name": "Elena (ACL)",
        "context": "You are Elena, a 19yo soccer player who heard a 'pop' in your knee. You are anxious about your scholarship."
    },
    "Shoulder": {
        "name": "George (Rotator Cuff)",
        "context": "You are George, a 65yo retired painter. Your shoulder aches at night and you can't reach the top shelf."
    }
}

# --- NAVIGATION ---
st.sidebar.title("Navigation")
role = st.sidebar.radio("Select Your Role:", ["Student", "Instructor"])

# --- INSTRUCTOR PAGE ---
if role == "Instructor":
    st.title("🛠️ Instructor Dashboard")
    st.subheader("Create or Modify a Patient")
    
    with st.form("patient_creator"):
        new_name = st.text_input("Patient Name & Primary Complaint")
        new_joint = st.selectbox("Joint", ["Spine", "Knee", "Shoulder", "Hip", "Ankle"])
        new_personality = st.text_area("Personality/Modifiers", placeholder="e.g. Grumpy, non-compliant, very talkative...")
        submitted = st.form_submit_button("Preview Patient")
        
        if submitted:
            st.info(f"Patient Logic Created: You are {new_name}. Joint: {new_joint}. Notes: {new_personality}")

# --- STUDENT PAGE ---
else:
    st.title("🎓 Student Clinic")
    
    # Selection of Case
    joint_choice = st.selectbox("Select Joint to Assess:", list(CASES.keys()))
    current_case = CASES[joint_choice]
    
    st.info(f"Currently Assessing: **{current_case['name']}**")
    
    # Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Start your subjective assessment..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Combine the base context with the student's question
            full_prompt = f"{current_case['context']} A student is interviewing you. Respond naturally. Question: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})