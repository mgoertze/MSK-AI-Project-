import streamlit as st
from groq import Groq
import json
import os

# --- API CONFIGURATION ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"
DATA_FILE = "cases.json"

# --- DEFAULT ANONYMIZED CASE LIBRARY ---
DEFAULT_CASE_LIBRARY = {
    "Neck": {
        "name": "Arthur",
        "region_label": "Neck",
        "forthcomingness": 3,
        "demeanor": "Guarded, holds head stiffly, hesitant to turn head quickly.",
        "chief_complaint": "Neck stiffness and radiating numbness down the left arm.",
        "history_present_illness": "Was rear-ended at a red light 2 weeks ago; neck felt sore that night, but sharp radiating pain down the arm started 4 days ago.",
        "location_pain": "Lower cervical spine radiating into the left shoulder blade and lateral forearm.",
        "onset_pain": "Initial soreness 2 weeks ago, severe nerve pain 4 days ago.",
        "type_pain": "Deep ache in neck; sharp, electric shock sensation extending into the arm.",
        "aggravating_factors": "Looking up, turning head to the left, prolonged desk work.",
        "easing_factors": "Resting head back against a high chair, gently supporting the left arm on a pillow.",
        "radiation": "Radiates down C6 dermatomal distribution to the thumb and index finger.",
        "red_flags": "Denies gait instability, denies clumsiness in hands or dropping objects frequently.",
        "social_history": "Accountant, spends 8-10 hours a day at a computer. Non-smoker.",
        "past_medical_history": "No prior cervical injuries or spinal conditions.",
        "diff_dx": "C6 Cervical Radiculopathy vs. Cervical Strain / Whiplash Associated Disorder vs. Thoracic Outlet Syndrome"
    },
    "Shoulder": {
        "name": "George",
        "region_label": "Shoulder",
        "forthcomingness": 3,
        "demeanor": "Frustrated, exhausted from poor sleep, holds right arm close to body.",
        "chief_complaint": "Deep aching right shoulder pain and weakness when lifting the arm.",
        "history_present_illness": "Gradual onset over 5 months after painting his house ceiling; felt a sudden sharp twinge 2 weeks ago while reaching into the backseat of his car.",
        "location_pain": "Anterolateral aspect of the right shoulder, deep to the deltoid.",
        "onset_pain": "Gradual onset 5 months ago, acute aggravation 2 weeks ago.",
        "type_pain": "Dull, heavy ache during the day; sharp catch when reaching overhead.",
        "aggravating_factors": "Reaching overhead, reaching behind back to put on a belt, sleeping on the right side.",
        "easing_factors": "Holding arm supported across stomach, heat packs, resting side-lying on the left side.",
        "radiation": "Pain spreads down the mid-deltoid muscle belly, does not cross the elbow.",
        "red_flags": "No unexplained weight loss, no history of cancer, no systemic night sweats.",
        "social_history": "Retired painter, active gardener. Enjoys woodworking.",
        "past_medical_history": "Hypertension, high cholesterol.",
        "diff_dx": "Supraspinatus Tendinopathy / Rotator Cuff Tear vs. Subacromial Impingement vs. Adhesive Capsulitis"
    },
    "Elbow": {
        "name": "David",
        "region_label": "Elbow",
        "forthcomingness": 3,
        "demeanor": "Irritated, impatient to return to recreational activities.",
        "chief_complaint": "Outer elbow pain and weak grip strength.",
        "history_present_illness": "Pain started 6 weeks ago after weekend spent clearing brush with manual shears and playing pickleball.",
        "location_pain": "Lateral epicondyle of the right elbow.",
        "onset_pain": "Insidious onset 6 weeks ago.",
        "type_pain": "Sharp burning sensation over lateral elbow, dull ache extending down forearm.",
        "aggravating_factors": "Gripping a coffee mug, shaking hands, opening jar lids, backhand strokes in pickleball.",
        "easing_factors": "Rest, ice application, avoiding heavy lifting or wringing actions.",
        "radiation": "Extends distally down the extensor muscle belly of the forearm toward the wrist.",
        "red_flags": "No joint locking, no swelling or redness, no warmth over the joint.",
        "social_history": "IT consultant, recreational pickleball player 3x a week.",
        "past_medical_history": "Mild asthma.",
        "diff_dx": "Lateral Epicondylalgia ('Tennis Elbow') vs. Radial Tunnel Syndrome vs. Cervical Spine Referral (C6)"
    },
    "Hand & Wrist": {
        "name": "Maya",
        "region_label": "Hand & Wrist",
        "forthcomingness": 3,
        "demeanor": "Anxious, frequently shakes hands out or rubs wrists during conversation.",
        "chief_complaint": "Tingling, numbness, and burning in the thumb and first two fingers.",
        "history_present_illness": "Began 3 months ago with occasional night numbness; now happens daily while typing and driving.",
        "location_pain": "Palmar aspect of wrist, thumb, index, and middle fingers.",
        "onset_pain": "Gradual development over 3 months.",
        "type_pain": "Prickling 'pins and needles', burning, occasional deep wrist ache.",
        "aggravating_factors": "Holding phone for extended periods, driving, typing, sleeping with wrists curled.",
        "easing_factors": "Shaking or flicking hands ('flick sign'), running warm water over hands, wearing temporary night splints.",
        "radiation": "Proximal pain into forearm occasionally, but main sensory symptoms are distal in fingers.",
        "red_flags": "No visible wasting of the thenar eminence yet, no sudden loss of hand motor function.",
        "social_history": "Graphic designer, mother of a 14-month-old toddler.",
        "past_medical_history": "Hypothyroidism (managed with levothyroxine), gestational diabetes during pregnancy.",
        "diff_dx": "Carpal Tunnel Syndrome vs. Pronator Teres Syndrome vs. Cervical Radiculopathy (C6/C7)"
    },
    "Spine": {
        "name": "Marcus",
        "region_label": "Spine",
        "forthcomingness": 3,
        "demeanor": "Stoic, worried about missing work, moves cautiously from sitting to standing.",
        "chief_complaint": "Lower back pain with numbness shooting down the right leg.",
        "history_present_illness": "Twisted awkwardly while lifting a heavy lumber crate 3 weeks ago; pain was immediate and worsened over 48 hours.",
        "location_pain": "Lumbosacral region extending into right buttock and lateral calf.",
        "onset_pain": "Sudden mechanical onset 3 weeks ago.",
        "type_pain": "Sharp toothache-like ache in lower back; electrical burning pain down leg.",
        "aggravating_factors": "Bending forward, sitting over 15 minutes, coughing, or sneezing.",
        "easing_factors": "Lying flat on back with knees propped up on pillows, short slow walks.",
        "radiation": "Radiates down posterior/lateral right leg to the lateral ankle.",
        "red_flags": "Denies bowel or bladder incontinence, denies saddle anesthesia (numbness in groin).",
        "social_history": "Construction foreman, sole earner for household. Non-smoker.",
        "past_medical_history": "Mild hypertension.",
        "diff_dx": "L5/S1 Lumbar Disc Herniation with Radiculopathy vs. Piriformis Syndrome vs. Lumbar Facet Arthropathy"
    },
    "Hip": {
        "name": "Rachel",
        "region_label": "Hip",
        "forthcomingness": 3,
        "demeanor": "Polite, limping slightly when walking into the room, rubs groin area when describing pain.",
        "chief_complaint": "Deep groin stiffness and difficulty tying shoes or putting on socks.",
        "history_present_illness": "Aching groinal stiffness has developed progressively over the past year; worsening stiffness in the morning.",
        "location_pain": "Anterior groin and deep anterior hip, occasionally spreading to anterior thigh.",
        "onset_pain": "Insidious progressive onset over 12 months.",
        "type_pain": "Dull, deep grinding ache and morning stiffness.",
        "aggravating_factors": "Weight-bearing after prolonged sitting, squatting, getting out of a car, putting on socks/shoes.",
        "easing_factors": "Gentle movement after warming up, warm showers, sitting in reclining chairs.",
        "radiation": "Refers down the anterior thigh toward the superior pole of the patella.",
        "red_flags": "No unexplained fevers, no night pain waking her up every night, no history of systemic corticosteroid use.",
        "social_history": "High school history teacher, avid walker.",
        "past_medical_history": "Post-menopausal, mild osteopenia.",
        "diff_dx": "Hip Osteoarthritis vs. Femoroacetabular Impingement (FAI) vs. Lumbar Spine L3 Referral"
    },
    "Knee": {
        "name": "Elena",
        "region_label": "Knee",
        "forthcomingness": 3,
        "demeanor": "Emotional, highly anxious about her athletic season, visibly guarding her left leg.",
        "chief_complaint": "Left knee pain, instability, and feeling of the joint 'giving way'.",
        "history_present_illness": "Pivoted quickly during a match yesterday, felt/heard a loud 'pop' followed by immediate instability.",
        "location_pain": "Deep inside the left knee joint.",
        "onset_pain": "Acute traumatic onset 24 hours ago.",
        "type_pain": "Throbbing, deep ache with sharp catch upon weight-bearing attempts.",
        "aggravating_factors": "Bearing weight, twisting, attempting full extension or flexion.",
        "easing_factors": "Ice, elevation, complete rest, non-weight-bearing with crutches.",
        "radiation": "Localized to joint line, no distal radiation.",
        "red_flags": "No fever, pedal pulses present and equal, sensation intact distally.",
        "social_history": "University soccer athlete.",
        "past_medical_history": "Prior right ankle sprain 2 years ago.",
        "diff_dx": "Acute ACL Tear vs. Medial Meniscus Tear vs. Patellar Subluxation"
    },
    "Ankle & Foot": {
        "name": "Lucas",
        "region_label": "Ankle & Foot",
        "forthcomingness": 3,
        "demeanor": "Frustrated, wincing during first few steps when getting up.",
        "chief_complaint": "Sharp heel pain when taking the first steps out of bed in the morning.",
        "history_present_illness": "Pain began 2 months ago after starting a new running program on pavement; initial steps every morning are agonizing.",
        "location_pain": "Plantar aspect of the heel, near the medial calcaneal tubercle.",
        "onset_pain": "Gradual onset over 8 weeks.",
        "type_pain": "Sharp stabbing pain initially, turns into a dull ache after walking for 10 minutes.",
        "aggravating_factors": "First steps in morning, standing after sitting, bare-foot walking on hard floors, running.",
        "easing_factors": "Moderate walking once warmed up, supportive arch footwear, rolling foot on a frozen water bottle.",
        "radiation": "Spreads slightly forward into the medial longitudinal arch.",
        "red_flags": "No calf swelling, no calf tenderness on palpation, no localized skin changes or warmth.",
        "social_history": "Store manager, stands 8 hours daily on concrete floors. Started marathon training.",
        "past_medical_history": "Overweight (BMI 28).",
        "diff_dx": "Plantar Fasciopathy ('Plantar Fasciitis') vs. Calcaneal Stress Fracture vs. Fat Pad Atrophy vs. Tarsal Tunnel Syndrome"
    }
}

# --- PERSISTENT DISK STORAGE FUNCTIONS ---
def load_cases_from_disk():
    """Reads cases from cases.json or creates file from baseline defaults if missing."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Ensure existing JSON data gets default forthcomingness value if missing
                for k in data:
                    if "forthcomingness" not in data[k]:
                        data[k]["forthcomingness"] = 3
                return data
        except Exception:
            return DEFAULT_CASE_LIBRARY
    else:
        save_cases_to_disk(DEFAULT_CASE_LIBRARY)
        return DEFAULT_CASE_LIBRARY

def save_cases_to_disk(case_data):
    """Writes updated case dictionary to cases.json file permanently."""
    with open(DATA_FILE, "w") as f:
        json.dump(case_data, f, indent=4)

# --- INITIAL APP STATE SETUP ---
if "ccid" not in st.session_state:
    st.session_state.ccid = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "case_library" not in st.session_state:
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
            "- Make the student probe deeply with specific follow-up questions to pull information out of you."
        )
    elif level == 2:
        return (
            "COMMUNICATION STYLE (LEVEL 2 - GUARDED / RESERVED):\n"
            "- Answer the exact question asked, but do not provide much additional context.\n"
            "- Require the student to ask precise questions to get clear clinical details."
        )
    elif level == 3:
        return (
            "COMMUNICATION STYLE (LEVEL 3 - BALANCED CLINICAL RESPONSIVENESS):\n"
            "- Answer questions naturally and realistically as a standard patient.\n"
            "- Share relevant details naturally when asked, but do not dump your whole history at once."
        )
    elif level == 4:
        return (
            "COMMUNICATION STYLE (LEVEL 4 - OPEN & VERBOSE):\n"
            "- Be very helpful and willing to share details.\n"
            "- When asked a question, comfortably elaborate on related symptoms, timeline, or concerns."
        )
    else:  # Level 5
        return (
            "COMMUNICATION STYLE (LEVEL 5 - GIVES ALL RELEVANT INFORMATION FREELY):\n"
            "- Be extremely open, talkative, and forthcoming.\n"
            "- When asked a broad or general question, freely share extensive details about your history, aggravating factors, and symptom onset without waiting for deep probing."
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
        f"- DO NOT reveal your diagnosis or explicit medical anatomical terms (like 'L5/S1' or 'ACL') unless describing what a previous doctor told you.\n"
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

# --- STAGE 2: NAVIGATION & ADMIN BACKDOOR SIDEBAR ---
st.sidebar.title("🩺 Control Center")
st.sidebar.markdown(f"**Active User ID:** `{st.session_state.ccid}`")

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
    st.session_state.differentials_submitted = False
    st.session_state.submitted_differentials = ["", "", ""]
    st.rerun()

# --- STAGE 3: ADMIN CASE EDITOR PAGE ---
if role == "Admin/Instructor Editor":
    st.title("🛠️ Admin Case Management Matrix")
    st.write("Edit case attributes below. Modifications are saved **permanently** to disk and take effect live for all students.")
    
    case_keys = list(st.session_state.case_library.keys())
    selected_key = st.selectbox(
        "Select Case to Customize (Faculty Region View):", 
        case_keys, 
        format_func=lambda k: f"{st.session_state.case_library[k]['name']} — [{st.session_state.case_library[k]['region_label']}]"
    )
    
    case_data = st.session_state.case_library[selected_key]
    
    st.markdown("---")
    
    with st.form("admin_case_form"):
        st.subheader(f"Editing Case: {case_data['name']} ({case_data['region_label']})")
        
        # --- NEW: PATIENT FORTHCOMINGNESS SLIDING SCALE ---
        st.markdown("### 🎚️ Patient Communication Style & Forthcomingness")
        e_forthcoming = st.slider(
            "Select how forthcoming the patient will be during history taking:",
            min_value=1,
            max_value=5,
            value=int(case_data.get("forthcomingness", 3)),
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
            e_diff = st.text_area("Differential Diagnosis Framework (Faculty Notes)", value=case_data.get("diff_dx", ""))
            
        save_submitted = st.form_submit_button("Save Case Updates Permanently", type="primary")
        
        if save_submitted:
            st.session_state.case_library[selected_key].update({
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
            st.success(f"Case details and forthcomingness level ({e_forthcoming}/5) for '{e_name}' permanently saved!")

    st.markdown("---")
    with st.expander("⚠️ Danger Zone: Revert to Factory Defaults"):
        st.write("If you want to erase all permanent admin edits and restore the original cases, click below.")
        if st.button("Reset All Cases to Default"):
            st.session_state.case_library = DEFAULT_CASE_LIBRARY.copy()
            save_cases_to_disk(DEFAULT_CASE_LIBRARY)
            st.success("All cases reset to original defaults!")
            st.rerun()

# --- STAGE 4: STUDENT CLINICAL SIMULATOR PAGE ---
else:
    st.title("🎓 Interactive Clinical Assessment")
    st.write("Complete a subjective history on the assigned patient. When you are ready to conclude the encounter, click **Input Differential Diagnoses** below.")
    
    case_keys = list(st.session_state.case_library.keys())
    chosen_key = st.selectbox(
        "Select Patient for Evaluation:", 
        case_keys,
        format_func=lambda k: f"Patient: {st.session_state.case_library[k]['name']}"
    )
    
    active_case = st.session_state.case_library[chosen_key]
    
    # Reset conversation and differential status if switching cases
    if "last_chosen_case" not in st.session_state or st.session_state.last_chosen_case != chosen_key:
        st.session_state.messages = []
        st.session_state.differentials_submitted = False
        st.session_state.submitted_differentials = ["", "", ""]
        st.session_state.last_chosen_case = chosen_key

    st.info(f"📋 **Current Active Case:** Patient {active_case['name']}")
    
    # Display Chat Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Check if encounter has been completed
    if st.session_state.differentials_submitted:
        st.success("🔒 **Encounter Completed:** You have submitted your differential diagnoses for this patient.")
        st.markdown("**Submitted Differential Diagnoses:**")
        for idx, dx in enumerate(st.session_state.submitted_differentials, 1):
            st.markdown(f"{idx}. {dx}")
    else:
        # Input Tray for standard chat
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
        
        # --- DIFFERENTIAL DIAGNOSES SUBMISSION DIALOG ---
        @st.dialog("Input Differential Diagnoses")
        def open_differential_modal():
            st.write("Enter your top 3 differential diagnoses for this patient encounter. Submitting will end the patient interaction.")
            with st.form("diff_submission_form"):
                dx1 = st.text_input("Differential Diagnosis 1 (Primary):", placeholder="e.g., C6 Cervical Radiculopathy")
                dx2 = st.text_input("Differential Diagnosis 2:", placeholder="e.g., Cervical Strain")
                dx3 = st.text_input("Differential Diagnosis 3:", placeholder="e.g., Thoracic Outlet Syndrome")
                
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
            export_string += f"Patient Name: {active_case['name']}\n"
            export_string += f"Encounter Status: {'COMPLETED' if st.session_state.differentials_submitted else 'IN PROGRESS'}\n"
            export_string += f"--------------------------------------------------\n\n"
            export_string += f"--- SUBJECTIVE HISTORY TRANSCRIPT ---\n\n"
            
            for line in st.session_state.messages:
                speaker = "STUDENT" if line["role"] == "user" else "PATIENT"
                export_string += f"[{speaker}]: {line['content']}\n\n"
            
            # Append Differential Diagnoses at the bottom of the transcript
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
                file_name=f"MSK_Assessment_{st.session_state.ccid}_Patient_{active_case['name']}.txt",
                mime="text/plain"
            )