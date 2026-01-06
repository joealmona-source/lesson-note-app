import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Exquisite Lesson Notes",
    page_icon="📚",
    layout="wide"
)

# --- SETUP GOOGLE GEMINI ---
try:
    # 1. Get the Key
    api_key = st.secrets["GOOGLE_API_KEY"]
    # 2. Configure Google
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Key Error. Please check your Secrets on Streamlit.")
    st.stop()

# --- SIDEBAR: CLASS DATA ---
with st.sidebar:
    st.title("⚙️ Class Profile")
    st.success("✅ System Status: Online & Free")
    
    st.header("General Info")
    section = st.selectbox("Section", ["Nursery", "Primary", "JSS", "SSS"])
    class_level = st.text_input("Class", value="JSS 3")
    subject = st.text_input("Subject", value="Mathematics")
    
    col1, col2 = st.columns(2)
    with col1:
        sex = st.text_input("Sex", value="Mixed")
        periods = st.number_input("Periods", min_value=1, value=5)
    with col2:
        avg_age = st.text_input("Avg Age", value="13 years")
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
    topic = st.text_input("Topic", placeholder="e.g. Factorization")

subtopics = st.text_area("Subtopics", placeholder="e.g. Factorization of simple algebraic expressions...")

# --- SMART PROMPT LOGIC ---
def build_prompt(subj, topic, subs, sect, cls, sex, age, pers, dur, ref):
    
    # 1. MATHEMATICS
    if "math" in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL:** Split this section into {pers} distinct Periods/Days.
           **FOR EACH PERIOD, YOU MUST INCLUDE:**
           - Detailed explanation of the subtopic.
           - **AT LEAST 3 SOLVED WORKED EXAMPLES** (Step-by-step calculations).
           - **DO NOT** generate a Board Summary.
        """
        end_section = "9. **Weekly Assignment**: (5 practice calculation questions)."

    # 2. ENGLISH (BUT NOT LITERATURE)
    elif "english" in subj.lower() and "literature" not in subj.lower():
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           **CRITICAL:** Split this section into {pers} distinct Periods/Days.
           **FOR EACH PERIOD, YOU MUST INCLUDE:**
           - Explanation of the rule.
           - **CLASS EXERCISES:** 3-5 quick drill questions.
           - **DO NOT** generate a Board Summary.
        """
        end_section = "9. **Weekly Assignment**: (Write an essay or answer comprehensive questions)."

    # 3. LITERATURE & OTHERS
    else:
        special_instruction = f"""
        * IV. Presentation of Stimulus materials (CONTENT DELIVERY):
           - Split this section into {pers} distinct Periods/Days.
           - Explain concepts clearly.
        """
        end_section = """
        9. **Board Summary**: (EXTREMELY IMPORTANT: ELABORATE and DETAILED summary suitable for copying. Use full paragraphs and subheadings).
        """

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
        prompt_text = build_prompt(subject, topic, subtopics, section, class_level, sex, avg_age, periods, duration, ref_materials)

        with st.spinner("Consulting the curriculum... this may take about 30 seconds..."):
            try:
                # --- USE THE STANDARD MODEL ---
                # We use 'gemini-1.5-flash' because it is the current standard free model.
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                response = model.generate_content(prompt_text)
                result = response.text
                
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
                # If Flash fails, the error will show here.
                st.error(f"Error: {e}")
                st.info("Tip: If you see a 404 error, it means your API Key is not active.")

