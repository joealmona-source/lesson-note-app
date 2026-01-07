import streamlit as st
import openai
from docx import Document
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Exquisite Lesson Notes",
    page_icon="📚",
    layout="wide"
)

# --- SETUP: USE GROQ (FREE & FAST) ---
try:
    client = openai.OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
except:
    st.error("⚠️ Key Error. Please check your Secrets for GROQ_API_KEY.")
    st.stop()

# --- SIDEBAR: CLASS DATA ---
with st.sidebar:
    st.title("⚙️ Class Profile")
    st.success("✅ System Status: Online & Free")
    
    st.header("General Info")
    section = st.selectbox("Section", ["Nursery", "Primary", "JSS", "SSS"])
    class_level = st.text_input("Class", value="SSS 1")
    subject = st.text_input("Subject", value="Physics")
    
    col1, col2 = st.columns(2)
    with col1:
        sex = st.text_input("Sex", value="Mixed")
        periods = st.number_input("Periods", min_value=1, value=4)
    with col2:
        avg_age = st.text_input("Avg Age", value="15 years")
        duration = st.text_input("Duration", value="40 mins")
        
    ref_materials = st.text_area("Reference Materials", value="New General Mathematics, WAEC Curriculum")

# --- MAIN PAGE ---
st.title("🇳🇬 Exquisite Lesson Notes by Joseph Almona")
st.markdown("Generate comprehensive lesson notes in line with the **National Curriculum**.")

# Input for the specific week
st.subheader("📝 Current Lesson Details")
c1, c2 = st.columns([1, 3])
with c1:
    week_num = st.number_input("Week Number", min_value=1, value=1)
with c2:
    topic = st.text_input("Topic", placeholder="e.g. Projectiles")

subtopics = st.text_area("Subtopics", placeholder="e.g. Concept of Projectile Motion, Time of Flight, Maximum Height...")

# --- SMART PROMPT LOGIC ---
def build_prompt(subj, topic, subs, sect, cls, sex, age, pers, dur, ref):
    
    # 1. MATHEMATICS (Guardrail: Strict NO Board Summary)
    # Checks for 'math' to catch 'Maths', 'Mathematics', 'Further Math'
    if "math" in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL: WRITE A FULL LECTURE.**
           - Split into {pers} distinct Periods/Days.
           - Provide EXTENSIVE detailed explanations.
           - **AT LEAST 3 SOLVED WORKED EXAMPLES** per period (Step-by-step calculations).
           - **DO NOT** generate a Board Summary. The examples here serve as the notes.
        """
        board_summary_section = "" # <--- FORCED EMPTY

    # 2. ENGLISH LANGUAGE (Guardrail: Strict NO Board Summary)
    # Checks for 'english' but ensures it is NOT 'literature'
    elif "english" in subj.lower() and "literature" not in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL: DETAILED GRAMMAR EXPLANATION.**
           - Split into {pers} distinct Periods/Days.
           - Explain the rules elaborately with multiple sentence examples.
           - **CLASS EXERCISES:** 3-5 quick drill questions per period.
           - **DO NOT** generate a Board Summary.
        """
        board_summary_section = "" # <--- FORCED EMPTY

    # 3. ALL OTHER SUBJECTS (Physics, Econ, Basic Tech, Lit, Gov, etc.)
    # This uses the "Smart Detection" for calculations.
    else:
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL: WRITE A FULL LECTURE (NOT OUTLINES).**
           - Split into {pers} distinct Periods/Days.
           - **BE VERBOSE.** Write out full paragraphs of teaching content, definitions, and theories.
           - If the topic involves calculations (like in Physics, Economics, Accounting), explain the formula clearly here.
        """
        
        # Smart Summary Logic
        board_summary_section = f"""
        9. **Board Summary**: (EXTREMELY IMPORTANT: This is the note students will copy).
           - **LOGIC CHECK:** Look at the Topic "{topic}".
           - **IF** the topic involves **Calculations, Formulas, or Accounts** (e.g., Physics, Economics, Basic Tech, Accounting), you **MUST** include:
             1. All relevant Formulas/Equations.
             2. **TWO (2) SOLVED CALCULATION EXAMPLES** with clear steps.
           - **IF** the topic is purely **Theoretical/Descriptive** (e.g., Biology, History, Government), provide a detailed text summary with subheadings.
        """

    # --- THE FINAL PROMPT STRUCTURE ---
    return f"""
    Act as a {sect} {subj} curriculum expert in Nigeria. 
    Generate a fully comprehensive lesson note for {cls}.
    
    INPUT DATA:
    - Week: {week_num} | Topic: {topic} | Subtopics: {subs}
    - Sex: {sex} | Avg Age: {age} | Periods: {pers} | Duration: {dur}
    - Ref Materials: {ref}

    STRICT OUTPUT FORMAT:
    1.  **Header Details**: Week, Class, Topic, Subtopics, Sex, Average Age, Periods, Duration.
    2.  **Behavioural Objectives**: (Use action verbs like Define, Mention, List. Do not use 'Know' or 'Understand').
    3.  **Instructional Materials**: (List tangible objects or charts).
    4.  **Reference Materials**.
    5.  **Entry Behaviour**: (Describe what the students already know from their daily lives that relates to this topic).
    6.  **Procedures**:
        * I. Gaining students attention: (DO NOT just say "Greet students". Describe a specific short story, a physical demonstration, or a catchy real-world scenario to grab their interest immediately).
        * II. Informing students of the objectives: (Explain clearly what they will learn and WHY it is important to them).
        * III. Recall of previous knowledge: (List 3 specific questions the teacher asks to link the last topic to this new one).
        {special_instruction}
        * V. Eliciting the desired behaviour: (Describe a specific class activity, discussion, or classwork where students apply what they learnt).
        * VI. Providing feedback: (Explain how the teacher corrects wrong answers and commends correct ones. Give examples of praise).
    7.  **Assessment Questions**: (5 likely exam questions).
    8.  **Assignments**: (3 likely exam questions).
    {board_summary_section}
    """

# --- GENERATION LOGIC ---
if st.button("Generate Lesson Note", type="primary"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        prompt_text = build_prompt(subject, topic, subtopics, section, class_level, sex, avg_age, periods, duration, ref_materials)

        with st.spinner("Consulting the curriculum... this may take about 30 seconds..."):
            try:
                # WE USE GROQ'S NEWEST MODEL
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile", 
                    messages=[
                        {"role": "system", "content": "You are an experienced Nigerian teacher. You are NOT lazy. You write EXTENSIVE, DETAILED, and ELABORATE lesson notes. You write full lectures, not outlines."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                st.success("Lesson Note Generated Successfully!")
                st.markdown("---")
                st.markdown(result)
                
                # Word Doc
                doc = Document()
                doc.add_heading(f"Lesson Note: {topic}", 0)
                clean_text = result.replace("**", "").replace("###", "") 
                doc.add_paragraph(clean_text)
                
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.download_button(
                    label="📄 Download as Word Document",
                    data=buffer,
                    file_name=f"{subject}_{week_num}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Error: {e}")

