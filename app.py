Python
import streamlit as st
from groq import Groq

# Secure way for the cloud — pulls directly from Streamlit Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# Using Llama 3.1 8B Instant - the free-tier workhorse for handling fast requests
MODEL_NAME = "llama-3.1-8b-instant"

# --- INITIAL APP STATE SETUP ---
if "ccid" not in st.session_state:
    st.session_state.ccid = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- INSTRUCTOR WRITABLE DATA STATE ---
# We initialize standard cases. If an instructor updates them, it modifies session state.
if "case_library" not in st.session_state:
    st.session_state.case_library = {
        "Spine": {
            "name": "Marcus (Low Back)",
            "context": "You are Marcus, a 42-year-old construction foreman with sharp lower back pain and shooting numbness down your right leg (sciatica) for 3 weeks. You are stoic, deeply worried about missing work, and slightly reluctant to do exercises that 'make it pinch'. Give short, direct answers.",
            "sub_notes": "Patient presents with sharp L5/S1 localized pain. Aggravated by extension, eased by slight flexion.",
            "obj_notes": "Expected findings: Straight Leg Raise (SLR) positive on right at 45 degrees. Core stabilization weakness.",
            "diff_dx": "Lumbar Disc Herniation vs. Piriformis Syndrome vs. Lumbar Facet Arthropathy"
        },
        "Knee": {
            "name": "Elena (ACL)",
            "context": "You are Elena, a 19-year-old varsity soccer player who heard a loud 'pop' in your left knee during a pivoting maneuver yesterday. Your knee is swollen, you cannot put weight on it, and you are highly emotional and anxious about losing your athletic scholarship.",
            "sub_notes": "Acute trauma during non-contact deceleration and twist. Immediate swelling reported within 2 hours.",
            "obj_notes": "Expected findings: Positive Lachman test, positive Anterior Drawer. Significant effusion.",
            "diff_dx": "Acute ACL Tear vs. Medial Meniscus Tear vs. Patellar Subluxation"
        },
        "Shoulder": {
            "name": "George (Rotator Cuff)",
            "context": "You are George, a 65-year-old retired home painter. Your right dominant shoulder has been aching for 6 months, mostly at night when rolling onto it. You struggle to reach your arm up to put things in top cabinets.",
            "sub_notes": "Chronic, progressive anterolateral shoulder pain. History of repetitive overhead occupational strain.",
            "obj_notes": "Expected findings: Painful arc between 60-120 degrees elevation. Weakness in supraspinatus empty-can testing.",
            "diff_dx": "Supraspinatus Tendinopathy vs. Subacromial Impingement vs. Adhesive Capsulitis"
        }
    }

# --- STAGE 1: CCID SECURITY GATE ---
if not st.session_state.ccid:
    st.title("🏥 MSK Clinical Assessment Simulator")
    st.write("Welcome to the simulation environment. Please provide your institutional CCID badge number to initialize the patient clinic.")
    
    ccid_input = st.text_input("Institutional CCID Number:", placeholder="e.g., MGOERTZ99")
    if st.button("Access Clinical Portal", type="primary"):
        if ccid_input.strip():
            st.session_state.ccid = ccid_input.strip()
            st.rerun()
        else:
            st.warning("A valid CCID sequence is mandatory to initialize active server sessions.")
    st.stop()

# --- STAGE 2: MANAGEMENT SIDEBAR ---
st.sidebar.title("🩺 Control Center")
st.sidebar.markdown(f"**Active User ID:** `{st.session_state.ccid}`")
role = st.sidebar.radio("Navigation Role Profile:", ["Student Portal", "Instructor Dashboard"])

if st.sidebar.button("Terminate Session (Logout)", type="secondary"):
    st.session_state.ccid = None
    st.session_state.messages = []
    st.rerun()

# --- STAGE 3: INSTRUCTOR PROFILE ENGINE ---
if role == "Instructor Dashboard":
    st.title("🛠️ Faculty Portal & Live Case Compiler")
    st.write("Modify patient parameters, change physiological presentation text live, or view clinical reference notes.")
    
    selected_joint = st.selectbox("Select Active Structural Domain to Tweak:", list(st.session_state.case_library.keys()))
    case_data = st.session_state.case_library[selected_joint]
    
    st.markdown("---")
    
    # Text entry for modifying cases on the fly
    updated_name = st.text_input("Patient Identifier Name", value=case_data["name"])
    updated_context = st.text_area("Patient Psychological Profile & AI Context Boundary", value=case_data["context"], height=150)
    
    st.subheader("📋 Faculty Reference Matrix")
    updated_sub = st.text_area("Subjective Anamnesis / Key Milestones", value=case_data["sub_notes"])
    updated_obj = st.text_area("Expected Objective Inspection Targets", value=case_data["obj_notes"])
    updated_dx = st.text_area("Differential Diagnosis Frameworks", value=case_data["diff_dx"])
    
    if st.button("Push Framework Updates Live", type="primary"):
        st.session_state.case_library[selected_joint] = {
            "name": updated_name,
            "context": updated_context,
            "sub_notes": updated_sub,
            "obj_notes": updated_obj,
            "diff_dx": updated_dx
        }
        st.success(f"System Matrix for '{updated_name}' updated successfully! Changes are live across the active instance.")

# --- STAGE 4: STUDENT CLINICAL SIMULATOR ---
else:
    st.title("🎓 Interactive Clinical Placement Arena")
    st.write("Conduct an anamnesis (subjective assessment) below. Ask specific questions about mechanisms of injury, lifestyle, patterns, and pain characteristics to narrow down your diagnostic directions.")
    
    # Active Selection
    chosen_domain = st.selectbox("Assign Patient Structural Case Focus:", list(st.session_state.case_library.keys()))
    active_case = st.session_state.case_library[chosen_domain]
    
    # Clear history if switching cases to avoid conversation pollution
    if "last_chosen_case" not in st.session_state or st.session_state.last_chosen_case != chosen_domain:
        st.session_state.messages = []
        st.session_state.last_chosen_case = chosen_domain

    st.info(f"📋 **Current Evaluation Scope:** {active_case['name']} — Speak directly to the patient using the input tray below.")
    
    # Render historical layout logs
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat Actions Block
    if prompt := st.chat_input("Ask your patient an assessment question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                # System execution instruction structure for Groq API
                system_instruction = f"{active_case['context']} You are speaking directly to a clinician student checking your case. Maintain professional accuracy as a patient, do not step outside character, and do not simulate an instructor role."
                
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=250
                )
                
                ai_text = completion.choices[0].message.content
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                
            except Exception as e:
                st.error(f"Groq Cloud Transfer Failure: {e}")

    # --- STAGE 5: SYSTEM TRANSCRIPT EXTRACTION ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Class Assignment Delivery")
    if st.sidebar.button("Compile Active Evaluation Records"):
        if len(st.session_state.messages) == 0:
            st.sidebar.warning("Conversation tracking pipeline is empty. Initiate active dialog lines before exporting records.")
        else:
            # Build a neat readable transcript string
            export_string = f"==================================================\n"
            export_string += f"OFFICIAL MSK CLINICAL SIMULATION EVALUATION RECORD\n"
            export_string += f"==================================================\n"
            export_string += f"Student Identity CCID: {st.session_state.ccid}\n"
            export_string += f"Evaluated System Arena: {chosen_domain} Case\n"
            export_string += f"Patient Configuration: {active_case['name']}\n"
            export_string += f"--------------------------------------------------\n\n"
            
            for line in st.session_state.messages:
                speaker = "STUDENT" if line["role"] == "user" else "PATIENT"
                export_string += f"[{speaker}]: {line['content']}\n\n"
                
            st.sidebar.download_button(
                label="📥 Download Submission Text File",
                data=export_string,
                file_name=f"MSK_Assessment_CCID_{st.session_state.ccid}_{chosen_domain}.txt",
                mime="text/plain"
            )
            st.sidebar.success("Transcript compiled successfully. Provide this file to your supervisor for analysis.")