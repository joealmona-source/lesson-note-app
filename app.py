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
        
    ref_materials = st.text_area("Reference Materials", value="New School Physics, WAEC Curriculum")

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
    
    # 1. MATHEMATICS
    if "math" in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus Materials (CONTENT DELIVERY):
           **INSTRUCTION:** Describe the TEACHING METHOD for {pers} periods.
           - Describe how the teacher introduces the formula/concept.
           - Mention that the teacher solves examples on the board step-by-step.
           - **DO NOT** just list the math. Explain HOW it is taught.
           - **AT LEAST 3 SOLVED WORKED EXAMPLES** (The teacher solves these on the board).
        """
        board_summary_section = "" # No Board Summary for Math

    # 2. ENGLISH LANGUAGE (Grammar/Drill)
    elif "english" in subj.lower() and "literature" not in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus Materials (CONTENT DELIVERY):
           **INSTRUCTION:** Describe the TEACHING METHOD for {pers} periods.
           - Describe how the teacher explains the rule using sentence examples.
           - Describe how the teacher engages students to form their own sentences.
           - **CLASS EXERCISES:** 3-5 quick drill questions per period.
        """
        board_summary_section = "" # No Board Summary for English

    # 3. ALL OTHER SUBJECTS (Science, Arts, Comm, etc.)
    else:
        special_instruction = f"""
        * IV. Presentation of Stimulus Materials (CONTENT DELIVERY):
           **INSTRUCTION:** This section must be ENGAGING and METHODOLOGICAL.
           - Split into {pers} distinct Periods/Days.
           - **DO NOT** just write the notes here. Instead, describe **HOW** the teacher explains the subtopics.
           - Example: "The teacher explains [concept] by using an analogy of..." or "The teacher demonstrates..."
           - Ensure the explanation covers the depth of the subtopic but focuses on the delivery method.
        """
        
        # Smart Summary Logic (Includes Definitions + Formulas if needed)
        board_summary_section = f"""
        9. **Board Summary**: (EXTREMELY IMPORTANT: This is the CONTENT students copy).
           - This section MUST contain the **Full Notes**: Definitions, Detailed Explanations, and Key Points.
           - **LOGIC CHECK:** Look at the Topic "{topic}".
           - **IF** the topic involves **Calculations/Formulas** (Physics, Econ, etc.), you **MUST** add:
             1. All derived Formulas.
             2. **TWO (2) SOLVED CALCULATION EXAMPLES** (Data, Formula, Substitution, Answer).
        """

    # --- THE FINAL PROMPT STRUCTURE ---
    return f"""
    Act as a {sect} {subj} curriculum expert in Nigeria. 
    Generate a fully comprehensive lesson note for {cls}.
    
    INPUT DATA:
    - Week: {week_num} | Topic: {topic} | Subtopics: {subs}
    - Sex: {sex} | Avg Age: {age} | Periods: {pers} | Duration: {dur}
    - Ref Materials: {ref}

    STRICT OUTPUT FORMAT (Do not skip sections):
    1.  **Header Details**: Week, Subject, Class, Topic, Subtopics, Sex, Average Age, Periods, Duration.
    2.  **Behavioural Objectives**: (Use action verbs like Define, Mention, List).
    3.  **Instructional Materials**: (List tangible objects or charts).
    4.  **Reference Materials**.
    5.  **Entry Behaviour**: (Describe what students already know).
    6.  **Procedures**:
        * I. Gaining students attention: (Describe a specific story, object, or scenario to grab interest).
        * II. Informing students of the objectives.
        * III. Recall of previous knowledge: (3 linking questions).
        {special_instruction}
        * V. Eliciting the desired behaviour: (Class activity/discussion).
        * VI. Providing feedback: (How the teacher corrects/praises).
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
                        {"role": "system", "content": "You are an experienced Nigerian teacher. You are detailed and follow the 6-step procedure strictly. For Step IV, describe the TEACHING METHOD, not just the notes."},
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

