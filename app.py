import streamlit as st
import pandas as pd
from groq import Groq
import json
import os

# --- API CONFIGURATION ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_NAME = "llama-3.1-8b-instant"
DATA_FILE = "cases.json"

OBJECTIVE_CATEGORIES = [
    "Observation",
    "Active Range of Motion (AROM)",
    "Passive Range of Motion (PROM)",
    "Strength / Resisted Isometrics",
    "Functional Testing",
    "Palpation",
    "Special Tests"
]

# --- DEFAULT OBJECTIVE FINDINGS TEMPLATE ---
def get_default_objective_template():
    return {
        "Observation": "Postural alignment: Guarded position. Slight asymmetry noted on affected side.",
        "Active Range of Motion (AROM)": "Flexion: 75% available with pain at end-range. Extension: Full, pain-free. Lateral movements: Mildly restricted.",
        "Passive Range of Motion (PROM)": "Flexion: Full range with tissue-stretch end-feel and mild discomfort. Extension: Unrestricted.",
        "Strength / Resisted Isometrics": "Primary movers: 4/5 with pain elicited on strong contraction. Surrounding stabilizers: 5/5 non-tender.",
        "Functional Testing": "Single-leg balance: Stable. Deep squat / overhead reach: Reproduces primary complaint at 80% depth.",
        "Palpation": "Point tenderness noted over local tendinous insertion. Surrounding muscular hypertonicity present.",
        "Special Tests": "Primary provocative test: Positive. Secondary stability tests: Negative."
    }

# --- DEFAULT FULL CASE LIBRARY ---
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
            "diff_dx": "Mechanical Neck Pain (Postural Strain)",
            "objective_data": {
                "Observation": "Forward head posture, protracted scapulae, hypertonic upper trapezius muscles.",
                "Active Range of Motion (AROM)": "Flexion: Full, mild ache. Extension: Full, pain-free. Rotation (B/L): Restricted 15% end-range tight.",
                "Passive Range of Motion (PROM)": "Full in all planes with muscle-tightness end-feel in flexion.",
                "Strength / Resisted Isometrics": "Cervical flexors: 4/5. Cervical extensors: 5/5. Scapular retractors: 4-/5.",
                "Functional Testing": "Sustained neck flexion (desk posture simulation): Reproduces familiar ache at 2 minutes.",
                "Palpation": "Bilateral upper trapezius and levator scapulae hypertonicity with active trigger points.",
                "Special Tests": "Spurling Test: Negative. Cervical Distraction: Relieves tightness. Upper Limb Tension Tests: Negative."
            }
        }
    }
}

# Add default objective structure to fallback cases dynamically
for region, cases in DEFAULT_CASE_LIBRARY.items():
    for case_key, cdata in cases.items():
        if "objective_data" not in cdata:
            cdata["objective_data"] = get_default_objective_template()

# --- DISK STORAGE FUNCTIONS ---
def save_cases_to_disk(case_data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(case_data, f, indent=4)
    except Exception:
        pass

def load_cases_from_disk():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            
            for region, cases in data.items():
                for case_key, cdata in cases.items():
                    if "objective_data" not in cdata:
                        cdata["objective_data"] = get_default_objective_template()
                    else:
                        for cat in OBJECTIVE_CATEGORIES:
                            if cat not in cdata["objective_data"]:
                                cdata["objective_data"][cat] = "No findings recorded."
            return data
        except Exception:
            save_cases_to_disk(DEFAULT_CASE_LIBRARY)
            return DEFAULT_CASE_LIBRARY
    else:
        save_cases_to_disk(DEFAULT_CASE_LIBRARY)
        return DEFAULT_CASE_LIBRARY

# --- SESSION STATE INITIALIZATION ---
if "ccid" not in st.session_state:
    st.session_state.ccid = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "case_library" not in st.session_state:
    st.session_state.case_library = load_cases_from_disk()

if "encounter_phase" not in st.session_state:
    st.session_state.encounter_phase = 1
if "subjective_messages" not in st.session_state:
    st.session_state.subjective_messages = []
if "objective_tests" not in st.session_state:
    st.session_state.objective_tests = []
if "initial_differentials" not in st.session_state:
    st.session_state.initial_differentials = ["", "", ""]

# Phase 3 Structured Inputs State
if "tx_final_dx" not in st.session_state:
    st.session_state.tx_final_dx = ""
if "tx_education" not in st.session_state:
    st.session_state.tx_education = ""
if "tx_pain_mgmt" not in st.session_state:
    st.session_state.tx_pain_mgmt = ""
if "tx_mobility" not in st.session_state:
    st.session_state.tx_mobility = ""
if "tx_strength" not in st.session_state:
    st.session_state.tx_strength = ""

# --- HELPER FUNCTIONS ---
def get_forthcomingness_instruction(level):
    level = int(level)
    if level == 1:
        return "COMMUNICATION STYLE: Very short, reluctant answers (1-2 sentences)."
    elif level == 2:
        return "COMMUNICATION STYLE: Answer exact questions asked without extra detail."
    elif level == 3:
        return "COMMUNICATION STYLE: Answer questions naturally as a realistic patient."
    elif level == 4:
        return "COMMUNICATION STYLE: Open and verbose; share related details comfortably."
    else:
        return "COMMUNICATION STYLE: Extremely open; freely share extensive personal details."

def build_patient_instructions(c):
    return (
        f"You are a standardized patient named {c['name']} in a medical simulation.\n"
        f"PATIENT DEMEANOR: {c['demeanor']}\n"
        f"{get_forthcomingness_instruction(c.get('forthcomingness', 3))}\n\n"
        f"CHIEF COMPLAINT: {c['chief_complaint']}\n"
        f"HPI: {c['history_present_illness']}\n"
        f"LOCATION: {c['location_pain']}\n"
        f"ONSET: {c['onset_pain']}\n"
        f"TYPE: {c['type_pain']}\n"
        f"AGGRAVATING: {c['aggravating_factors']}\n"
        f"EASING: {c['easing_factors']}\n"
        f"RADIATION: {c['radiation']}\n"
        f"RED FLAGS: {c['red_flags']}\n"
        f"SOCIAL: {c['social_history']}\n"
        f"PMH: {c['past_medical_history']}\n\n"
        f"INSTRUCTIONS:\n"
        f"- Stay in character as {c['name']}.\n"
        f"- Never state your diagnosis or medical jargon directly."
    )

# --- STAGE 1: CCID SECURITY GATE ---
if not st.session_state.ccid:
    st.title("🏥 MSK Clinical Assessment Simulator")
    st.write("Enter your CCID badge number to start your clinical simulation.")
    ccid_input = st.text_input("Institutional CCID Number:", placeholder="e.g., MGOERTZ99")
    if st.button("Access Clinical Portal", type="primary"):
        if ccid_input.strip():
            st.session_state.ccid = ccid_input.strip()
            st.rerun()
        else:
            st.warning("A valid CCID sequence is mandatory.")
    st.stop()

# --- STAGE 2: NAVIGATION & SIDEBAR ---
st.sidebar.title("🩺 Control Center")
st.sidebar.markdown(f"**Active User:** `{st.session_state.ccid}`")

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
    st.sidebar.success("🔓 Admin Mode Active")
    if st.sidebar.button("Lock Admin Access"):
        st.session_state.is_admin = False
        st.rerun()

if st.sidebar.button("Terminate Session"):
    st.session_state.ccid = None
    st.session_state.is_admin = False
    st.session_state.encounter_phase = 1
    st.session_state.subjective_messages = []
    st.session_state.objective_tests = []
    st.session_state.initial_differentials = ["", "", ""]
    st.session_state.tx_final_dx = ""
    st.session_state.tx_education = ""
    st.session_state.tx_pain_mgmt = ""
    st.session_state.tx_mobility = ""
    st.session_state.tx_strength = ""
    st.rerun()

# --- STAGE 3: ADMIN CASE EDITOR ---
if role == "Admin/Instructor Editor":
    st.title("🛠️ Admin Case Management Matrix")
    
    cat_col, case_col = st.columns(2)
    with cat_col:
        selected_category = st.selectbox("1. Select Joint Domain:", list(st.session_state.case_library.keys()))
    with case_col:
        selected_case_key = st.selectbox(
            "2. Select Patient Case:", 
            list(st.session_state.case_library[selected_category].keys()),
            format_func=lambda k: f"{k} — Patient: {st.session_state.case_library[selected_category][k]['name']}"
        )
        
    case_data = st.session_state.case_library[selected_category][selected_case_key]
    if "objective_data" not in case_data:
        case_data["objective_data"] = get_default_objective_template()

    st.markdown("---")
    
    with st.form("admin_case_form"):
        st.subheader(f"Editing {selected_case_key}: Patient {case_data['name']} ({selected_category})")
        
        tab1, tab2 = st.tabs(["🗣️ Subjective Case Parameters", "📊 Objective Test Matrix"])
        
        with tab1:
            e_forthcoming = st.slider("Patient Forthcomingness (1-5):", 1, 5, int(case_data.get("forthcomingness", 3)))
            col1, col2 = st.columns(2)
            with col1:
                e_name = st.text_input("Patient Name", value=case_data.get("name", ""))
                e_demeanor = st.text_input("Demeanor", value=case_data.get("demeanor", ""))
                e_chief = st.text_area("Chief Complaint", value=case_data.get("chief_complaint", ""))
                e_hpi = st.text_area("HPI", value=case_data.get("history_present_illness", ""))
                e_loc = st.text_input("Location", value=case_data.get("location_pain", ""))
                e_onset = st.text_input("Onset", value=case_data.get("onset_pain", ""))
                e_type = st.text_input("Type", value=case_data.get("type_pain", ""))
            with col2:
                e_agg = st.text_area("Aggravating Factors", value=case_data.get("aggravating_factors", ""))
                e_ease = st.text_area("Easing Factors", value=case_data.get("easing_factors", ""))
                e_rad = st.text_input("Radiation", value=case_data.get("radiation", ""))
                e_red = st.text_area("Red Flags", value=case_data.get("red_flags", ""))
                e_soc = st.text_area("Social History", value=case_data.get("social_history", ""))
                e_pmh = st.text_area("Past Medical History", value=case_data.get("past_medical_history", ""))
                e_diff = st.text_input("Master Diagnosis Key", value=case_data.get("diff_dx", ""))

        with tab2:
            st.markdown("### Edit Objective Category Chart Values")
            st.caption("These findings populate the physical exam chart when students select these categories.")
            
            edited_objective_data = {}
            for cat in OBJECTIVE_CATEGORIES:
                current_val = case_data["objective_data"].get(cat, "")
                edited_objective_data[cat] = st.text_area(f"📌 {cat}", value=current_val, height=80)

        save_submitted = st.form_submit_button("Save Case Settings & Objective Matrix", type="primary")
        
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
                "diff_dx": e_diff,
                "objective_data": edited_objective_data
            })
            save_cases_to_disk(st.session_state.case_library)
            st.success(f"Case '{selected_case_key}' ({e_name}) objective matrix saved!")

# --- STAGE 4: STUDENT 3-PHASE CLINICAL SIMULATOR ---
else:
    st.title("🎓 Interactive 3-Phase Clinical Assessment")
    
    col_cat, col_case = st.columns(2)
    with col_cat:
        student_category = st.selectbox("Select Joint Category:", list(st.session_state.case_library.keys()))
    with col_case:
        student_case_key = st.selectbox(
            "Select Patient Case:", 
            list(st.session_state.case_library[student_category].keys()),
            format_func=lambda k: f"{k} — Patient: {st.session_state.case_library[student_category][k]['name']}"
        )
        
    active_case = st.session_state.case_library[student_category][student_case_key]
    if "objective_data" not in active_case:
        active_case["objective_data"] = get_default_objective_template()

    unique_case_id = f"{student_category}_{student_case_key}"
    if "last_chosen_case_id" not in st.session_state or st.session_state.last_chosen_case_id != unique_case_id:
        st.session_state.subjective_messages = []
        st.session_state.objective_tests = []
        st.session_state.encounter_phase = 1
        st.session_state.initial_differentials = ["", "", ""]
        st.session_state.tx_final_dx = ""
        st.session_state.tx_education = ""
        st.session_state.tx_pain_mgmt = ""
        st.session_state.tx_mobility = ""
        st.session_state.tx_strength = ""
        st.session_state.last_chosen_case_id = unique_case_id

    st.info(f"📋 **Active Encounter:** {student_category} ({student_case_key}) — Patient: **{active_case['name']}**")

    # ENCOUNTER PROGRESS BAR
    phase_names = {
        1: "Phase 1: Subjective History",
        2: "Phase 2: Objective Physical Exam",
        3: "Phase 3: Treatment & Management Plan",
        4: "Encounter Complete"
    }
    progress_val = {1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}[st.session_state.encounter_phase]
    st.progress(progress_val, text=f"**Current Status:** {phase_names[st.session_state.encounter_phase]}")
    st.markdown("---")

    # ==========================================
    # PHASE 1: SUBJECTIVE HISTORY
    # ==========================================
    if st.session_state.encounter_phase == 1:
        st.subheader("🗣️ Phase 1: Subjective History Taking")
        
        for msg in st.session_state.subjective_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask your patient a subjective history question..."):
            st.session_state.subjective_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                if not client:
                    st.error("GROQ_API_KEY missing from secrets.")
                else:
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
                        st.session_state.subjective_messages.append({"role": "assistant", "content": ai_text})
                    except Exception as e:
                        st.error(f"Groq API Error: {e}")

        st.markdown("---")
        
        @st.dialog("Submit Initial Differential Diagnoses")
        def open_phase1_dialog():
            st.write("Enter your top 3 differential diagnoses based on the subjective history to unlock Phase 2.")
            with st.form("phase1_diff_form"):
                dx1 = st.text_input("Primary Suspected Differential:", placeholder="e.g., Postural Strain")
                dx2 = st.text_input("Secondary Differential:", placeholder="e.g., Facet Joint Dysfunction")
                dx3 = st.text_input("Tertiary Differential:", placeholder="e.g., Discogenic Radiculopathy")
                
                if st.form_submit_button("Submit & Proceed to Objective Exam", type="primary"):
                    if not dx1.strip() or not dx2.strip() or not dx3.strip():
                        st.error("Please fill in all 3 differential fields before proceeding.")
                    else:
                        st.session_state.initial_differentials = [dx1.strip(), dx2.strip(), dx3.strip()]
                        st.session_state.encounter_phase = 2
                        st.rerun()

        # HIGH VISIBILITY PROGRESSION BUTTON
        if st.button("➡️ Move on to Objective Exam", type="primary", use_container_width=True):
            if not st.session_state.subjective_messages:
                st.warning("Please ask at least one subjective history question before moving on.")
            else:
                open_phase1_dialog()

    # ==========================================
    # PHASE 2: OBJECTIVE PHYSICAL EXAM
    # ==========================================
    elif st.session_state.encounter_phase == 2:
        st.subheader("🔬 Phase 2: Objective Physical Examination Charting")
        st.write("Select or type an objective category to pull the patient's physical examination chart.")

        with st.expander("📌 Your Phase 1 Initial Differential Diagnoses"):
            for i, d in enumerate(st.session_state.initial_differentials, 1):
                st.markdown(f"**{i}.** {d}")

        st.markdown("### Perform Physical Exam Category")
        
        selected_category_input = st.selectbox(
            "Select Objective Category to Evaluate:",
            ["-- Choose Category --"] + OBJECTIVE_CATEGORIES
        )
        
        custom_typed = st.text_input("Or type specific test / category variations:", placeholder="e.g., Active range of motion")

        if st.button("Request Examination Chart Findings", type="primary"):
            chosen_cat = None
            if selected_category_input != "-- Choose Category --":
                chosen_cat = selected_category_input
            elif custom_typed.strip():
                typed_lower = custom_typed.strip().lower()
                for cat in OBJECTIVE_CATEGORIES:
                    if typed_lower in cat.lower() or cat.lower() in typed_lower:
                        chosen_cat = cat
                        break
                if not chosen_cat:
                    chosen_cat = custom_typed.strip()

            if chosen_cat:
                finding_text = active_case["objective_data"].get(chosen_cat, "No pathological findings noted.")
                
                st.session_state.objective_tests.append({
                    "category": chosen_cat,
                    "findings": finding_text
                })
                st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Physical Exam Charting Record")
        
        if not st.session_state.objective_tests:
            st.info("No physical exam charts requested yet. Select a category above to evaluate.")
        else:
            chart_df = pd.DataFrame(st.session_state.objective_tests)
            chart_df.columns = ["Objective Category / Test", "Clinical Findings"]
            st.dataframe(chart_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        if st.button("➡️ Move on to Treatment Phase", type="primary", use_container_width=True):
            if not st.session_state.objective_tests:
                st.warning("Please request at least one objective evaluation before proceeding.")
            else:
                st.session_state.encounter_phase = 3
                st.rerun()

    # ==========================================
    # PHASE 3: TREATMENT & MANAGEMENT
    # ==========================================
    elif st.session_state.encounter_phase >= 3:
        st.subheader("💊 Phase 3: Treatment & Management Plan")
        st.write("Synthesize your subjective and objective findings to formulate your final diagnosis and management strategy.")

        with st.expander("🔍 Review Prior Phase Findings"):
            st.markdown("**Phase 1 Differentials:** " + ", ".join(st.session_state.initial_differentials))
            st.markdown("**Phase 2 Objective Findings:**")
            for t in st.session_state.objective_tests:
                st.markdown(f"- **{t['category']}:** {t['findings']}")

        if st.session_state.encounter_phase == 3:
            with st.form("treatment_phase_form"):
                st.markdown("### 📝 Clinical Management Plan")
                
                f_dx = st.text_input("1. Final Diagnosis:", placeholder="e.g., Right Subacromial Pain Syndrome")
                f_edu = st.text_area("2. Education:", placeholder="Patient reassurance, pathology explanation, posture advice...", height=100)
                f_pain = st.text_area("3. Pain Management:", placeholder="Ice/heat, load modification, activity changes, modalities...", height=100)
                f_mob = st.text_area("4. Mobility:", placeholder="Range of motion exercises, joint mobilizations, stretching...", height=100)
                f_str = st.text_area("5. Strength:", placeholder="Progressive resistance exercises, stabilizer strengthening...", height=100)

                if st.form_submit_button("Submit Complete Treatment Plan", type="primary"):
                    if not f_dx.strip() or not f_edu.strip() or not f_pain.strip() or not f_mob.strip() or not f_str.strip():
                        st.error("Please complete all 5 text fields before submitting.")
                    else:
                        st.session_state.tx_final_dx = f_dx.strip()
                        st.session_state.tx_education = f_edu.strip()
                        st.session_state.tx_pain_mgmt = f_pain.strip()
                        st.session_state.tx_mobility = f_mob.strip()
                        st.session_state.tx_strength = f_str.strip()
                        st.session_state.encounter_phase = 4
                        st.rerun()

        elif st.session_state.encounter_phase == 4:
            st.success("🎉 **Clinical Encounter Complete!**")
            st.markdown(f"**Final Diagnosis:** {st.session_state.tx_final_dx}")
            
            st.markdown("---")
            st.markdown("### Submitted Treatment Plan")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Education:**")
                st.info(st.session_state.tx_education)
                st.markdown("**Pain Management:**")
                st.info(st.session_state.tx_pain_mgmt)
            with col_b:
                st.markdown("**Mobility:**")
                st.info(st.session_state.tx_mobility)
                st.markdown("**Strength:**")
                st.info(st.session_state.tx_strength)

    # ==========================================
    # STAGE 5: FULL 3-PHASE TRANSCRIPT EXPORT
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Submission Records")
    if st.sidebar.button("Compile Full 3-Phase Transcript"):
        if not st.session_state.subjective_messages:
            st.sidebar.warning("No encounter data recorded.")
        else:
            export = f"==================================================\n"
            export += f"OFFICIAL MSK 3-PHASE EVALUATION TRANSCRIPT\n"
            export += f"==================================================\n"
            export += f"Student CCID: {st.session_state.ccid}\n"
            export += f"Joint Region: {student_category} ({student_case_key})\n"
            export += f"Patient Name: {active_case['name']}\n"
            export += f"--------------------------------------------------\n\n"
            
            export += f"--- PHASE 1: SUBJECTIVE HISTORY ---\n"
            for line in st.session_state.subjective_messages:
                spk = "STUDENT" if line["role"] == "user" else "PATIENT"
                export += f"[{spk}]: {line['content']}\n"
            
            export += f"\nPHASE 1 INITIAL DIFFERENTIALS:\n"
            for idx, dx in enumerate(st.session_state.initial_differentials, 1):
                export += f"  {idx}. {dx}\n"
            
            export += f"\n--------------------------------------------------\n"
            export += f"--- PHASE 2: OBJECTIVE FINDINGS ---\n"
            if st.session_state.objective_tests:
                for item in st.session_state.objective_tests:
                    export += f"Category: {item['category']}\nFindings: {item['findings']}\n\n"
            else:
                export += f"[No objective evaluations recorded]\n\n"

            export += f"--------------------------------------------------\n"
            export += f"--- PHASE 3: TREATMENT & MANAGEMENT PLAN ---\n\n"
            export += f"FINAL DIAGNOSIS:\n{st.session_state.tx_final_dx}\n\n"
            export += f"EDUCATION:\n{st.session_state.tx_education}\n\n"
            export += f"PAIN MANAGEMENT:\n{st.session_state.tx_pain_mgmt}\n\n"
            export += f"MOBILITY:\n{st.session_state.tx_mobility}\n\n"
            export += f"STRENGTH:\n{st.session_state.tx_strength}\n"
            export += f"==================================================\n"
                
            st.sidebar.download_button(
                label="📥 Download Full Transcript (.txt)",
                data=export,
                file_name=f"MSK_FullEncounter_{st.session_state.ccid}_{student_case_key}.txt",
                mime="text/plain"
            )