import streamlit as st
from groq import Groq

# --- API CONFIGURATION ---
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

# --- COMPREHENSIVE ANONYMIZED CASE LIBRARY INITIALIZATION ---
if "case_library" not in st.session_state:
    st.session_state.case_library = {
        "Neck": {
            "name": "Arthur",
            "region_label": "Neck",
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

# --- HELPER FUNCTION: COMPILE AI INSTRUCTIONS ---
def build_patient_instructions(c):
    return (
        f"You are a standardized patient named {c['name']} in a clinical simulation for medical/physiotherapy students.\n"
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
        f"- DO NOT reveal your diagnosis or explicit medical anatomical terms (like 'L5/S1' or 'ACL') unless describing what a previous doctor told you.\n"
        f"- Only reveal information if the student asks relevant clinical questions.\n"
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
    st.write("Edit case attributes below. Modifications take effect live for students.")
    
    # Format options for Admin to show region label
    case_keys = list(st.session_state.case_library.keys())
    selected_key = st.selectbox(
        "Select Case to Customize (Faculty Region View):", 
        case_keys, 
        format_func=lambda k: f"{st.session_state.case_library[k]['name']} — [{st.session_state.case_library[k]['region_label']}]"
    )
    
    case_data = st.session_state.case_library[selected_key]
    
    st.markdown("---")
    
    # 13 Granular Case Categories
    with st.form("admin_case_form"):
        st.subheader(f"Editing Case: {case_data['name']} ({case_data['region_label']})")
        
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
            
        save_submitted = st.form_submit_button("Save Case Updates Live", type="primary")
        
        if save_submitted:
            st.session_state.case_library[selected_key].update({
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
            })
            st.success(f"Case details for '{e_name}' successfully updated!")

# --- STAGE 4: STUDENT CLINICAL SIMULATOR PAGE ---
else:
    st.title("🎓 Interactive Clinical Assessment")
    st.write("Complete a subjective history on the assigned patient. When you believe you have completed your history type \"Differential diagnosis:__________.\" Compile your transcript and send it to your instructor.")
    
    # Dropdown displays ONLY the patient names to students
    case_keys = list(st.session_state.case_library.keys())
    chosen_key = st.selectbox(
        "Select Patient for Evaluation:", 
        case_keys,
        format_func=lambda k: f"Patient: {st.session_state.case_library[k]['name']}"
    )
    
    active_case = st.session_state.case_library[chosen_key]
    
    # Clear conversation history if switching cases
    if "last_chosen_case" not in st.session_state or st.session_state.last_chosen_case != chosen_key:
        st.session_state.messages = []
        st.session_state.last_chosen_case = chosen_key

    st.info(f"📋 **Current Active Case:** Patient {active_case['name']}")
    
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
            export_string += f"Patient Name: {active_case['name']}\n"
            export_string += f"--------------------------------------------------\n\n"
            
            for line in st.session_state.messages:
                speaker = "STUDENT" if line["role"] == "user" else "PATIENT"
                export_string += f"[{speaker}]: {line['content']}\n\n"
                
            st.sidebar.download_button(
                label="📥 Download Transcript (.txt)",
                data=export_string,
                file_name=f"MSK_Assessment_{st.session_state.ccid}_Patient_{active_case['name']}.txt",
                mime="text/plain"
            )