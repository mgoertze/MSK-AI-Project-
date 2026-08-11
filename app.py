import streamlit as st
import pandas as pd
from groq import Groq
import json
import os
import requests
import base64

# --- API & REPO CONFIGURATION ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")  # Expected format: "username/repo-name"

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

# --- REGION-SPECIFIC DEFAULT OBJECTIVE FINDINGS TEMPLATES ---
def get_default_objective_template_for_region(region_name):
    r = str(region_name).lower()
    
    # 1. CERVICAL SPINE
    if "cervical" in r or "neck" in r:
        return {
            "Observation": "Forward head posture, protracted shoulder girdle, hypertonic upper trapezius visual bulk.",
            "Active Range of Motion (AROM)": "Flexion: 40° (Full = 50°). Extension: 45° (Full = 60°). Left Rotation: 60° painful at end-range (Full = 80°). Right Rotation: 70°. Side Bending B/L: 30° painful.",
            "Passive Range of Motion (PROM)": "Flexion: Full range with tissue-stretch end-feel. Extension: Full range. Rotation: 70° with muscular tightness end-feel.",
            "Strength / Resisted Isometrics": "Cervical Flexion: 4/5 painful. Cervical Extension: 5/5 pain-free. Cervical Side Bending B/L: 4+/5. Deep Cervical Flexors (CCFT): Impaired endurance.",
            "Functional Testing": "Sustained Neck Flexion (Desk posture simulation): Reproduces familiar neck/upper back ache at 60 seconds.",
            "Palpation": "Cervical Paraspinals (C4-C6): Moderately tender. Upper Trapezius & Levator Scapulae: Markedly tender with active trigger points. Spinous processes: Non-tender.",
            "Special Tests": "Spurling Test: Positive for localized neck pain (Negative for arm radiculopathy). Cervical Distraction Test: Reduces feeling of heaviness. Upper Limb Tension Tests (ULTT 1/Median): Negative."
        }
    
    # 2. LUMBAR SPINE
    elif "lumbar" in r or "back" in r:
        return {
            "Observation": "Flattened lumbar lordosis, antalgic posture, guarded transfer movements.",
            "Active Range of Motion (AROM)": "Flexion: 40° painful (Finger-to-floor distance 25cm). Extension: 10° painful. Side Bending B/L: 15° restricted.",
            "Passive Range of Motion (PROM)": "Flexion: Limited by muscle guarding. Extension: Limited with firm end-feel.",
            "Strength / Resisted Isometrics": "Lumbar Extension: 4/5 painful. Hip Flexion B/L: 5/5. Knee Extension (L4): 5/5. Great Toe Extension (L5): 5/5. Plantarflexion (S1): 5/5.",
            "Functional Testing": "Sit-to-Stand transfer: Slow, uses arms for assistance. Repeated Forward Bending: Increases lumbar pain.",
            "Palpation": "Lumbar Erector Spinae (L3-L5): Bilateral hypertonicity and tenderness. Quadratus Lumborum: Moderately tender. L4/L5 Spinous processes: Mildly tender.",
            "Special Tests": "Straight Leg Raise (SLR): Negative for radicular shooting pain below knee. Slump Test: Negative. Lumbar Quadrant Test: Reproduces localized L/S pain."
        }
    
    # 3. SHOULDER
    elif "shoulder" in r:
        return {
            "Observation": "Slight anterior hitch of humeral head, mild sulcus asymmetry, muscle guarding.",
            "Active Range of Motion (AROM)": "Flexion: 130° painful (Full = 180°). Abduction: 90° with painful arc between 60-120°. External Rotation: 50°. Internal Rotation: 45°.",
            "Passive Range of Motion (PROM)": "Flexion: 150° end-range discomfort. Abduction: 130° painful. External Rotation: Full. Internal Rotation: Full.",
            "Strength / Resisted Isometrics": "Flexion: 4/5. Abduction: 3+/5 painful. External Rotation: 4-/5 painful. Internal Rotation: 5/5 pain-free.",
            "Functional Testing": "Overhead reaching test: Reproduces primary pain at 90°. Hand-behind-back reach: Limited to L4 level.",
            "Palpation": "Supraspinatus insertion at greater tubercle: Markedly tender. Bicipital groove: Non-tender. AC Joint: Non-tender.",
            "Special Tests": "Hawkins-Kennedy Test: Positive. Neer Impingement Test: Positive. Empty Can (Jobe) Test: Positive for weakness and pain. Apprehension Test: Negative."
        }

    # 4. ELBOW
    elif "elbow" in r:
        return {
            "Observation": "Carrying angle normal (10-15°), no gross joint effusion, holding arm guarded in 90° flexion.",
            "Active Range of Motion (AROM)": "Flexion: 135° (Full = 145°). Extension: -5° (Full = 0°). Pronation: 80°. Supination: 75°.",
            "Passive Range of Motion (PROM)": "Flexion: Full with soft tissue-approximation. Extension: Full with hard end-feel.",
            "Strength / Resisted Isometrics": "Wrist Extension (Cozen's): 3+/5 painful. Wrist Flexion: 5/5 pain-free. Elbow Flexion: 5/5. Elbow Extension: 5/5.",
            "Functional Testing": "Grip strength testing (Dynamometer): Significantly reduced on affected side due to pain at elbow.",
            "Palpation": "Lateral Epicondyle: Exquisitely tender to touch. Medial Epicondyle: Non-tender. Radial Head: Non-tender.",
            "Special Tests": "Cozen's Test (Resisted Wrist Extension): Positive. Mill's Test (Passive Wrist Flexion/Pronation): Positive. Golfer's Elbow Test: Negative."
        }

    # 5. WRIST AND HAND
    elif "wrist" in r or "hand" in r:
        return {
            "Observation": "Mild localized swelling over radial wrist, normal muscle bulk in thenar/hypothenar eminences.",
            "Active Range of Motion (AROM)": "Wrist Flexion: 60° (Full = 80°). Wrist Extension: 55° (Full = 70°). Radial Deviation: 10° painful (Full = 20°). Ulnar Deviation: 20°.",
            "Passive Range of Motion (PROM)": "Wrist Flexion/Extension: Full. Radial Deviation: Limited by sharp localized pain.",
            "Strength / Resisted Isometrics": "Resisted Thumb Abduction: 4/5 painful. Grip Strength: 80% of unaffected side.",
            "Functional Testing": "Pinch grip test (Key & Tip pinch): Reproduces thumb-side wrist pain. Jar opening: Unable due to sharp pain.",
            "Palpation": "1st Dorsal Compartment (Abductor Pollicis Longus / Extensor Pollicis Brevis tendons): Highly tender. Anatomical Snuffbox: Non-tender.",
            "Special Tests": "Finkelstein's Test: Positive (sharp pain over radial styloid). Eichhoff's Test: Positive. Tinel's at Carpal Tunnel: Negative."
        }

    # 6. HIP
    elif "hip" in r:
        return {
            "Observation": "Antalgic gait with shortened stance phase on affected side, Trendelenburg sign negative.",
            "Active Range of Motion (AROM)": "Flexion: 100° painful (Full = 120°). Extension: 10° (Full = 20°). Abduction: 30° painful. Internal Rotation: 15° limited (Full = 45°). External Rotation: 35°.",
            "Passive Range of Motion (PROM)": "Flexion: 110° with hard/capsular end-feel. Internal Rotation: 20° with deep groin pinching.",
            "Strength / Resisted Isometrics": "Hip Abduction: 4/5 painful. Hip Flexion: 4+/5. Hip Extension: 5/5. Internal Rotation: 4/5 painful.",
            "Functional Testing": "Single-Leg Stance: Stable for 10s. Deep Squat: Limited to 60° knee bend due to groin pinching.",
            "Palpation": "Greater Trochanter: Moderately tender. Deep Groin / Femoral Triangle: Tender to deep palpation. Ischial Tuberosity: Non-tender.",
            "Special Tests": "FADDIR Test (Flexion, Adduction, Internal Rotation): Positive for deep groin pain. FABER / Patrick's Test: Positive for lateral/groin pain. Thomas Test: Positive for hip flexor tightness."
        }

    # 7. KNEE
    elif "knee" in r:
        return {
            "Observation": "Mild intra-articular joint effusion (1+ sweep test), no visible alignment deformity (Genu Varum/Valgum normal).",
            "Active Range of Motion (AROM)": "Flexion: 115° painful (Full = 135°). Extension: -5° lack of full extension.",
            "Passive Range of Motion (PROM)": "Flexion: 125° with tissue-stretch end-feel. Extension: 0° with springy block end-feel.",
            "Strength / Resisted Isometrics": "Quadriceps (Knee Extension): 4/5 painful. Hamstrings (Knee Flexion): 5/5 pain-free.",
            "Functional Testing": "Single-leg Hop: Hesitant, unable to perform smoothly. Step-down test: Painful at 45° flexion.",
            "Palpation": "Medial Joint Line: Point tender. Patellar Tendon: Non-tender. Lateral Joint Line: Non-tender. Anserine Bursa: Non-tender.",
            "Special Tests": "McMurray Test: Positive for medial joint line click/pain. Lachman Test: Negative (Firm end-point). Anterior Drawer: Negative. Patellar Apprehension: Negative."
        }

    # 8. ANKLE AND FOOT
    elif "ankle" in r or "foot" in r:
        return {
            "Observation": "Ecchymosis and edema localized below lateral malleolus, antalgic gait favoring heel-strike.",
            "Active Range of Motion (AROM)": "Dorsiflexion: 10° (Full = 20°). Plantarflexion: 35° (Full = 50°). Inversion: 15° painful (Full = 30°). Eversion: 15°.",
            "Passive Range of Motion (PROM)": "Inversion: Limited by sharp pain over lateral ligaments. Dorsiflexion: Limited by Achilles tightness.",
            "Strength / Resisted Isometrics": "Ankle Eversion (Peroneals): 4/5. Inversion: 4/5 painful. Plantarflexion (Gastrocnemius): 5/5.",
            "Functional Testing": "Single-leg Heel Raise: Able to perform 3 reps with mild wobble. Tandem gait: Unstable.",
            "Palpation": "Anterior Talofibular Ligament (ATFL): Highly tender. Calcaneofibular Ligament (CFL): Moderately tender. Lateral Malleolus Bone: Non-tender.",
            "Special Tests": "Anterior Drawer Test (Ankle): Positive for mild laxity compared to contralateral side. Talar Tilt Test: Positive for pain. Thompson Squeeze Test: Negative (Achilles intact)."
        }
        
    # GENERAL FALLBACK
    else:
        return {
            "Observation": "Postural alignment: Guarded position. Slight asymmetry noted on affected side.",
            "Active Range of Motion (AROM)": "Flexion: 75% available with pain at end-range. Extension: Full, pain-free. Lateral movements: Mildly restricted.",
            "Passive Range of Motion (PROM)": "Flexion: Full range with tissue-stretch end-feel and mild discomfort. Extension: Unrestricted.",
            "Strength / Resisted Isometrics": "Primary movers: 4/5 with pain elicited on strong contraction. Surrounding stabilizers: 5/5 non-tender.",
            "Functional Testing": "Functional movement test: Reproduces primary complaint at end-range loading.",
            "Palpation": "Point tenderness noted over local tendinous insertion. Surrounding muscular hypertonicity present.",
            "Special Tests": "Primary provocative test: Positive. Secondary stability tests: Negative."
        }

# --- DEFAULT FULL CASE LIBRARY ---
DEFAULT_CASE_LIBRARY = {
    "Cervical spine": {
        "Case 1": {
            "name": "Arthur", "region_label": "Cervical spine", "forthcomingness": 1,
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
        }
    },
    "Shoulder": {
        "Case 1": {
            "name": "Sarah", "region_label": "Shoulder", "forthcomingness": 1,
            "demeanor": "Holding right arm close to side, avoids overhead reach.",
            "chief_complaint": "Anterior shoulder pain when reaching into upper cabinets.",
            "history_present_illness": "Pain started 6 weeks ago after painting garage ceiling.",
            "location_pain": "Anterolateral shoulder radiating down to mid-deltoid.",
            "onset_pain": "Gradual onset over 6 weeks.",
            "type_pain": "Sharp with overhead activity, dull ache at rest.",
            "aggravating_factors": "Reaching overhead, dressing, lying on affected side.",
            "easing_factors": "Rest, ice, holding arm supported.",
            "radiation": "Lateral arm down to insertion of deltoid.",
            "red_flags": "Denies neck pain, chest pain, or systemic weakness.",
            "social_history": "Recreational tennis player, office worker.",
            "past_medical_history": "None.",
            "diff_dx": "Subacromial Pain Syndrome / Rotator Cuff Tendinopathy"
        }
    },
    "Hip": {
        "Case 1": {
            "name": "Robert", "region_label": "Hip", "forthcomingness": 1,
            "demeanor": "Walking with slight limp, rubs anterior groin when sitting.",
            "chief_complaint": "Deep groin pinching pain when getting out of car or squatting.",
            "history_present_illness": "Deep groin stiffness developed over 4 months.",
            "location_pain": "Anterior groin and lateral hip ('C-sign').",
            "onset_pain": "Insidious onset.",
            "type_pain": "Deep pinching ache.",
            "aggravating_factors": "Deep hip flexion, prolonged sitting, twisting on planted foot.",
            "easing_factors": "Walking on flat ground, NSAIDs.",
            "radiation": "Anterior thigh down toward knee.",
            "red_flags": "Denies night pain, unexplained weight loss, or fever.",
            "social_history": "Former recreational soccer player.",
            "past_medical_history": "None.",
            "diff_dx": "Femoroacetabular Impingement (FAI) / Labral Tear"
        }
    }
}

# --- PERSISTENT DISK & GITHUB STORAGE FUNCTIONS ---
def save_cases_to_disk(case_data):
    # 1. Update local copy for current session
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(case_data, f, indent=4)
    except Exception:
        pass

    # 2. Push commit to GitHub for permanent cloud persistence
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Get current SHA required for updating an existing file via GitHub API
            get_res = requests.get(url, headers=headers)
            sha = get_res.json().get("sha", "") if get_res.status_code == 200 else ""

            # Base64 encode updated JSON content
            json_bytes = json.dumps(case_data, indent=4).encode("utf-8")
            base64_content = base64.b64encode(json_bytes).decode("utf-8")

            payload = {
                "message": "Admin update: Sync cases.json via Streamlit UI",
                "content": base64_content,
                "sha": sha
            }

            put_res = requests.put(url, headers=headers, json=payload)
            if put_res.status_code in [200, 201]:
                st.toast("Saved permanently to GitHub repo!", icon="✅")
            else:
                st.error(f"GitHub Sync Failed: {put_res.json().get('message')}")
        except Exception as err:
            st.error(f"GitHub Sync Error: {err}")

def load_cases_from_disk():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            
            for region, cases in data.items():
                region_template = get_default_objective_template_for_region(region)
                
                for case_key, cdata in cases.items():
                    if "forthcomingness" not in cdata:
                        cdata["forthcomingness"] = 1
                    
                    if "objective_data" not in cdata:
                        cdata["objective_data"] = region_template
                    else:
                        sp_tests = cdata["objective_data"].get("Special Tests", "")
                        if "cervical" in region.lower() and "Hawkins" in sp_tests:
                            cdata["objective_data"] = region_template
                        elif "hip" in region.lower() and ("Hawkins" in sp_tests or "Spurling" in sp_tests):
                            cdata["objective_data"] = region_template
                        elif "knee" in region.lower() and ("Hawkins" in sp_tests or "Spurling" in sp_tests):
                            cdata["objective_data"] = region_template
                        elif "shoulder" in region.lower() and ("Spurling" in sp_tests or "FADDIR" in sp_tests):
                            cdata["objective_data"] = region_template
                        else:
                            for cat in OBJECTIVE_CATEGORIES:
                                if cat not in cdata["objective_data"]:
                                    cdata["objective_data"][cat] = region_template.get(cat, "No pathological findings recorded.")
            return data
        except Exception:
            save_cases_to_disk(DEFAULT_CASE_LIBRARY)
            return DEFAULT_CASE_LIBRARY
    else:
        for region, cases in DEFAULT_CASE_LIBRARY.items():
            region_template = get_default_objective_template_for_region(region)
            for case_key, cdata in cases.items():
                cdata["forthcomingness"] = 1
                cdata["objective_data"] = region_template
                
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
        f"{get_forthcomingness_instruction(c.get('forthcomingness', 1))}\n\n"
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

def match_objective_query(query_text, case_obj_data):
    q = query_text.strip().lower()
    
    if any(k in q for k in ["strength", "resisted", "mmt", "manual muscle", "myotome"]):
        return "Strength / Resisted Isometrics", case_obj_data.get("Strength / Resisted Isometrics", "Normal strength.")
    elif any(k in q for k in ["palpate", "palpation", "touch", "tenderness", "point"]):
        return "Palpation", case_obj_data.get("Palpation", "No specific point tenderness noted.")
    elif any(k in q for k in ["special test", "provocative", "test", "spurling", "distraction", "hawkins", "faddir", "faber", "mcmurray", "slr", "lachman", "cozen", "finkelstein"]):
        return "Special Tests", case_obj_data.get("Special Tests", "Special tests negative.")
    elif any(k in q for k in ["prom", "passive"]):
        return "Passive Range of Motion (PROM)", case_obj_data.get("Passive Range of Motion (PROM)", "Full PROM.")
    elif any(k in q for k in ["arom", "active range", "active motion", "flexion", "extension", "abduction", "rotation", "side bend"]):
        return "Active Range of Motion (AROM)", case_obj_data.get("Active Range of Motion (AROM)", "Full AROM.")
    elif any(k in q for k in ["observe", "observation", "posture", "gait", "look", "alignment"]):
        return "Observation", case_obj_data.get("Observation", "No gross abnormality.")
    elif any(k in q for k in ["functional", "squat", "reach", "hop", "balance", "desk", "step"]):
        return "Functional Testing", case_obj_data.get("Functional Testing", "Functional movements intact.")
    else:
        for cat, content in case_obj_data.items():
            if q in content.lower() or any(term in content.lower() for term in q.split()):
                return f"{cat} ({query_text.strip()})", content
                
        return query_text.strip(), f"Evaluation of '{query_text.strip()}': No localized or specific pathological findings reproduced."

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
        case_data["objective_data"] = get_default_objective_template_for_region(selected_category)

    st.markdown("---")
    
    with st.form("admin_case_form"):
        st.subheader(f"Editing {selected_case_key}: Patient {case_data['name']} ({selected_category})")
        
        tab1, tab2 = st.tabs(["🗣️ Subjective Case Parameters", "📊 Granular Objective Matrix"])
        
        with tab1:
            e_forthcoming = st.slider("Patient Forthcomingness (1-5):", 1, 5, int(case_data.get("forthcomingness", 1)))
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
            st.markdown(f"### Edit Objective Physical Exam Findings ({selected_category})")
            st.caption("Customize movement breakdowns, specific anatomical structures, and special tests.")
            
            edited_objective_data = {}
            for cat in OBJECTIVE_CATEGORIES:
                current_val = case_data["objective_data"].get(cat, "")
                edited_objective_data[cat] = st.text_area(f"📌 {cat}", value=current_val, height=100)

        save_submitted = st.form_submit_button("Save Case Settings & Sync to GitHub", type="primary")
        
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
        active_case["objective_data"] = get_default_objective_template_for_region(student_category)

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
                dx1 = st.text_input("Primary Suspected Differential:", placeholder="e.g., Primary Pathology")
                dx2 = st.text_input("Secondary Differential:", placeholder="e.g., Secondary Suspect")
                dx3 = st.text_input("Tertiary Differential:", placeholder="e.g., Alternative Suspect")
                
                if st.form_submit_button("Submit & Proceed to Objective Exam", type="primary"):
                    if not dx1.strip() or not dx2.strip() or not dx3.strip():
                        st.error("Please fill in all 3 differential fields before proceeding.")
                    else:
                        st.session_state.initial_differentials = [dx1.strip(), dx2.strip(), dx3.strip()]
                        st.session_state.encounter_phase = 2
                        st.rerun()

        if st.button("➡️ Move on to Objective Exam", type="primary", use_container_width=True):
            if not st.session_state.subjective_messages:
                st.warning("Please ask at least one subjective history question before moving on.")
            else:
                open_phase1_dialog()

    # ==========================================
    # PHASE 2: OBJECTIVE PHYSICAL EXAM
    # ==========================================
    elif st.session_state.encounter_phase == 2:
        st.subheader("🔬 Phase 2: Objective Physical Examination")
        st.write("Type what physical exam procedures or evaluations you want to perform.")

        with st.expander("📌 Your Phase 1 Initial Differential Diagnoses"):
            for i, d in enumerate(st.session_state.initial_differentials, 1):
                st.markdown(f"**{i}.** {d}")

        st.markdown("### Request Physical Examination Procedures")
        st.caption(f"Perform tests relevant to the **{student_category}** (e.g., MMT/Strength, Palpation, Special Tests, AROM/PROM)")
        
        user_test_query = st.text_input("Enter physical exam evaluation / test to perform:", key="test_input_field", placeholder=f"e.g., {student_category} strength testing or special tests")

        if st.button("Execute Physical Examination Test", type="primary"):
            if not user_test_query.strip():
                st.warning("Please type a test or evaluation request first.")
            else:
                category_name, finding_text = match_objective_query(user_test_query, active_case["objective_data"])
                
                st.session_state.objective_tests.append({
                    "requested": user_test_query.strip(),
                    "category": category_name,
                    "findings": finding_text
                })
                st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Physical Exam Charting Record")
        
        if not st.session_state.objective_tests:
            st.info("No physical exam tests executed yet. Type an examination request above to evaluate.")
        else:
            chart_df = pd.DataFrame(st.session_state.objective_tests)
            chart_df = chart_df[["requested", "category", "findings"]]
            chart_df.columns = ["Student Requested Test", "Matched Category", "Specific Clinical Findings"]
            st.dataframe(chart_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        if st.button("➡️ Move on to Treatment Phase", type="primary", use_container_width=True):
            if not st.session_state.objective_tests:
                st.warning("Please perform at least one objective evaluation before proceeding.")
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
                st.markdown(f"- **{t['requested']}** ({t['category']}): {t['findings']}")

        if st.session_state.encounter_phase == 3:
            with st.form("treatment_phase_form"):
                st.markdown("### 📝 Clinical Management Plan")
                
                f_dx = st.text_input("1. Final Diagnosis:", placeholder=f"e.g., Primary {student_category} Pathology")
                f_edu = st.text_area("2. Education:", placeholder="Patient reassurance, posture/ergonomic advice, prognosis...", height=100)
                f_pain = st.text_area("3. Pain Management:", placeholder="Heat/ice, activity modification, movement breaks...", height=100)
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
                    export += f"Requested: {item['requested']}\nMatched Category: {item['category']}\nFindings: {item['findings']}\n\n"
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