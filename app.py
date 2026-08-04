import streamlit as st
from groq import Groq
import json
import os

# --- API CONFIGURATION ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.1-8b-instant"
DATA_FILE = "cases.json"

# --- DEFAULT 48-CASE ANONYMIZED CLINICAL LIBRARY ---
DEFAULT_CASE_LIBRARY = {
    "Cervical spine": {
        "Case 1: Mechanical Neck Pain (Postural Strain)": {
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
            "diff_dx": "Mechanical Neck Pain (Postural Strain) vs. Cervical Facet Arthropathy vs. Tension Headache"
        },
        "Case 2: Mechanical Neck Pain (Facet Dysfunction)": {
            "name": "Beatrice", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Holds head slightly turned, hesitant to rotate quickly.",
            "chief_complaint": "Sharp catching pain when looking over right shoulder while driving.",
            "history_present_illness": "Woke up 4 days ago after sleeping in an awkward position with a 'locked' neck.",
            "location_pain": "Right unilateral C4-C6 cervical region.",
            "onset_pain": "Acute onset upon waking 4 days ago.",
            "type_pain": "Sharp catch on rotation, dull localized ache at rest.",
            "aggravating_factors": "Right cervical rotation and extension.",
            "easing_factors": "Chin tucks, keeping neck neutral, gentle warmth.",
            "radiation": "Localized to upper scapular border.",
            "red_flags": "Neurological examination completely clear.",
            "social_history": "Graphic artist.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Neck Pain (Facet Dysfunction) vs. Cervical Radiculopathy vs. Levator Scapulae Strain"
        },
        "Case 3: Mechanical Neck Pain (Discogenic Non-Radicular)": {
            "name": "Charles", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Sits very upright, cautious with cervical flexion.",
            "chief_complaint": "Deep central neck ache that worsens when looking down at phone.",
            "history_present_illness": "Gradual onset over 6 weeks after lifting heavy boxes in garage.",
            "location_pain": "Central lower cervical spine.",
            "onset_pain": "Gradual progression over 6 weeks.",
            "type_pain": "Deep toothache-like ache.",
            "aggravating_factors": "Neck flexion, coughing, sitting without head support.",
            "easing_factors": "Resting head against high-back chair, cervical retraction.",
            "radiation": "Interscapular pain (referred, non-dermatomal).",
            "red_flags": "No arm numbness or hand weakness.",
            "social_history": "Warehouse manager.",
            "past_medical_history": "Lumbar strain 5 years ago.",
            "diff_dx": "Mechanical Neck Pain (Discogenic Non-Radicular) vs. Cervical Radiculopathy vs. Thoracic Outlet Syndrome"
        },
        "Case 4: Cervical Radiculopathy": {
            "name": "Diana", "region_label": "Cervical spine", "forthcomingness": 3,
            "demeanor": "Holding arm on top of head for pain relief.",
            "chief_complaint": "Sharp shooting electric pain down left arm into thumb and index finger.",
            "history_present_illness": "Severe arm pain started 5 days ago after sudden head turn while exercising.",
            "location_pain": "Left neck radiating down arm to 1st and 2nd digits.",
            "onset_pain": "Acute event 5 days ago.",
            "type_pain": "Sharp, burning, electric shock sensation.",
            "aggravating_factors": "Cervical extension, sidebending to left.",
            "easing_factors": "Placing left hand on top of head (Bakody sign).",
            "radiation": "C6 dermatomal distribution.",
            "red_flags": "Mild weakness in biceps / wrist extension; no gait ataxia.",
            "social_history": "Accountant.",
            "past_medical_history": "Hypertension.",
            "diff_dx": "Cervical Radiculopathy vs. Carpal Tunnel Syndrome vs. Thoracic Outlet Syndrome"
        },
        "Case 5: Transverse Ligament Instability": {
            "name": "Ethan", "region_label": "Cervical spine", "forthcomingness": 2,
            "demeanor": "Anxious, manually supporting chin with hand.",
            "chief_complaint": "Feeling like head is 'heavy and unstable' with paresthesia in lip and hands upon bending neck forward.",
            "history_present_illness": "Followed high-velocity whiplash trauma in motor vehicle collision 2 weeks ago.",
            "location_pain": "Upper cervical (C1-C2) and suboccipital region.",
            "onset_pain": "Acute post-trauma 14 days ago.",
            "type_pain": "Deep pressure accompanied by neurological sensations on flexion.",
            "aggravating_factors": "Cervical flexion, unexpected bumps in car.",
            "easing_factors": "Lying supine, supporting head firmly with hands.",
            "radiation": "Perioral paresthesia and bilateral glove-like hand tingling.",
            "red_flags": "Lhermitte sign positive; perioral numbness present on flexion.",
            "social_history": "College student.",
            "past_medical_history": "Rheumatoid Arthritis.",
            "diff_dx": "Transverse Ligament Instability vs. Cervical Myelopathy vs. Odontoid Fracture"
        },
        "Case 6: Cervical Myelopathy": {
            "name": "Fiona", "region_label": "Cervical spine", "forthcomingness": 2,
            "demeanor": "Elderly, cautious wide-based gait, clumsy holding pen.",
            "chief_complaint": "Progressive hand clumsiness, difficulty buttoning shirts, and feeling off-balance when walking.",
            "history_present_illness": "Symptoms worsening over 6 months; dropping keys frequently.",
            "location_pain": "Diffuse neck stiffness, global hand paresthesia.",
            "onset_pain": "Insidious progression over 6 months.",
            "type_pain": "Vague ache with profound functional clumsiness.",
            "aggravating_factors": "Walking on uneven ground, looking down.",
            "easing_factors": "Resting in supportive armchairs.",
            "radiation": "Bilateral hands and legs.",
            "red_flags": "Positive Hoffmann sign, gait ataxia, Babinski positive.",
            "social_history": "Retired school teacher.",
            "past_medical_history": "Cervical spondylosis.",
            "diff_dx": "Cervical Myelopathy vs. Amyotrophic Lateral Sclerosis vs. Bilateral C7 Radiculopathy"
        }
    },
    "Lumbar spine": {
        "Case 1: Mechanical Low Back Pain (Lumbar Strain)": {
            "name": "George", "region_label": "Lumbar spine", "forthcomingness": 4,
            "demeanor": "Moving slowly, holding lower back with both hands.",
            "chief_complaint": "Acute lower back muscle spasm after lifting heavy garden soil.",
            "history_present_illness": "Felt sudden back tightness 2 days ago while lifting.",
            "location_pain": "Lumbosacral paraspinal muscles bilaterally.",
            "onset_pain": "Acute mechanical onset 48 hours ago.",
            "type_pain": "Tight throbbing muscle ache.",
            "aggravating_factors": "Bending forward, standing from sitting, twisting.",
            "easing_factors": "Lying flat with knees bent, ice packs.",
            "radiation": "None; stays in lower back.",
            "red_flags": "Normal leg strength, normal reflex exam.",
            "social_history": "Landscape designer.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Low Back Pain (Lumbar Strain) vs. Lumbar Disc Herniation vs. Facet Joint Sprain"
        },
        "Case 2: Mechanical Low Back Pain (Facet Arthropathy)": {
            "name": "Hannah", "region_label": "Lumbar spine", "forthcomingness": 3,
            "demeanor": "Stands slightly stooped forward to avoid extension.",
            "chief_complaint": "Dull ache in low back worse when standing straight or arching back.",
            "history_present_illness": "Developing over 1 year; worse in mornings.",
            "location_pain": "L4-S1 bilateral low back and upper buttocks.",
            "onset_pain": "Gradual progressive onset.",
            "type_pain": "Dull localized bone and joint ache.",
            "aggravating_factors": "Lumbar extension, standing upright, prolonged walking.",
            "easing_factors": "Sitting flexed, leaning forward over counter.",
            "radiation": "Posterior buttock, does not cross knee.",
            "red_flags": "No neurological deficits down legs.",
            "social_history": "Retired administrative clerk.",
            "past_medical_history": "Lumbar osteoarthritis.",
            "diff_dx": "Mechanical Low Back Pain (Facet Arthropathy) vs. Lumbar Spinal Stenosis vs. Sacroiliac Joint Dysfunction"
        },
        "Case 3: Mechanical Low Back Pain (Discogenic)": {
            "name": "Ian", "region_label": "Lumbar spine", "forthcomingness": 3,
            "demeanor": "Prefers standing during interview; sitting causes groans.",
            "chief_complaint": "Deep central low back pain made agonizing by prolonged sitting.",
            "history_present_illness": "Felt a 'pop' in back 3 weeks ago while moving couch.",
            "location_pain": "Central L5-S1 lumbar spine.",
            "onset_pain": "Subacute mechanical onset 3 weeks ago.",
            "type_pain": "Deep, pressure-like toothache in low back.",
            "aggravating_factors": "Sitting, forward bending, coughing, sneezing.",
            "easing_factors": "Standing, walking, prone press-ups.",
            "radiation": "Gluteal region bilaterally.",
            "red_flags": "Straight leg raise negative for true radicular leg pain.",
            "social_history": "Office worker.",
            "past_medical_history": "None.",
            "diff_dx": "Mechanical Low Back Pain (Discogenic) vs. Lumbar Radiculopathy vs. Sacroiliac Joint Strain"
        },
        "Case 4: Neurogenic Claudication / Lateral Foraminal Stenosis": {
            "name": "Julia", "region_label": "Lumbar spine", "forthcomingness": 4,
            "demeanor": "Elderly, leaning forward over a walking frame.",
            "chief_complaint": "Bilateral leg aching and heaviness that forces sitting down after walking 5 minutes.",
            "history_present_illness": "Gradual progression over 2 years; can only shop using a grocery cart.",
            "location_pain": "Lower lumbar spine radiating to bilateral posterior thighs and calves.",
            "onset_pain": "Insidious onset over 24 months.",
            "type_pain": "Heavy, cramping leg fatigue.",
            "aggravating_factors": "Walking upright, lumbar extension.",
            "easing_factors": "Sitting down, bending forward ('shopping cart sign').",
            "radiation": "Bilateral legs.",
            "red_flags": "Pedal pulses strong; no bowel or bladder changes.",
            "social_history": "Retired librarian.",
            "past_medical_history": "Spinal stenosis.",
            "diff_dx": "Neurogenic Claudication / Lateral Foraminal Stenosis vs. Vascular Claudication vs. Lumbar Disc Herniation"
        },
        "Case 5: Radiculopathy": {
            "name": "Kevin", "region_label": "Lumbar spine", "forthcomingness": 3,
            "demeanor": "Anxious, guarding right leg.",
            "chief_complaint": "Sharp burning pain shooting down back of right leg to top of foot.",
            "history_present_illness": "Onset 10 days ago after heavy squatting at gym.",
            "location_pain": "Right L5 dermatome (buttock, lateral thigh, dorsum of foot).",
            "onset_pain": "Acute event 10 days ago.",
            "type_pain": "Sharp, electric shock, burning pain.",
            "aggravating_factors": "Sitting, coughing, straight leg elevation.",
            "easing_factors": "Lying supine with legs elevated on pillows.",
            "radiation": "Down leg into foot.",
            "red_flags": "Dorsiflexion weakness (great toe extension 4/5); no bowel/bladder dysfunction.",
            "social_history": "Personal trainer.",
            "past_medical_history": "None.",
            "diff_dx": "Radiculopathy vs. Piriformis Syndrome vs. Hamstring Strain"
        },
        "Case 6: Cauda Equina Syndrome": {
            "name": "Laura", "region_label": "Lumbar spine", "forthcomingness": 2,
            "demeanor": "Distressed, tearful, unable to sit comfortably.",
            "chief_complaint": "Sudden bilateral leg weakness, groin numbness, and loss of bowel/bladder control.",
            "history_present_illness": "Severe back pain for 1 week suddenly exploded into leg numbness and incontinence 6 hours ago.",
            "location_pain": "Low back, bilateral legs, groin ('saddle area').",
            "onset_pain": "Acute red flag emergency onset 6 hours ago.",
            "type_pain": "Severe deep pain with profound numbness.",
            "aggravating_factors": "Any movement.",
            "easing_factors": "None.",
            "radiation": "Bilateral legs and perineum.",
            "red_flags": "Saddle anesthesia, urinary retention/incontinence, bilateral leg foot drop.",
            "social_history": "Teacher.",
            "past_medical_history": "Lumbar disc herniation.",
            "diff_dx": "Cauda Equina Syndrome vs. Massive Lumbar Disc Herniation vs. Spinal Cord Compression"
        }
    },
    "Shoulder": {
        "Case 1: Rotator Cuff Related Pain Syndrome": {
            "name": "Maya", "region_label": "Shoulder", "forthcomingness": 3,
            "demeanor": "Holding shoulder, wincing when lifting arm.",
            "chief_complaint": "Anterolateral shoulder pain when reaching overhead or taking off sweater.",
            "history_present_illness": "Pain developed gradually over 2 months after painting walls.",
            "location_pain": "Anterolateral deltoid insertion.",
            "onset_pain": "Insidious onset over 8 weeks.",
            "type_pain": "Dull ache, sharp painful arc between 60-120 degrees.",
            "aggravating_factors": "Reaching overhead, reaching behind back, lying on affected side.",
            "easing_factors": "Resting arm at side, ice packs.",
            "radiation": "Mid-deltoid muscle belly.",
            "red_flags": "No sudden total loss of muscle strength.",
            "social_history": "Painter, handyman.",
            "past_medical_history": "None.",
            "diff_dx": "Rotator Cuff Related Pain Syndrome vs. Adhesive Capsulitis vs. Cervical Spine Referral"
        },
        "Case 2: Massive Rotator Cuff Rupture": {
            "name": "Nora", "region_label": "Shoulder", "forthcomingness": 3,
            "demeanor": "Elderly, arm hanging limp at side, unable to lift arm against gravity.",
            "chief_complaint": "Inability to raise right arm after falling onto shoulder 2 weeks ago.",
            "history_present_illness": "Fell 14 days ago; felt tearing sensation, arm has been non-functional since.",
            "location_pain": "Global anterolateral shoulder.",
            "onset_pain": "Acute traumatic onset 2 weeks ago.",
            "type_pain": "Deep dull ache; severe weakness / pseudo-paralysis on abduction.",
            "aggravating_factors": "Attempting to raise arm.",
            "easing_factors": "Supporting elbow with opposite hand.",
            "radiation": "Down arm to elbow.",
            "red_flags": "Positive drop arm test; complete inability to hold arm abducted.",
            "social_history": "Retired gardener.",
            "past_medical_history": "Chronic shoulder impingement.",
            "diff_dx": "Massive Rotator Cuff Rupture vs. Axillary Nerve Palsy vs. Glenohumeral Dislocation"
        },
        "Case 3: Adhesive Capsulitis": {
            "name": "Oliver", "region_label": "Shoulder", "forthcomingness": 3,
            "demeanor": "Holding arm pinned tightly against ribs.",
            "chief_complaint": "Severe global stiffness with loss of both active and passive shoulder movement.",
            "history_present_illness": "Deep shoulder ache started 5 months ago and progressively froze shoulder movement.",
            "location_pain": "Deep shoulder joint capsule.",
            "onset_pain": "Insidious progression over 20 weeks.",
            "type_pain": "Agonizing sharp pain at end-range, constant deep ache at night.",
            "aggravating_factors": "External rotation, sudden movements, sleeping on arm.",
            "easing_factors": "Resting arm immobilized at side.",
            "radiation": "Upper arm.",
            "red_flags": "Profound loss of passive external rotation.",
            "social_history": "Executive.",
            "past_medical_history": "Type II Diabetes Mellitus.",
            "diff_dx": "Adhesive Capsulitis vs. Glenohumeral Osteoarthritis vs. Rotator Cuff Tear"
        },
        "Case 4: Anterior Instability": {
            "name": "Penelope", "region_label": "Shoulder", "forthcomingness": 4,
            "demeanor": "Young, hesitant to let doctor move arm into high-five position.",
            "chief_complaint": "Feeling that shoulder is going to 'pop out' when throwing or reaching overhead.",
            "history_present_illness": "Dislocated shoulder playing rugby 6 months ago; felt unstable ever since.",
            "location_pain": "Anterior glenohumeral joint line.",
            "onset_pain": "Recurrent instability following acute dislocation.",
            "type_pain": "Sharp apprehension and slipping sensation.",
            "aggravating_factors": "Abduction and external rotation ('cocking phase' of throw).",
            "easing_factors": "Keeping arm in internal rotation against chest.",
            "radiation": "Anterior arm.",
            "red_flags": "Positive apprehension test; axillary nerve intact.",
            "social_history": "Rugby player.",
            "past_medical_history": "Anterior dislocation 6 months ago.",
            "diff_dx": "Anterior Instability vs. SLAP Tear vs. AC Joint Sprain"
        },
        "Case 5: Frozen Shoulder": {
            "name": "Quentin", "region_label": "Shoulder", "forthcomingness": 3,
            "demeanor": "Guarded, holding shoulder still.",
            "chief_complaint": "Aching shoulder pain with restriction in reaching up into cupboards.",
            "history_present_illness": "Spontaneous onset over past 3 months following minor wrist injury.",
            "location_pain": "Global shoulder joint capsule.",
            "onset_pain": "Gradual onset over 12 weeks.",
            "type_pain": "Dull constant ache, sharp with forced movement.",
            "aggravating_factors": "Reaching behind back, reaching overhead.",
            "easing_factors": "Keeping arm close to trunk.",
            "radiation": "Deltoid area.",
            "red_flags": "Passive motion restricted in all planes.",
            "social_history": "Teacher.",
            "past_medical_history": "Hypothyroidism.",
            "diff_dx": "Frozen Shoulder vs. Rotator Cuff Related Pain Syndrome vs. Biceps Tendinopathy"
        },
        "Case 6: AC Joint Sprain": {
            "name": "Rosa", "region_label": "Shoulder", "forthcomingness": 3,
            "demeanor": "Pointing directly to top bump on shoulder.",
            "chief_complaint": "Sharp pain on the very top of shoulder after landing directly on it during cycling crash.",
            "history_present_illness": "Crashed bicycle 5 days ago, impacting lateral point of shoulder.",
            "location_pain": "Acromioclavicular (AC) joint top of shoulder.",
            "onset_pain": "Acute trauma 5 days ago.",
            "type_pain": "Sharp focal pain, visible step-off deformity.",
            "aggravating_factors": "Cross-body adduction (reaching across chest), overhead reaching.",
            "easing_factors": "Arm supported in sling.",
            "radiation": "Trapezius muscle ridge.",
            "red_flags": "Skin intact over bump; neurovascular exam normal distally.",
            "social_history": "Cyclist.",
            "past_medical_history": "None.",
            "diff_dx": "AC Joint Sprain vs. Clavicle Fracture vs. Subacromial Bursitis"
        }
    },
    "Elbow": {
        "Case 1: Medial Epicondylosis": {
            "name": "Samuel", "region_label": "Elbow", "forthcomingness": 4,
            "demeanor": "Holding inner elbow knob.",
            "chief_complaint": "Inner elbow pain when flexing wrist or gripping objects tightly.",
            "history_present_illness": "Gradual onset over 2 months after intensive golf practice.",
            "location_pain": "Medial epicondyle of elbow.",
            "onset_pain": "Insidious onset over 8 weeks.",
            "type_pain": "Aching over inner bone, sharp during wrist flexion.",
            "aggravating_factors": "Golf swings, carrying heavy buckets, wrist flexing.",
            "easing_factors": "Rest, ice, wrist flexor bracing.",
            "radiation": "Flexor muscle mass of anterior forearm.",
            "red_flags": "No ulnar nerve numbness in 4th/5th digits.",
            "social_history": "Golfer, carpenter.",
            "past_medical_history": "None.",
            "diff_dx": "Medial Epicondylosis vs. Cubital Tunnel Syndrome vs. UCL Sprain"
        },
        "Case 2: Lateral Epicondylosis": {
            "name": "Tina", "region_label": "Elbow", "forthcomingness": 3,
            "demeanor": "Wincing when picking up coffee cup.",
            "chief_complaint": "Outer elbow pain and weak grip strength.",
            "history_present_illness": "Onset 6 weeks ago after repetitive manual pruning in garden and tennis.",
            "location_pain": "Lateral epicondyle of elbow.",
            "onset_pain": "Insidious onset 6 weeks ago.",
            "type_pain": "Sharp burning sensation over outer elbow point.",
            "aggravating_factors": "Shaking hands, opening jar lids, gripping, backhand tennis strokes.",
            "easing_factors": "Rest, ice, counterforce strap.",
            "radiation": "Distally down extensor forearm muscles.",
            "red_flags": "Joint range of motion fully intact.",
            "social_history": "IT specialist, tennis player.",
            "past_medical_history": "None.",
            "diff_dx": "Lateral Epicondylosis vs. Radial Tunnel Syndrome vs. C6 Cervical Radiculopathy"
        },
        "Case 3: UCL Sprain": {
            "name": "Victor", "region_label": "Elbow", "forthcomingness": 3,
            "demeanor": "Young baseball player, rubbing inner elbow crease.",
            "chief_complaint": "Inner elbow pain and popping feeling during acceleration phase of pitch.",
            "history_present_illness": "Felt a sharp pop in inner elbow during fast pitch 1 week ago.",
            "location_pain": "Ulnar collateral ligament along medial elbow joint line.",
            "onset_pain": "Acute event during throwing 7 days ago.",
            "type_pain": "Sharp inner elbow joint pain with throwing.",
            "aggravating_factors": "Valgus stress on elbow, high-velocity throwing.",
            "easing_factors": "Resting from throwing, ice.",
            "radiation": "Medial elbow.",
            "red_flags": "Valgus stress test reveals increased laxity.",
            "social_history": "College baseball pitcher.",
            "past_medical_history": "Medial elbow soreness 1 year ago.",
            "diff_dx": "UCL Sprain vs. Medial Epicondylosis vs. Flexor-Pronator Strain"
        },
        "Case 4: Olecranon Bursitis": {
            "name": "Wendy", "region_label": "Elbow", "forthcomingness": 4,
            "demeanor": "Pointing to large fluid-filled sac at tip of elbow.",
            "chief_complaint": "Large, goose-egg shaped fluid swelling on the tip of the elbow.",
            "history_present_illness": "Swelling appeared over 3 days after leaning on hard desk while working.",
            "location_pain": "Posterior olecranon tip.",
            "onset_pain": "Rapid onset swelling over 72 hours.",
            "type_pain": "Pressure discomfort, non-tender unless pressed hard.",
            "aggravating_factors": "Direct pressure on elbow tip.",
            "easing_factors": "Avoiding contact pressure, compression.",
            "radiation": "None.",
            "red_flags": "No fever, no skin redness or warmth (aseptic).",
            "social_history": "Office worker.",
            "past_medical_history": "Gout.",
            "diff_dx": "Olecranon Bursitis (Aseptic) vs. Septic Bursitis vs. Rheumatoid Nodule"
        },
        "Case 5: Distal Biceps Rupture": {
            "name": "Xavier", "region_label": "Elbow", "forthcomingness": 2,
            "demeanor": "Guarding elbow flexed at 90 degrees, visible bruising in crease.",
            "chief_complaint": "Sudden pop in elbow crease while lifting heavy motor, followed by weak arm curling.",
            "history_present_illness": "Heard/felt a pop 4 days ago lifting heavy machinery.",
            "location_pain": "Anterodistal cubital fossa.",
            "onset_pain": "Acute traumatic onset 4 days ago.",
            "type_pain": "Deep tearing ache, severe weakness in supination.",
            "aggravating_factors": "Flexing elbow, supinating forearm against load.",
            "easing_factors": "Resting arm supported.",
            "radiation": "Anterior distal upper arm.",
            "red_flags": "Positive hook test (distal tendon cord non-palpable); ecchymosis.",
            "social_history": "Mechanic.",
            "past_medical_history": "None.",
            "diff_dx": "Distal Biceps Rupture vs. Brachialis Muscle Strain vs. Antecubital Hematoma"
        },
        "Case 6: Osteoarthritis": {
            "name": "Yasmine", "region_label": "Elbow", "forthcomingness": 3,
            "demeanor": "Older manual laborer, elbow stuck in partial flexion.",
            "chief_complaint": "Deep elbow joint ache and inability to fully straighten or bend elbow.",
            "history_present_illness": "Gradual stiffness and locking over 5 years.",
            "location_pain": "Global elbow joint line.",
            "onset_pain": "Chronic insidious progression over years.",
            "type_pain": "Dull deep joint ache, mechanical clicking at end-range.",
            "aggravating_factors": "Heavy lifting, terminal extension and flexion.",
            "easing_factors": "Warmth, light unweighted movement.",
            "radiation": "Forearm.",
            "red_flags": "Loss of end-range extension and flexion.",
            "social_history": "Retired jackhammer operator.",
            "past_medical_history": "Systemic OA.",
            "diff_dx": "Elbow Osteoarthritis vs. Intra-articular Loose Body vs. Posterior Impingement"
        }
    },
    "Wrist and hand": {
        "Case 1: De-Quervains": {
            "name": "Zachary", "region_label": "Wrist and hand", "forthcomingness": 4,
            "demeanor": "Holding thumb-side of wrist, cradling hand.",
            "chief_complaint": "Sharp wrist pain on the thumb side when picking up baby or wringing towels.",
            "history_present_illness": "Developed 3 weeks postpartum, worsening with lifting infant under armpits.",
            "location_pain": "Radial styloid process of wrist.",
            "onset_pain": "Gradual onset over 3 weeks.",
            "type_pain": "Sharp stabbing pain over radial styloid.",
            "aggravating_factors": "Lifting baby, flexing thumb and bending wrist to ulnar side.",
            "easing_factors": "Thumb spica splint, rest.",
            "radiation": "Dorsal thumb and radial forearm.",
            "red_flags": "No nerve tingling in fingers.",
            "social_history": "New mother.",
            "past_medical_history": "None.",
            "diff_dx": "De-Quervains Tenosynovitis vs. Scaphoid Fracture vs. 1st CMC Osteoarthritis"
        },
        "Case 2: Jersey Finger": {
            "name": "Abigail", "region_label": "Wrist and hand", "forthcomingness": 3,
            "demeanor": "Holding ring finger straight, unable to bend tip.",
            "chief_complaint": "Inability to bend the tip of the ring finger after tackling player in football.",
            "history_present_illness": "Ring finger got caught in jersey 2 days ago during match.",
            "location_pain": "Volar aspect of distal phalanx / DIP joint of 4th digit.",
            "onset_pain": "Acute traumatic onset 48 hours ago.",
            "type_pain": "Local tender ache, complete loss of active DIP flexion.",
            "aggravating_factors": "Attempting to make a fist.",
            "easing_factors": "Splinting finger in extension.",
            "radiation": "None.",
            "red_flags": "FDP tendon retraction; finger remains extended at DIP in resting cascade.",
            "social_history": "Football player.",
            "past_medical_history": "None.",
            "diff_dx": "Jersey Finger (FDP Avulsion) vs. DIP Joint Sprain vs. Mallet Finger"
        },
        "Case 3: Trigger Finger": {
            "name": "Benjamin", "region_label": "Wrist and hand", "forthcomingness": 3,
            "demeanor": "Demonstrating middle finger popping open with opposite hand.",
            "chief_complaint": "Middle finger catches in palm when flexing and pops open painfully.",
            "history_present_illness": "Started catching 1 month ago; requires unlocking manually in morning.",
            "location_pain": "Palmar A1 pulley at 3rd metacarpal head.",
            "onset_pain": "Insidious onset over 4 weeks.",
            "type_pain": "Painful snap or popping sensation in palm.",
            "aggravating_factors": "Gripping objects tight, making a fist.",
            "easing_factors": "Passively straightening finger, warm water soak.",
            "radiation": "Along palmar aspect of finger.",
            "red_flags": "Tender nodule palpable over A1 pulley.",
            "social_history": "Gardener.",
            "past_medical_history": "Diabetes Mellitus.",
            "diff_dx": "Trigger Finger vs. Flexor Tendon Laceration vs. Dupuytren Contracture"
        },
        "Case 4: TFCC Pathology": {
            "name": "Chloe", "region_label": "Wrist and hand", "forthcomingness": 3,
            "demeanor": "Holding pinky side of wrist.",
            "chief_complaint": "Ulnar-sided wrist pain and clicking when pushing up from a chair.",
            "history_present_illness": "Fell on outstretched hand 6 weeks ago while gymnastics training.",
            "location_pain": "Triangular fibrocartilage complex (ulnar fovea / distal to ulnar head).",
            "onset_pain": "Subacute post-trauma 6 weeks ago.",
            "type_pain": "Deep dull ulnar ache, sharp clicking with forearm rotation.",
            "aggravating_factors": "Pushing up from chair, ulnar deviation, pronation/supination under load.",
            "easing_factors": "Ulnar gutter splint, avoiding wrist loading.",
            "radiation": "None.",
            "red_flags": "Positive TFCC compression test; DRUJ stability intact.",
            "social_history": "Gymnast.",
            "past_medical_history": "None.",
            "diff_dx": "TFCC Pathology vs. ECU Tendinopathy vs. Ulnar Styloid Fracture"
        },
        "Case 5: Thumb UCL": {
            "name": "Daniel", "region_label": "Wrist and hand", "forthcomingness": 3,
            "demeanor": "Holding base of thumb with ice pack.",
            "chief_complaint": "Weak pinch grip and sharp pain at inner base of thumb after ski pole fell out of hand.",
            "history_present_illness": "Ski pole caught thumb 3 days ago, twisting it outward.",
            "location_pain": "Ulnar collateral ligament of 1st MCP joint.",
            "onset_pain": "Acute valgus stress trauma 3 days ago.",
            "type_pain": "Sharp pain on pinching, localized swelling at inner thumb MCP joint.",
            "aggravating_factors": "Pinching paper, opening door handles, twisting keys.",
            "easing_factors": "Immobilizing thumb in spica.",
            "radiation": "None.",
            "red_flags": "Valgus stress testing shows significant joint opening (Gamekeeper / Skier Thumb).",
            "social_history": "Skier.",
            "past_medical_history": "None.",
            "diff_dx": "Thumb UCL Sprain ('Skier Thumb') vs. 1st MCP Fracture vs. Radial Collateral Ligament Sprain"
        },
        "Case 6: Scaphoid Fracture": {
            "name": "Emily", "region_label": "Wrist and hand", "forthcomingness": 2,
            "demeanor": "Wearing elastic wrist wrap, cautious of thumb movement.",
            "chief_complaint": "Deep wrist ache in anatomical snuffbox after falling on outstretched hand 1 week ago.",
            "history_present_illness": "Fell 7 days ago; thought it was a simple wrist sprain.",
            "location_pain": "Anatomical snuffbox / scaphoid tubercle.",
            "onset_pain": "Acute trauma 7 days ago.",
            "type_pain": "Deep dull wrist ache, sharp with thumb loading.",
            "aggravating_factors": "Gripping, weight-bearing on extended palm, axial loading of thumb.",
            "easing_factors": "Resting wrist, immobilization.",
            "radiation": "Radial side of wrist.",
            "red_flags": "Focal point tenderness over scaphoid in anatomical snuffbox.",
            "social_history": "Snowboarder.",
            "past_medical_history": "None.",
            "diff_dx": "Scaphoid Fracture vs. Wrist Sprain vs. Radial Styloid Fracture"
        }
    },
    "Hip": {
        "Case 1: Proximal Hamstring Tendinopathy": {
            "name": "Frank", "region_label": "Hip", "forthcomingness": 3,
            "demeanor": "Sits on edge of chair / cushion to avoid sitting on ischial tuberosity.",
            "chief_complaint": "Deep buttock pain right over sit-bone when sitting long hours or running hills.",
            "history_present_illness": "Developed gradually over 3 months during marathon training.",
            "location_pain": "Ischial tuberosity of deep buttock.",
            "onset_pain": "Insidious onset over 12 weeks.",
            "type_pain": "Deep localized dull ache, sharp catching with deep hip flexion.",
            "aggravating_factors": "Sitting on hard chairs, running uphill, lunging.",
            "easing_factors": "Standing, sitting on donut cushion.",
            "radiation": "Proximal posterior thigh.",
            "red_flags": "Lumbar spine screen normal; sciatic nerve conduction clear.",
            "social_history": "Marathon runner, accountant.",
            "past_medical_history": "None.",
            "diff_dx": "Proximal Hamstring Tendinopathy vs. Ischiogluteal Bursitis vs. Sciatic Nerve Entrapment"
        },
        "Case 2: Athletic Pubalgia": {
            "name": "Grace", "region_label": "Hip", "forthcomingness": 3,
            "demeanor": "Holding lower abdomen / inner groin.",
            "chief_complaint": "Sharp lower abdominal and inner groin pain during twisting and kicking.",
            "history_present_illness": "Pain onset 1 month ago during soccer match when twisting off planted foot.",
            "location_pain": "Pubic tubercle and inguinal canal region.",
            "onset_pain": "Subacute onset 4 weeks ago.",
            "type_pain": "Sharp tearing groin pain with high-intensity load.",
            "aggravating_factors": "Sprinting, cutting, sit-ups, squeezing knees together.",
            "easing_factors": "Rest, avoiding explosive sprinting.",
            "radiation": "Medial thigh and lower rectus abdominis.",
            "red_flags": "No palpable hernia sac or abdominal wall defect.",
            "social_history": "Soccer player.",
            "past_medical_history": "None.",
            "diff_dx": "Athletic Pubalgia ('Sports Hernia') vs. Adductor Longus Strain vs. Osteitis Pubis"
        },
        "Case 3: Greater Trochanteric Pain Syndrome": {
            "name": "Henry", "region_label": "Hip", "forthcomingness": 4,
            "demeanor": "Touching lateral aspect of outer hip bone.",
            "chief_complaint": "Outer hip pain when lying on affected side at night and walking up stairs.",
            "history_present_illness": "Developed over 2 months after starting a walking program.",
            "location_pain": "Greater trochanter of lateral hip.",
            "onset_pain": "Insidious onset over 8 weeks.",
            "type_pain": "Sharp tenderness over outer bone, dull ache down lateral thigh.",
            "aggravating_factors": "Lying directly on hip in bed, single-leg stance, stairs.",
            "easing_factors": "Sleeping with pillow between knees, ice.",
            "radiation": "Lateral thigh to knee.",
            "red_flags": "Hip joint internal rotation is smooth and painless.",
            "social_history": "Walker, teacher.",
            "past_medical_history": "None.",
            "diff_dx": "Greater Trochanteric Pain Syndrome vs. IT Band Syndrome vs. L4 Radiculopathy"
        },
        "Case 4: FAI": {
            "name": "Isabel", "region_label": "Hip", "forthcomingness": 3,
            "demeanor": "Making a 'C-shape' with hand around anterior/lateral hip.",
            "chief_complaint": "Sharp pinch in deep groin when squatting or getting out of car.",
            "history_present_illness": "Groin pinch developed over 4 months in young active individual.",
            "location_pain": "Anterior hip joint capsule / groin ('C-sign').",
            "onset_pain": "Gradual onset over 16 weeks.",
            "type_pain": "Sharp catching deep in front of hip joint.",
            "aggravating_factors": "Deep hip flexion, internal rotation, prolonged sitting in low chair.",
            "easing_factors": "Standing, keeping hip in neutral alignment.",
            "radiation": "Anterior thigh.",
            "red_flags": "FADIR test positive (reproduces deep groin pain).",
            "social_history": "Crossfit athlete.",
            "past_medical_history": "Cam morphology on prior X-ray.",
            "diff_dx": "FAI (Femoroacetabular Impingement) vs. Acetabular Labral Tear vs. Iliopsoas Bursitis"
        },
        "Case 5: Osteoarthritis": {
            "name": "Jack", "region_label": "Hip", "forthcomingness": 3,
            "demeanor": "Older adult, limping, rubbing front groin area.",
            "chief_complaint": "Deep groin stiffness and difficulty tying shoes or putting on socks.",
            "history_present_illness": "Aching stiffness worsening progressively over 2 years.",
            "location_pain": "Anterior groin and deep hip joint.",
            "onset_pain": "Chronic insidious progression over 24 months.",
            "type_pain": "Dull deep grinding ache, morning stiffness lasting 30 minutes.",
            "aggravating_factors": "Weight-bearing after sitting, squatting, getting out of car.",
            "easing_factors": "Warm showers, light unweighted movement.",
            "radiation": "Down anterior thigh to knee.",
            "red_flags": "Loss of passive hip internal rotation.",
            "social_history": "Retired farmer.",
            "past_medical_history": "Bilateral knee OA.",
            "diff_dx": "Hip Osteoarthritis vs. Lumbar Spine L3 Referral vs. Trochanteric Bursitis"
        },
        "Case 6: Hip Flexor Strain": {
            "name": "Karen", "region_label": "Hip", "forthcomingness": 4,
            "demeanor": "Sprinter, pointing to front fold of hip.",
            "chief_complaint": "Sharp pull in front crease of hip when driving knee up high while sprinting.",
            "history_present_illness": "Felt sharp pain 3 days ago sprinting off track blocks.",
            "location_pain": "Anterior hip crease (iliopsoas / rectus femoris origin).",
            "onset_pain": "Acute event 3 days ago.",
            "type_pain": "Sharp pain on hip flexion, tender muscle belly.",
            "aggravating_factors": "Driving knee up against resistance, stretching hip into extension.",
            "easing_factors": "Rest, keeping hip slightly flexed, ice.",
            "radiation": "Down anterior thigh.",
            "red_flags": "No palpable mass; hip joint internal rotation painless.",
            "social_history": "Track sprinter.",
            "past_medical_history": "None.",
            "diff_dx": "Hip Flexor Strain vs. Avulsion Fracture of AIIS vs. Femoral Nerve Entrapment"
        }
    },
    "Knee": {
        "Case 1: Patellofemoral Pain Syndrome": {
            "name": "Liam", "region_label": "Knee", "forthcomingness": 4,
            "demeanor": "Young woman, pointing around kneecap.",
            "chief_complaint": "Dull ache around and behind kneecap when sitting long hours or running downhill.",
            "history_present_illness": "Vague kneecap ache started 2 months ago after increasing running mileage.",
            "location_pain": "Peripatellar / retro-patellar region.",
            "onset_pain": "Insidious onset 8 weeks ago.",
            "type_pain": "Diffuse aching 'movie theater sign' ache.",
            "aggravating_factors": "Sitting flexed long hours, running downhill, stairs.",
            "easing_factors": "Straightening leg, quadriceps strengthening, ice.",
            "radiation": "Around kneecap.",
            "red_flags": "Zero joint swelling, no true locking.",
            "social_history": "Marathon trainee.",
            "past_medical_history": "None.",
            "diff_dx": "Patellofemoral Pain Syndrome vs. Patellar Tendinopathy vs. Plica Syndrome"
        },
        "Case 2: Meniscal Tear": {
            "name": "Michael", "region_label": "Knee", "forthcomingness": 3,
            "demeanor": "Holding medial knee joint line.",
            "chief_complaint": "Inner knee joint line pain with painful clicking and locking when squatting.",
            "history_present_illness": "Twisted knee 3 weeks ago while stepping down off ladder.",
            "location_pain": "Medial joint line of knee.",
            "onset_pain": "Subacute post-twist 3 weeks ago.",
            "type_pain": "Sharp catching pain at joint line, delayed swelling.",
            "aggravating_factors": "Deep squatting, twisting on planted foot, stairs.",
            "easing_factors": "Keeping knee straight, ice.",
            "radiation": "Medial joint line.",
            "red_flags": "Occasional true joint locking where knee cannot fully straighten.",
            "social_history": "Electrician.",
            "past_medical_history": "None.",
            "diff_dx": "Meniscal Tear vs. MCL Sprain vs. Pes Anserine Bursitis"
        },
        "Case 3: ACL Sprain": {
            "name": "Elena", "region_label": "Knee", "forthcomingness": 3,
            "demeanor": "Guarding knee, on crutches.",
            "chief_complaint": "Right knee instability and feeling of joint giving way after hearing a loud 'pop'.",
            "history_present_illness": "Pivoted quickly in soccer match yesterday, felt loud pop with immediate rapid joint swelling.",
            "location_pain": "Deep inside knee joint.",
            "onset_pain": "Acute traumatic onset 24 hours ago.",
            "type_pain": "Throbbing, deep ache with sharp catch upon weight-bearing.",
            "aggravating_factors": "Bearing weight, twisting, attempting extension.",
            "easing_factors": "Crutches, ice, elevation.",
            "radiation": "Localized to joint.",
            "red_flags": "Lachman test and anterior drawer test strongly positive.",
            "social_history": "Soccer athlete.",
            "past_medical_history": "None.",
            "diff_dx": "ACL Sprain vs. Meniscal Tear vs. Patellar Dislocation"
        },
        "Case 4: PCL Sprain": {
            "name": "Nina", "region_label": "Knee", "forthcomingness": 3,
            "demeanor": "Holding anterior upper shin area.",
            "chief_complaint": "Posterior knee ache and instability when walking down stairs after dashboard injury.",
            "history_present_illness": "Direct impact to front of flexed shin in car crash 2 weeks ago.",
            "location_pain": "Posterior popliteal fossa / upper tibia.",
            "onset_pain": "Acute post-trauma 14 days ago.",
            "type_pain": "Dull posterior knee pain, feeling of sag.",
            "aggravating_factors": "Walking down steep slopes, deceleration, kneeling.",
            "easing_factors": "Resting knee in mild extension.",
            "radiation": "Calf.",
            "red_flags": "Posterior sag sign positive (tibial tuberosity drops posteriorly).",
            "social_history": "Sales manager.",
            "past_medical_history": "None.",
            "diff_dx": "PCL Sprain vs. ACL Sprain vs. Popliteus Muscle Strain"
        },
        "Case 5: Osteoarthritis": {
            "name": "Oscar", "region_label": "Knee", "forthcomingness": 4,
            "demeanor": "Senior citizen, cheerful, rubbing inner knee.",
            "chief_complaint": "Deep knee stiffness and grinding when climbing stairs or getting up from chairs.",
            "history_present_illness": "Gradual worsening of morning knee stiffness over 3 years.",
            "location_pain": "Bilateral medial joint line and patellofemoral joint.",
            "onset_pain": "Chronic insidious progression over 36 months.",
            "type_pain": "Deep aching sore pain, morning stiffness lasting 20 minutes.",
            "aggravating_factors": "Stairs, squatting, prolonged sitting, cold weather.",
            "easing_factors": "Warm compress, gentle unweighted movement.",
            "radiation": "None.",
            "red_flags": "Visible genu varum deformity; crepitus on passive movement.",
            "social_history": "Retired teacher.",
            "past_medical_history": "Hypertension.",
            "diff_dx": "Knee Osteoarthritis vs. Degenerative Meniscal Tear vs. Pes Anserine Bursitis"
        },
        "Case 6: Patellar Instability": {
            "name": "Patricia", "region_label": "Knee", "forthcomingness": 3,
            "demeanor": "Teenage athlete, hesitant to allow patellar touch.",
            "chief_complaint": "Feeling that kneecap shifted outward and popped out of place when twisting.",
            "history_present_illness": "Twisted leg 3 days ago; kneecap visibly displaced laterally before sliding back in.",
            "location_pain": "Medial patellar retinaculum / lateral femoral condyle.",
            "onset_pain": "Acute event 72 hours ago.",
            "type_pain": "Sharp apprehension and localized medial pain.",
            "aggravating_factors": "Quadriceps contraction, pushing kneecap laterally.",
            "easing_factors": "Knee extension immobilizer, ice.",
            "radiation": "Anterior knee.",
            "red_flags": "Patellar apprehension test positive; medial retinacular tenderness.",
            "social_history": "Dancer.",
            "past_medical_history": "Generalized hypermobility.",
            "diff_dx": "Patellar Instability vs. ACL Sprain vs. Medial Meniscus Tear"
        }
    },
    "Ankle and foot": {
        "Case 1: Tibial Stress Syndrome": {
            "name": "Ryan", "region_label": "Ankle and foot", "forthcomingness": 4,
            "demeanor": "Runner, touching inner border of shin bone.",
            "chief_complaint": "Diffuse aching pain along the inner lower shin bone after increasing running volume.",
            "history_present_illness": "Ache started 3 weeks ago; worsens toward end of runs.",
            "location_pain": "Posteromedial border of distal third of tibia.",
            "onset_pain": "Gradual onset over 21 days.",
            "type_pain": "Diffuse dull ache along bone ridge (length >5 cm).",
            "aggravating_factors": "Running on hard pavement, jumping, dorsiflexing ankle.",
            "easing_factors": "Rest, ice along shin border.",
            "radiation": "Down inner shin.",
            "red_flags": "No focal point bone tenderness (diffuse length of tenderness rules out acute focal fracture).",
            "social_history": "Cross-country runner.",
            "past_medical_history": "Overpronation.",
            "diff_dx": "Tibial Stress Syndrome ('Shin Splints') vs. Tibial Stress Fracture vs. Exertional Compartment Syndrome"
        },
        "Case 2: Exertional Compartment Syndrome": {
            "name": "Sophia", "region_label": "Ankle and foot", "forthcomingness": 3,
            "demeanor": "Military cadet, holding tight anterolateral shin.",
            "chief_complaint": "Tightness, fullness, and foot numbness that occurs strictly 15 minutes into running and resolves completely with rest.",
            "history_present_illness": "Recurrent pattern over past 2 months during conditioning marches.",
            "location_pain": "Anterolateral muscular compartment of lower leg.",
            "onset_pain": "Exercise-induced predictable onset.",
            "type_pain": "Ischemic tight squeezing pressure, dorsal foot numbness.",
            "aggravating_factors": "Sustained high-intensity running.",
            "easing_factors": "Stopping exercise completely for 20 minutes.",
            "radiation": "Dorsum of foot.",
            "red_flags": "Symptoms clear completely at rest; pulse present throughout.",
            "social_history": "Military recruit.",
            "past_medical_history": "None.",
            "diff_dx": "Exertional Compartment Syndrome vs. Tibial Stress Syndrome vs. Popliteal Artery Entrapment"
        },
        "Case 3: Lateral Ankle Sprain": {
            "name": "Lucas", "region_label": "Ankle and foot", "forthcomingness": 3,
            "demeanor": "Limping, wearing elastic ankle sleeve.",
            "chief_complaint": "Outer ankle swelling and bruising after rolling ankle inward playing basketball.",
            "history_present_illness": "Inverted ankle 2 days ago; immediate lateral swelling.",
            "location_pain": "Anterior talofibular ligament (ATFL) lateral ankle.",
            "onset_pain": "Acute inversion trauma 48 hours ago.",
            "type_pain": "Sharp pain on weight-bearing, dull throbbing at rest.",
            "aggravating_factors": "Inverting foot, walking on uneven ground.",
            "easing_factors": "Rest, Ice, Compression, Elevation.",
            "radiation": "Lateral foot.",
            "red_flags": "Ottawa Ankle Rules negative (able to bear weight 4 steps; malleoli non-tender).",
            "social_history": "Basketball player.",
            "past_medical_history": "Prior ankle sprain 2 years ago.",
            "diff_dx": "Lateral Ankle Sprain vs. High Ankle Sprain vs. 5th Metatarsal Fracture"
        },
        "Case 4: High Ankle Sprain": {
            "name": "Oliver", "region_label": "Ankle and foot", "forthcomingness": 3,
            "demeanor": "Hockey player, non-weight bearing on foot.",
            "chief_complaint": "Severe pain above the ankle joint line after foot was twisted outward in tackle.",
            "history_present_illness": "Foot forced into external rotation 4 days ago during game.",
            "location_pain": "Anterior inferior tibiofibular syndesmosis (above ankle joint line).",
            "onset_pain": "Acute external rotation trauma 4 days ago.",
            "type_pain": "Sharp severe pain above ankle, total inability to bear weight.",
            "aggravating_factors": "External rotation of foot, ankle dorsiflexion, squeezing shin bones together.",
            "easing_factors": "Rigid boot, non-weight bearing with crutches.",
            "radiation": "Up lower leg shin.",
            "red_flags": "Squeeze test and external rotation stress test positive.",
            "social_history": "Hockey player.",
            "past_medical_history": "None.",
            "diff_dx": "High Ankle Sprain (Syndesmotic Tear) vs. Lateral Ankle Sprain vs. Maisonneuve Fracture"
        },
        "Case 5: Plantar Fasciopathy": {
            "name": "Penelope", "region_label": "Ankle and foot", "forthcomingness": 4,
            "demeanor": "Wincing during initial steps across the room.",
            "chief_complaint": "Agonizing sharp heel pain during the very first steps out of bed in the morning.",
            "history_present_illness": "Heel pain started 2 months ago after standing long hours on concrete floors in flat shoes.",
            "location_pain": "Plantar aspect of calcaneal medial tubercle.",
            "onset_pain": "Gradual onset over 8 weeks.",
            "type_pain": "Sharp knife-like pain initially, eases into dull ache after 10 minutes walking.",
            "aggravating_factors": "First steps in morning, standing after sitting, barefoot on tile.",
            "easing_factors": "Moderate walking warm-up, supportive arch shoes, frozen bottle rolling.",
            "radiation": "Medial foot arch.",
            "red_flags": "No calf swelling; no systemic joint swelling.",
            "social_history": "Retail manager.",
            "past_medical_history": "BMI 29.",
            "diff_dx": "Plantar Fasciopathy vs. Calcaneal Stress Fracture vs. Tarsal Tunnel Syndrome"
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
        f"- DO NOT reveal your diagnosis or explicit medical anatomical terms unless describing what a previous doctor told you.\n"
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
    st.write("Select a joint domain and specific patient case to edit attributes permanently.")
    
    cat_col, case_col = st.columns(2)
    with cat_col:
        selected_category = st.selectbox("1. Select Joint Domain:", list(st.session_state.case_library.keys()))
    with case_col:
        selected_case_key = st.selectbox("2. Select Patient Case:", list(st.session_state.case_library[selected_category].keys()))
        
    case_data = st.session_state.case_library[selected_category][selected_case_key]
    
    st.markdown("---")
    
    with st.form("admin_case_form"):
        st.subheader(f"Editing: {case_data['name']} ({selected_category})")
        
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
            e_diff = st.text_area("Differential Diagnosis Framework (Faculty Notes)", value=case_data.get("diff_dx", ""))
            
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
            st.success(f"Case '{e_name}' in {selected_category} permanently saved!")

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
    st.write("Complete a subjective history on the assigned patient. When you are ready to conclude the encounter, click **Input Differential Diagnoses** below.")
    
    col_cat, col_case = st.columns(2)
    with col_cat:
        student_category = st.selectbox("Select Joint Category:", list(st.session_state.case_library.keys()))
    with col_case:
        student_case_key = st.selectbox("Select Patient Case:", list(st.session_state.case_library[student_category].keys()))
        
    active_case = st.session_state.case_library[student_category][student_case_key]
    
    unique_case_id = f"{student_category}_{student_case_key}"
    if "last_chosen_case_id" not in st.session_state or st.session_state.last_chosen_case_id != unique_case_id:
        st.session_state.messages = []
        st.session_state.differentials_submitted = False
        st.session_state.submitted_differentials = ["", "", ""]
        st.session_state.last_chosen_case_id = unique_case_id

    st.info(f"📋 **Current Active Case:** Patient {active_case['name']} — *{student_case_key}*")
    
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
                dx1 = st.text_input("Differential Diagnosis 1 (Primary):", placeholder="e.g., De-Quervains Tenosynovitis")
                dx2 = st.text_input("Differential Diagnosis 2:", placeholder="e.g., Scaphoid Fracture")
                dx3 = st.text_input("Differential Diagnosis 3:", placeholder="e.g., 1st CMC Osteoarthritis")
                
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
            export_string += f"Case Title: {student_case_key}\n"
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
                file_name=f"MSK_Assessment_{st.session_state.ccid}_Patient_{active_case['name']}.txt",
                mime="text/plain"
            )