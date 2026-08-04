import streamlit as st
from groq import Groq
import json
import os

# --- API CONFIGURATION ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"
DATA_FILE = "cases.json"

# --- DEFAULT ANONYMIZED CLINICAL LIBRARY (NO DIAGNOSES IN CASE BODY) ---
DEFAULT_CASE_LIBRARY = {
    "Cervical spine": {
        "Case 1": {
            "name": "Arthur", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Rubbing neck, sits slouched forward.",
            "chief_complaint": "Persistent ache across upper back and neck after long hours at computer.",
            "history_present_illness": "Dull ache developed over 3 months as work demands increased.",
            "location_pain": "Bilateral upper trapezius and mid-cervical paraspinals.",
            "onset_pain": "Insidious onset over 12 weeks.",
            "type_pain": "Constant heavy ache, muscular tightness.",
            "aggravating_factors": "Prolonged desk work, head-forward postures.",
            "easing_factors": "Heat packs, gentle stretching, lying down flat.",
            "radiation": "None into arms.",
            "red_flags": "Denies upper extremity numbness, weakness, or clumsiness.",
            "social_history": "Software developer, works 10-hour days.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Neck Pain (Postural Strain)"
        },
        "Case 2": {
            "name": "Beatrice", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Holds head slightly turned, hesitant to rotate quickly.",
            "chief_complaint": "Sharp catching pain when looking over right shoulder while driving.",
            "history_present_illness": "Woke up 4 days ago after sleeping in an awkward position with a stiff neck.",
            "location_pain": "Right unilateral upper neck region.",
            "onset_pain": "Acute onset upon waking 4 days ago.",
            "type_pain": "Sharp catch on rotation, dull localized ache at rest.",
            "aggravating_factors": "Right neck rotation and bending backwards.",
            "easing_factors": "Chin tucks, keeping neck neutral, gentle warmth.",
            "radiation": "Localized to upper scapular border.",
            "red_flags": "Neurological examination completely clear.",
            "social_history": "Graphic artist.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Neck Pain (Facet Dysfunction)"
        },
        "Case 3": {
            "name": "Charles", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Sits very upright, cautious with neck flexion.",
            "chief_complaint": "Deep central neck ache that worsens when looking down at phone.",
            "history_present_illness": "Gradual onset over 6 weeks after lifting heavy boxes in garage.",
            "location_pain": "Central lower neck.",
            "onset_pain": "Gradual progression over 6 weeks.",
            "type_pain": "Deep toothache-like ache.",
            "aggravating_factors": "Neck flexion, coughing, sitting without head support.",
            "easing_factors": "Resting head against high-back chair, chin retractions.",
            "radiation": "Interscapular pain between shoulder blades.",
            "red_flags": "No arm numbness or hand weakness.",
            "social_history": "Warehouse manager.",
            "past_medical_history": "Lower back strain 5 years ago.",
            "diff_dx": "Mechanical Neck Pain (Discogenic Non-Radicular)"
        },
        "Case 4": {
            "name": "Diana", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Holding arm on top of head for pain relief.",
            "chief_complaint": "Sharp shooting electric pain down left arm into thumb and index finger.",
            "history_present_illness": "Severe arm pain started 5 days ago after sudden head turn while exercising.",
            "location_pain": "Left neck radiating down arm to thumb and index finger.",
            "onset_pain": "Acute event 5 days ago.",
            "type_pain": "Sharp, burning, electric shock sensation.",
            "aggravating_factors": "Bending neck backward, tilting to left.",
            "easing_factors": "Placing left hand on top of head.",
            "radiation": "Down left arm into thumb and index finger.",
            "red_flags": "Mild weakness in biceps / wrist extension; no gait imbalance.",
            "social_history": "Accountant.",
            "past_medical_history": "Hypertension.",
            "diff_dx": "Cervical Radiculopathy"
        },
        "Case 5": {
            "name": "Ethan", "region_label": "Cervical spine", "forthcomingness": 2,
            "demeanor": "Anxious, manually supporting chin with hand.",
            "chief_complaint": "Feeling like head is heavy and unstable with tingling in lip and hands upon bending neck forward.",
            "history_present_illness": "Followed high-velocity jolting motion in car collision 2 weeks ago.",
            "location_pain": "Upper neck and back of head.",
            "onset_pain": "Acute post-trauma 14 days ago.",
            "type_pain": "Deep pressure accompanied by neurological sensations on flexion.",
            "aggravating_factors": "Bending neck forward, unexpected bumps in car.",
            "easing_factors": "Lying flat, supporting head firmly with hands.",
            "radiation": "Lip tingling and bilateral hand tingling.",
            "red_flags": "Electric shock down spine on bending neck forward; lip numbness.",
            "social_history": "College student.",
            "past_medical_history": "Rheumatoid Arthritis.",
            "diff_dx": "Transverse Ligament Instability"
        },
        "Case 6": {
            "name": "Fiona", "region_label": "Cervical spine", "forthcomingness": 2,
            "demeanor": "Elderly, cautious wide-based gait, clumsy holding pen.",
            "chief_complaint": "Progressive hand clumsiness, difficulty buttoning shirts, and feeling off-balance when walking.",
            "history_present_illness": "Symptoms worsening over 6 months; dropping keys frequently.",
            "location_pain": "Diffuse neck stiffness, global hand tingling.",
            "onset_pain": "Insidious progression over 6 months.",
            "type_pain": "Vague ache with functional clumsiness.",
            "aggravating_factors": "Walking on uneven ground, looking down.",
            "easing_factors": "Resting in supportive armchairs.",
            "radiation": "Bilateral hands and legs.",
            "red_flags": "Loss of fine manual dexterity, unsteadiness walking.",
            "social_history": "Retired school teacher.",
            "past_medical_history": "Longstanding neck wear and tear.",
            "diff_dx": "Cervical Myelopathy"
        }
    },
    "Lumbar spine": {
        "Case 1": {
            "name": "George", "region_label": "Lumbar spine", "forthcomingness": 4,
            "demeanor": "Moving slowly, holding lower back with both hands.",
            "chief_complaint": "Acute lower back muscle tightness after lifting heavy garden soil.",
            "history_present_illness": "Felt sudden back tightness 2 days ago while lifting.",
            "location_pain": "Lower back muscles on both sides.",
            "onset_pain": "Acute onset 48 hours ago.",
            "type_pain": "Tight throbbing muscle ache.",
            "aggravating_factors": "Bending forward, standing from sitting, twisting.",
            "easing_factors": "Lying flat with knees bent, ice packs.",
            "radiation": "None; stays in lower back.",
            "red_flags": "Normal leg strength and sensation.",
            "social_history": "Landscape designer.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Low Back Pain (Lumbar Strain)"
        },
        "Case 2": {
            "name": "Hannah", "region_label": "Lumbar spine", "forthcomingness": 3,
            "demeanor": "Stands slightly stooped forward to avoid arching back.",
            "chief_complaint": "Dull ache in low back worse when standing straight or arching back.",
            "history_present_illness": "Developing over 1 year; worse in mornings.",
            "location_pain": "Lower back and upper buttocks.",
            "onset_pain": "Gradual progressive onset.",
            "type_pain": "Dull localized joint ache.",
            "aggravating_factors": "Arching back, standing upright, prolonged walking.",
            "easing_factors": "Sitting bent forward, leaning forward over counter.",
            "radiation": "Upper buttock area.",
            "red_flags": "No nerve pain or weakness down legs.",
            "social_history": "Retired administrative clerk.",
            "past_medical_history": "Spinal joint wear and tear.",
            "diff_dx": "Mechanical Low Back Pain (Facet Arthropathy)"
        },
        "Case 3": {
            "name": "Ian", "region_label": "Lumbar spine", "forthcomingness": 3,
            "demeanor": "Prefers standing during interview; sitting causes groans.",
            "chief_complaint": "Deep central low back pain made agonizing by prolonged sitting.",
            "history_present_illness": "Felt a 'pop' in back 3 weeks ago while moving couch.",
            "location_pain": "Central lower back.",
            "onset_pain": "Subacute onset 3 weeks ago.",
            "type_pain": "Deep, pressure-like ache in low back.",
            "aggravating_factors": "Sitting, forward bending, coughing, sneezing.",
            "easing_factors": "Standing, walking, arching back gently while lying down.",
            "radiation": "Buttock region on both sides.",
            "red_flags": "No true shooting leg pain.",
            "social_history": "Office worker.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Low Back Pain (Discogenic)"
        },
        "Case 4": {
            "name": "Julia", "region_label": "Lumbar spine", "forthcomingness": 4,
            "demeanor": "Elderly, leaning forward over a walking frame.",
            "chief_complaint": "Bilateral leg aching and heaviness that forces sitting down after walking 5 minutes.",
            "history_present_illness": "Gradual progression over 2 years; can only shop using a grocery cart.",
            "location_pain": "Lower back radiating into back of both thighs and calves.",
            "onset_pain": "Insidious onset over 24 months.",
            "type_pain": "Heavy, cramping leg fatigue.",
            "aggravating_factors": "Walking upright, standing straight.",
            "easing_factors": "Sitting down, bending forward.",
            "radiation": "Both legs down to calves.",
            "red_flags": "Leg pulses normal; no bowel or bladder changes.",
            "social_history": "Retired librarian.",
            "past_medical_history": "Spinal narrowing.",
            "diff_dx": "Neurogenic Claudication / Lateral Foraminal Stenosis"
        },
        "Case 5": {
            "name": "Kevin", "region_label": "Lumbar spine", "forthcomingness": 3,
            "demeanor": "Anxious, guarding right leg.",
            "chief_complaint": "Sharp burning pain shooting down back of right leg to top of foot.",
            "history_present_illness": "Onset 10 days ago after heavy squatting at gym.",
            "location_pain": "Right buttock, outer thigh, and top of foot.",
            "onset_pain": "Acute event 10 days ago.",
            "type_pain": "Sharp, electric shock, burning pain.",
            "aggravating_factors": "Sitting, coughing, lifting leg straight up.",
            "easing_factors": "Lying flat with legs elevated on pillows.",
            "radiation": "Down leg into foot.",
            "red_flags": "Big toe weakness; no bowel or bladder changes.",
            "social_history": "Personal trainer.",
            "past_medical_history": "None.",
            "diff_dx": "Radiculopathy"
        },
        "Case 6": {
            "name": "Laura", "region_label": "Lumbar spine", "forthcomingness": 2,
            "demeanor": "Distressed, tearful, unable to sit comfortably.",
            "chief_complaint": "Sudden bilateral leg weakness, groin numbness, and loss of bowel and bladder control.",
            "history_present_illness": "Severe back pain for 1 week suddenly exploded into leg numbness and loss of toilet control 6 hours ago.",
            "location_pain": "Low back, both legs, and groin/saddle area.",
            "onset_pain": "Acute emergency onset 6 hours ago.",
            "type_pain": "Severe deep pain with profound numbness.",
            "aggravating_factors": "Any movement.",
            "easing_factors": "None.",
            "radiation": "Both legs and groin region.",
            "red_flags": "Numbness around groin, loss of bladder control, severe weakness in feet.",
            "social_history": "Teacher.",
            "past_medical_history": "Slipped disc in back.",
            "diff_dx": "Cauda Equina Syndrome"
        }
    }
}

# --- PERSISTENT DISK STORAGE FUNCTIONS ---
def load_cases_from_disk():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return data
        except Exception:
            return DEFAULT_CASE_LIBRARY
    else:
        save_cases_to_disk(DEFAULT_CASE_LIBRARY)
        return DEFAULT_CASE_LIBRARY

def save_cases_to_disk(case_data):
    with open(DATA_FILE, "w") as f:
        json.dump(case_data, f, indent=4)

# --- INITIAL APP STATE SETUP ---
if "ccid" not in st.session_state:
    st.session_state.ccid = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# Force load from default if cases.json contains obsolete data
st.session_state.case_library = load_cases_from_disk()

if "differentials_submitted" not in st.session_state:
    st.session_state.differentials_submitted = False
if "submitted_differentials" not in st.session_state:
    st.session_state.submitted_differentials = ["", "", ""]

# --- HELPER FUNCTION: COMPILE FORTHCOMINGNESS DIRECTIVE ---
def get_forthcomingness_instruction(level):
    level = int(level)
    if level == 1:
        return (
            "COMMUNICATION STYLE (LEVEL 1 - MAXIMAL PROBING REQUIRED):\n"
            "- Give VERY SHORT, brief, and reluctant answers (1-2 sentences maximum).\n"
            "- Do NOT elaborate or volunteer extra clinical details unless asked directly.\n"
            "- Make the student probe deeply with specific follow-up questions."
        )
    elif level == 2:
        return (
            "COMMUNICATION STYLE (LEVEL 2 - GUARDED / RESERVED):\n"
            "- Answer the exact question asked, but do not provide much additional context.\n"
            "- Require the student to ask precise questions."
        )
    elif level == 3:
        return (
            "COMMUNICATION STYLE (LEVEL 3 - BALANCED CLINICAL RESPONSIVENESS):\n"
            "- Answer questions naturally and realistically as a standard patient.\n"
            "- Share relevant details naturally when asked."
        )
    elif level == 4:
        return (
            "COMMUNICATION STYLE (LEVEL 4 - OPEN & VERBOSE):\n"
            "- Be very helpful and willing to share details.\n"
            "- Elaborate comfortably on related symptoms or concerns."
        )
    else:
        return (
            "COMMUNICATION STYLE (LEVEL 5 - GIVES ALL RELEVANT INFORMATION FREELY):\n"
            "- Be extremely open, talkative, and forthcoming.\n"
            "- Freely share extensive details about your history and symptom onset."
        )

# --- HELPER FUNCTION: COMPILE AI INSTRUCTIONS ---
def build_patient_instructions(c):
    forthcoming_text = get_forthcomingness_instruction(c.get("forthcomingness", 3))
    return (
        f"You are a standardized patient named {c['name']} in a clinical simulation for medical/physiotherapy students.\n"
        f"PATIENT DEMEANOR: {c['demeanor']}\n"
        f"{forthcoming_text}\n\n"
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
        f"- ABSOLUTE RULE: DO NOT reveal your medical diagnosis, medical terminology, or anatomical code to the student.\n"
        f"- Describe symptoms naturally in everyday layperson terms.\n"
        f"- Strictly adhere to your COMMUNICATION STYLE level specified above."
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

# --- STAGE 2: NAVIGATION & ADMIN SIDEBAR ---
st.sidebar.title("🩺 Control Center")
st.sidebar.markdown(f"**Active User ID:** `{st.session_state.ccid}`")

nav_options = ["Student Portal"]
if st.session_state.is_admin:
    nav_options.append("Admin/Instructor Editor")

role = st.sidebar.radio("Navigation View:", nav_options)
st.sidebar.markdown("---")

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
    st.session_state.differentials_submitted = False
    st.session_state.submitted_differentials = ["", "", ""]
    st.rerun()

# --- STAGE 3: ADMIN CASE EDITOR PAGE ---
if role == "Admin/Instructor Editor":
    st.title("🛠️ Admin Case Management Matrix")
    st.write("Select a joint domain and case to customize parameters.")
    
    cat_col, case_col = st.columns(2)
    with cat_col:
        selected_category = st.selectbox("1. Select Joint Domain:", list(st.session_state.case_library.keys()))
    with case_col:
        # STRICT DISPLAY: Case Number + Patient Name ONLY
        selected_case_key = st.selectbox(
            "2. Select Patient Case:", 
            list(st.session_state.case_library[selected_category].keys()),
            format_func=lambda k: f"{k} — Patient: {st.session_state.case_library[selected_category][k]['name']}"
        )
        
    case_data = st.session_state.case_library[selected_category][selected_case_key]
    
    st.markdown("---")
    
    with st.form("admin_case_form"):
        st.subheader(f"Editing {selected_case_key}: Patient {case_data['name']} ({selected_category})")
        
        st.markdown("### 🎚️ Patient Communication Style & Forthcomingness")
        e_forthcoming = st.slider(
            "Select how forthcoming the patient will be during history taking:",
            min_value=1, max_value=5, value=int(case_data.get("forthcomingness", 3)),
            help="1 = Short answers requiring maximal probing | 5 = Gives all relevant information freely"
        )
        
        forthcoming_labels = {
            1: "🔴 **Level 1:** Short answers requiring maximal probing",
            2: "🟠 **Level 2:** Guarded & reserved answers",
            3: "🟡 **Level 3:** Balanced clinical responsiveness (Default)",
            4: "🟢 **Level 4:** Open & verbose",
            5: "🔵 **Level 5:** Gives all relevant information freely"
        }
        st.markdown(forthcoming_labels[e_forthcoming])
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            e_name = st.text_input("Patient Identifier Name (Visible to Students)", value=case_data.get("name", ""))
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
            e_diff = st.text_input("Hidden Ground Truth Diagnosis (Faculty Master Key)", value=case_data.get("diff_dx", ""))
            
        save_submitted = st.form_submit_button("Save Case Updates Permanently", type="primary")
        
        if save_submitted:
            st.session_state.case_library[selected_category][selected_case_key].update({
                "name": e_name,
                "forthcomingness": e_forthcoming,
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
            })
            save_cases_to_disk(st.session_state.case_library)
            st.success(f"Case '{selected_case_key}' ({e_name}) saved!")

    st.markdown("---")
    with st.expander("⚠️ Danger Zone: Revert to Factory Defaults"):
        st.write("Reset all cases back to original baseline settings.")
        if st.button("Reset All Cases to Default"):
            st.session_state.case_library = DEFAULT_CASE_LIBRARY.copy()
            save_cases_to_disk(DEFAULT_CASE_LIBRARY)
            st.success("All cases reset to original defaults!")
            st.rerun()

# --- STAGE 4: STUDENT CLINICAL SIMULATOR PAGE ---
else:
    st.title("🎓 Interactive Clinical Assessment")
    st.write("Select a region and patient to begin taking a subjective history.")
    
    col_cat, col_case = st.columns(2)
    with col_cat:
        student_category = st.selectbox("Select Joint Category:", list(st.session_state.case_library.keys()))
    with col_case:
        # STRICT DISPLAY: Case Number + Patient Name ONLY
        student_case_key = st.selectbox(
            "Select Patient Case:", 
            list(st.session_state.case_library[student_category].keys()),
            format_func=lambda k: f"{k} — Patient: {st.session_state.case_library[student_category][k]['name']}"
        )
        
    active_case = st.session_state.case_library[student_category][student_case_key]
    
    unique_case_id = f"{student_category}_{student_case_key}"
    if "last_chosen_case_id" not in st.session_state or st.session_state.last_chosen_case_id != unique_case_id:
        st.session_state.messages = []
        st.session_state.differentials_submitted = False
        st.session_state.submitted_differentials = ["", "", ""]
        st.session_state.last_chosen_case_id = unique_case_id

    # STRICT HEADER DISPLAY: Case Identifier and Patient Name ONLY
    st.info(f"📋 **Active Encounter:** {student_category} ({student_case_key}) — Patient Name: **{active_case['name']}**")
    
    # Display Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if st.session_state.differentials_submitted:
        st.success("🔒 **Encounter Completed:** You have submitted your differential diagnoses for this patient.")
        st.markdown("**Submitted Differential Diagnoses:**")
        for idx, dx in enumerate(st.session_state.submitted_differentials, 1):
            st.markdown(f"{idx}. {dx}")
    else:
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

        st.markdown("---")
        
        @st.dialog("Input Differential Diagnoses")
        def open_differential_modal():
            st.write("Enter your top 3 differential diagnoses for this patient encounter. Submitting will end the patient interaction.")
            with st.form("diff_submission_form"):
                dx1 = st.text_input("Differential Diagnosis 1 (Primary):", placeholder="e.g., Primary Suspected Condition")
                dx2 = st.text_input("Differential Diagnosis 2:", placeholder="e.g., Secondary Alternative")
                dx3 = st.text_input("Differential Diagnosis 3:", placeholder="e.g., Tertiary Alternative")
                
                submitted = st.form_submit_button("Submit & End Encounter", type="primary")
                if submitted:
                    if not dx1.strip() or not dx2.strip() or not dx3.strip():
                        st.error("Please fill in all 3 differential diagnosis fields before submitting.")
                    else:
                        st.session_state.submitted_differentials = [dx1.strip(), dx2.strip(), dx3.strip()]
                        st.session_state.differentials_submitted = True
                        st.rerun()

        if st.button("🩺 Input Differential Diagnoses", type="secondary"):
            open_differential_modal()

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
            export_string += f"Joint Category: {student_category}\n"
            export_string += f"Case Identifier: {student_case_key}\n"
            export_string += f"Patient Name: {active_case['name']}\n"
            export_string += f"Encounter Status: {'COMPLETED' if st.session_state.differentials_submitted else 'IN PROGRESS'}\n"
            export_string += f"--------------------------------------------------\n\n"
            export_string += f"--- SUBJECTIVE HISTORY TRANSCRIPT ---\n\n"
            
            for line in st.session_state.messages:
                speaker = "STUDENT" if line["role"] == "user" else "PATIENT"
                export_string += f"[{speaker}]: {line['content']}\n\n"
            
            export_string += f"--------------------------------------------------\n"
            export_string += f"STUDENT SUBMITTED DIFFERENTIAL DIAGNOSES:\n"
            if st.session_state.differentials_submitted:
                for idx, dx in enumerate(st.session_state.submitted_differentials, 1):
                    export_string += f"  {idx}. {dx}\n"
            else:
                export_string += f"  [Encounter ended without submitting differential diagnoses]\n"
            export_string += f"==================================================\n"
                
            st.sidebar.download_button(
                label="📥 Download Transcript (.txt)",
                data=export_string,
                file_name=f"MSK_Assessment_{st.session_state.ccid}_{student_case_key}.txt",
                mime="text/plain"
            )