import streamlit as st
from groq import Groq

# --- API CONFIGURATION ---
# Pulls directly from Streamlit Cloud Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"

# --- INITIAL APP STATE SETUP ---
if "ccid" not in st.session_state:
    st.session_state.ccid = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- COMPREHENSIVE CASE LIBRARY INITIALIZATION ---
if "case_library" not in st.session_state:
    st.session_state.case_library = {
        "Spine": {
            "name": "Marcus (Low Back)",
            "demeanor": "Stoic, anxious about losing work, slightly reluctant to move.",
            "chief_complaint": "Lower back pain with numbness shooting down the right leg.",
            "history_present_illness": "Twisted awkwardly while lifting a heavy lumber crate 3 weeks ago; pain was immediate and worsened over 48 hours.",
            "location_pain": "Lumbosacral region (L5/S1 area) extending into right buttock and lateral calf.",
            "onset_pain": "Sudden onset following mechanical load 3 weeks ago.",
            "type_pain": "Sharp, toothache-like ache in lower back; electrical/burning shooting pain down the leg.",
            "aggravating_factors": "Bending forward, sitting for more than 15 minutes, coughing, or sneezing.",
            "easing_factors": "Lying flat on back with knees propped up on pillows, walking short distances.",
            "radiation": "Radiates down the posterior/lateral aspect of the right leg down to the ankle.",
            "red_flags": "Denies bowel or bladder incontinence, denies saddle anesthesia (numbness in groin).",
            "social_history": "Works full-time as a construction foreman. Sole provider for family of four. Non-smoker.",
            "past_medical_history": "Mild hypertension (managed with diet), no prior back operations or severe injury history.",
            "diff_dx": "L5/S1 Lumbar Disc Herniation with Radiculopathy vs. Piriformis Syndrome vs. Lumbar Facet Arthropathy"
        },
        "Knee": {
            "name": "Elena (ACL)",
            "demeanor": "Emotional, highly anxious about her athletic scholarship, tearful when discussing sports.",
            "chief_complaint": "Left knee pain, severe instability, and swelling after pivoting.",
            "history_present_illness": "Pivoted quickly during a soccer match yesterday, felt/heard a loud 'pop' followed by immediate instability.",
            "location_pain": "Deep intra-articular left knee joint pain.",
            "onset_pain": "Acute onset 24 hours ago.",
            "type_pain": "Throbbing, deep ache with sharp pain upon weight-bearing attempts.",
            "aggravating_factors": "Bearing weight, twisting, attempting full extension or flexion.",
            "easing_factors": "Ice, elevation, complete rest, non-weight-bearing.",
            "radiation": "No distal radiation; localized around the anterior and medial joint line.",
            "red_flags": "No fever, no loss of sensation in foot, pedal pulses strong.",
            "social_history": "Division 1 university soccer athlete, second-year kinesiology student.",
            "past_medical_history": "Right ankle inversion sprain 2 years ago (fully recovered).",
            "diff_dx": "Acute ACL Tear vs. Medial Meniscus Tear vs. Patellar Subluxation"
        }
    }

# --- HELPER FUNCTION: COMPILE AI INSTRUCTIONS ---
def build_patient_instructions(c):
    return (
        f"You are a standardized patient named {c['name']} in a clinical simulation for medical students.\n"
        f"PATIENT DEMEANOR: {c['demeanor']}\n"
        f"CHIEF COMPLAINT: {c['chief_complaint']}\n"
        f"HISTORY OF PRESENT ILLNESS: {c['history_present_illness']}\n"
        f"LOCATION OF PAIN: {c['location_pain']}\n"
        f"ONSET OF PAIN: {c['onset_pain']}\n"
        f"TYPE OF PAIN: {c['type_pain']}\n"
        f"AGGRAVATING FACTORS: {c['aggravating_factors']}\n"
        f"EASING FACTORS: {c['easing_factors']}\n"
        f"RADIATION: {c['radiation']}\n"
        f"RED FLAG STATUS: {c['red_flags']}\n"
        f"SOCIAL HISTORY: {c['social_history']}\n"
        f"PAST MEDICAL HISTORY: {c['past_medical_history']}\n\n"
        f"INSTRUCTIONS FOR CHAT:\n"
        f"- Stay in character as {c['name']} at all times.\n"
        f"- Only reveal information if the student asks relevant clinical questions.\n"
        f"- Do not diagnose yourself or use overly complex medical terminology.\n"
        f"- Be concise and realistic in your conversational responses."
    )

# --- STAGE 1: CCID SECURITY GATE ---
if not st.session_state.ccid:
    st.title("🏥 MSK Clinical Assessment Simulator")
    st.write("Welcome to the clinical simulation suite. Enter your CCID badge number to begin.")
    
    ccid_input = st.text_input("Institutional CCID Number:", placeholder="e.g., MGOERTZ99")
    if st.button("Access Clinical Portal", type="primary"):
        if ccid_input.strip():
            st.session_state.ccid = ccid_input.strip()
            st.rerun()
        else:
            st.warning("A valid CCID sequence is mandatory.")
    st.stop()

# --- STAGE 2: NAVIGATION & ADMIN BACKDOOR SIDEBAR ---
st.sidebar.title("🩺 Control Center")
st.sidebar.markdown(f"**Active User ID:** `{st.session_state.ccid}`")

# Navigation options expand if admin is unlocked
nav_options = ["Student Portal"]
if st.session_state.is_admin:
    nav_options.append("Admin/Instructor Editor")

role = st.sidebar.radio("Navigation View:", nav_options)

st.sidebar.markdown("---")

# Backdoor Admin Login Section
if not st.session_state.is_admin:
    with st.sidebar.expander("🔑 Admin Access"):
        admin_pass = st.text_input("Enter Admin Password:", type="password")
        if st.button("Unlock Admin Mode"):
            if admin_pass == "admin":
                st.session_state.is_admin = True
                st.success("Admin access granted!")
                st.rerun()
            else:
                st.error("Incorrect password.")
else:
    st.sidebar.success("🔓 Admin Privileges Active")
    if st.sidebar.button("Lock Admin Access"):
        st.session_state.is_admin = False
        st.rerun()

if st.sidebar.button("Terminate Session (Logout)"):
    st.session_state.ccid = None
    st.session_state.is_admin = False
    st.session_state.messages = []
    st.rerun()

# --- STAGE 3: ADMIN CASE EDITOR PAGE ---
if role == "Admin/Instructor Editor":
    st.title("🛠️ Admin Case Management Matrix")
    st.write("Edit case attributes below. Modifications will take effect live for students.")
    
    selected_joint = st.selectbox("Select Case to Customize:", list(st.session_state.case_library.keys()))
    case_data = st.session_state.case_library[selected_joint]
    
    st.markdown("---")
    
    # 13 Granular Case Categories
    with st.form("admin_case_form"):
        st.subheader(f"Editing Case: {case_data['name']}")
        
        col1, col2 = st.columns(2)
        with col1:
            e_name = st.text_input("Patient Identifier Name", value=case_data.get("name", ""))
            e_demeanor = st.text_input("Patient Demeanor", value=case_data.get("demeanor", ""))
            e_chief = st.text_area("Chief Complaint", value=case_data.get("chief_complaint", ""))
            e_hpi = st.text_area("History of Presenting Illness (HPI)", value=case_data.get("history_present_illness", ""))
            e_loc = st.text_input("Location of Pain", value=case_data.get("location_pain", ""))
            e_onset = st.text_input("Onset of Pain", value=case_data.get("onset_pain", ""))
            e_type = st.text_input("Type / Quality of Pain", value=case_data.get("type_pain", ""))

        with col2:
            e_agg = st.text_area("Aggravating Factors", value=case_data.get("aggravating_factors", ""))
            e_ease = st.text_area("Easing Factors", value=case_data.get("easing_factors", ""))
            e_rad = st.text_input("Radiation Pattern", value=case_data.get("radiation", ""))
            e_red = st.text_area("Red Flag Symptoms Status", value=case_data.get("red_flags", ""))
            e_soc = st.text_area("Social History", value=case_data.get("social_history", ""))
            e_pmh = st.text_area("Past Medical History", value=case_data.get("past_medical_history", ""))
            e_diff = st.text_area("Differential Diagnosis Framework (Faculty Notes)", value=case_data.get("diff_dx", ""))
            
        save_submitted = st.form_submit_button("Save Case Updates Live", type="primary")
        
        if save_submitted:
            st.session_state.case_library[selected_joint] = {
                "name": e_name,
                "demeanor": e_demeanor,
                "chief_complaint": e_chief,
                "history_present_illness": e_hpi,
                "location_pain": e_loc,
                "onset_pain": e_onset,
                "type_pain": e_type,
                "aggravating_factors": e_agg,
                "easing_factors": e_ease,
                "radiation": e_rad,
                "red_flags": e_red,
                "social_history": e_soc,
                "past_medical_history": e_pmh,
                "diff_dx": e_diff
            }
            st.success(f"Case details for '{e_name}' successfully updated!")

# --- STAGE 4: STUDENT CLINICAL SIMULATOR PAGE ---
else:
    st.title("🎓 Interactive Clinical Assessment")
    st.write("Interview your standardized patient. Ask structured questions regarding their pain presentation, medical background, and lifestyle factors.")
    
    chosen_domain = st.selectbox("Assign Patient Structural Case Focus:", list(st.session_state.case_library.keys()))
    active_case = st.session_state.case_library[chosen_domain]
    
    # Clear conversation history if switching cases
    if "last_chosen_case" not in st.session_state or st.session_state.last_chosen_case != chosen_domain:
        st.session_state.messages = []
        st.session_state.last_chosen_case = chosen_domain

    st.info(f"📋 **Current Active Case:** {active_case['name']}")
    
    # Display Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input Tray
    if prompt := st.chat_input("Ask your patient an assessment question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                system_instruction = build_patient_instructions(active_case)
                
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=300
                )
                
                ai_text = completion.choices[0].message.content
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                
            except Exception as e:
                st.error(f"Groq API Error: {e}")

    # --- STAGE 5: TRANSCRIPT EXPORT ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Submission Records")
    if st.sidebar.button("Compile Transcript"):
        if not st.session_state.messages:
            st.sidebar.warning("No conversation recorded yet.")
        else:
            export_string = f"==================================================\n"
            export_string += f"OFFICIAL MSK CLINICAL SIMULATION EVALUATION RECORD\n"
            export_string += f"==================================================\n"
            export_string += f"Student CCID: {st.session_state.ccid}\n"
            export_string += f"Case Domain: {chosen_domain}\n"
            export_string += f"Patient Name: {active_case['name']}\n"
            export_string += f"--------------------------------------------------\n\n"
            
            for line in st.session_state.messages:
                speaker = "STUDENT" if line["role"] == "user" else "PATIENT"
                export_string += f"[{speaker}]: {line['content']}\n\n"
                
            st.sidebar.download_button(
                label="📥 Download Transcript (.txt)",
                data=export_string,
                file_name=f"MSK_Assessment_{st.session_state.ccid}_{chosen_domain}.txt",
                mime="text/plain"
            )