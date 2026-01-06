import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Exquisite Lesson Notes by Joseph Almona",
    page_icon="📚",
    layout="wide"
)

# --- SETUP GOOGLE GEMINI ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Google API Key not found. Please check your Secrets settings.")
    st.stop()

# --- SIDEBAR: CLASS DATA ---
with st.sidebar:
    st.title("⚙️ Class Profile")
    st.info("✅ System Status: Online & Free")
    
    st.header("General Info")
    section = st.selectbox("Section", ["Nursery", "Primary", "JSS", "SSS"])
    class_level = st.text_input("Class", value="JSS 2")
    subject = st.text_input("Subject", value="Mathematics")
    
    col1, col2 = st.columns(2)
    with col1:
        sex = st.text_input("Sex", value="Mixed")
        periods = st.number_input("Periods", min_value=1, value=3)
    with col2:
        avg_age = st.text_input("Avg Age", value="12 years")
        duration = st.text_input("Duration", value="40 mins")
        
    ref_materials = st.text_area("Reference Materials", value="New General Mathematics, UBE Standard Curriculum")

# --- MAIN PAGE ---
st.title("🇳🇬 Exquisite Lesson Notes by Joseph Almona")
st.markdown("Generate comprehensive lesson notes in line with the **National Curriculum**.")

# Input for the specific week
st.subheader("📝 Current Lesson Details")
c1, c2 = st.columns([1, 3])
with c1:
    week_num = st.number_input("Week Number", min_value=1, value=1)
with c2:
    topic = st.text_input("Topic", placeholder="e.g. Quadratic Equations")

subtopics = st.text_area("Subtopics", placeholder="e.g. Factorization, Completing the Square, Formula Method")

# --- SMART PROMPT LOGIC ---
def build_prompt(subj, topic, subs, sect, cls, sex, age, pers, dur, ref):
    
    # 1. MATHEMATICS STRUCTURE (Calculation focus)
    if "math" in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL:** Split this section into {pers} distinct Periods/Days.
           **FOR EACH PERIOD, YOU MUST INCLUDE:**
           - Detailed explanation of the subtopic.
           - **AT LEAST 3 SOLVED WORKED EXAMPLES** (Step-by-step calculations).
           - **DO NOT** generate a Board Summary at the end. The examples here serve as the notes.
        """
        end_section = "9. **Weekly Assignment**: (5 practice calculation questions)."

    # 2. ENGLISH LANGUAGE (Grammar/Drill focus) - BUT EXCLUDE LITERATURE
    # We check if it is English BUT NOT Literature
    elif "english" in subj.lower() and "literature" not in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL:** Split this section into {pers} distinct Periods/Days.
           **FOR EACH PERIOD, YOU MUST INCLUDE:**
           - Explanation of the grammar/speech/reading rule.
           - **CLASS EXERCISES:** Provide 3-5 quick drill questions for students to solve in class immediately after the explanation.
           - **DO NOT** generate a Board Summary at the end.
        """
        end_section = "9. **Weekly Assignment**: (Write an essay or answer comprehensive questions)."

    # 3. LITERATURE & OTHER SUBJECTS (Standard Note focus)
    # Literature falls here, so it gets the Elaborate Board Summary.
    else:
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           - Split this section into {pers} distinct Periods/Days.
           - Explain concepts clearly and in detail.
        """
        end_section = """
        9. **Board Summary**: (EXTREMELY IMPORTANT: This must be an ELABORATE and DETAILED summary suitable for students to copy into their notes. Do not summarize briefly. Use full paragraphs, clear subheadings for every subtopic, and explain concepts in depth. Include at least 3 solved examples or illustrations where applicable).
        """

    # Combine into the final prompt
    return f"""
    Act as a {sect} {subj} curriculum expert in Nigeria. 
    Generate a fully comprehensive lesson note for {cls}.
    
    INPUT DATA:
    - Week: {week_num} | Topic: {topic} | Subtopics: {subs}
    - Sex: {sex} | Avg Age: {age} | Periods: {pers} | Duration: {dur}
    - Ref Materials: {ref}

    STRICT OUTPUT FORMAT:
    1.  **Header Details**: Week, Class, Topic, Subtopics, Sex, Average Age, Periods, Duration.
    2.  **Behavioural Objectives**: (Use action verbs).
    3.  **Instructional Materials**.
    4.  **Reference Materials**.
    5.  **Entry Behaviour**.
    6.  **Procedures**:
        * I. Gaining students attention
        * II. Informing students of the objectives
        * III. Recall of previous knowledge
        {special_instruction}
        * V. Eliciting the desired behaviour
        * VI. Providing feedback
    7.  **Assessment Questions**: (5 likely exam questions).
    8.  {end_section}
    """

# --- GENERATION LOGIC ---
if st.button("Generate Lesson Note", type="primary"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        # Build the smart prompt based on the subject
        prompt_text = build_prompt(subject, topic, subtopics, section, class_level, sex, avg_age, periods, duration, ref_materials)

        with st.spinner("Consulting the curriculum... this may take about 30 seconds..."):
            try:
                # Use Google's Gemini 1.5 Flash model
                model = genai.GenerativeModel('gemini-pro')
                
                response = model.generate_content(prompt_text)
                result = response.text
                
                # Display Result
                st.success("Lesson Note Generated Successfully!")
                st.markdown("---")
                st.markdown(result)
                
                # --- WORD DOCUMENT GENERATION ---
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
                st.error(f"An error occurred: {e}")

