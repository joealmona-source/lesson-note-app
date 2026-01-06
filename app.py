import streamlit as st
import openai
from docx import Document  # <--- NEW
from io import BytesIO     # <--- NEW

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Lesson Note Generator by Tr Joseph",
    page_icon="📚",
    layout="wide"
)

# --- SIDEBAR: SETTINGS & CLASS DATA ---
with st.sidebar:
    st.title("⚙️ Class Profile")
    
    # API Key Handling (See instructions below on how to hide this later)
    api_key = st.text_input("OpenAI API Key", type="password", help="Ask the admin for the key if you don't have one.")
    
    st.markdown("---")
    st.header("General Info")
    section = st.selectbox("Section", ["Nursery", "Primary", "JSS", "SSS"])
    class_level = st.text_input("Class", value="JSS 2")
    subject = st.text_input("Subject", value="Basic Science")
    
    col1, col2 = st.columns(2)
    with col1:
        sex = st.text_input("Sex", value="Mixed")
        periods = st.number_input("Periods", min_value=1, value=3)
    with col2:
        avg_age = st.text_input("Avg Age", value="12 years")
        duration = st.text_input("Duration", value="40 mins")
        
    ref_materials = st.text_area("Reference Materials", value="New General Mathematics, UBE Standard Curriculum")

# --- MAIN PAGE ---
st.title("🇳🇬 Lesson Note Generator by Tr Joseph")
st.markdown("Generate comprehensive lesson notes in line with the **National Curriculum**.")

# Input for the specific week
st.subheader("📝 Current Lesson Details")
c1, c2 = st.columns([1, 3])
with c1:
    week_num = st.number_input("Week Number", min_value=1, value=1)
with c2:
    topic = st.text_input("Topic", placeholder="e.g. Living and Non-Living Things")

subtopics = st.text_area("Subtopics", placeholder="e.g. 1. Definition of Matter\n2. States of Matter\n3. Characteristics of Solid, Liquid, and Gas")

# --- GENERATION LOGIC ---
if st.button("Generate Lesson Note", type="primary"):
    if not api_key:
        st.error("Please enter an API Key in the sidebar to proceed.")
    elif not topic:
        st.warning("Please enter a topic.")
    else:
        # Initialize Client
        client = openai.OpenAI(api_key=api_key)
        
        # The prompt with your EXACT structure
        prompt_text = f"""
        Act as a {section} {subject} curriculum expert in Nigeria. 
        Generate a fully comprehensive lesson note for {class_level}.
        
        INPUT DATA:
        - Week: {week_num}
        - Topic: {topic}
        - Subtopics: {subtopics}
        - Sex: {sex} | Avg Age: {avg_age}
        - Periods: {periods} | Duration: {duration}
        - Ref Materials: {ref_materials}

        STRICT OUTPUT FORMAT (Do not deviate):
        1.  **Header Details**: Week, Class, Topic, Subtopics, Sex, Average Age, Periods, Duration.
        2.  **Behavioural Objectives**: (Use action verbs).
        3.  **Instructional Materials**.
        4.  **Reference Materials**.
        5.  **Entry Behaviour**.
        6.  **Procedures**:
            * I. Gaining students attention
            * II. Informing students of the objectives
            * III. Recall of previous knowledge
            * IV. Presentation of Stimulus materials (DETAILED EXPLANATION of content. **Split this into {periods} distinct periods/days**).
            * V. Eliciting the desired behaviour
            * VI. Providing feedback
        7.  **Assessment Questions**: (5 likely exam questions).
        8.  **Assignments**: (3 likely exam questions).
        9.  **Board Summary**: (EXTREMELY IMPORTANT: This must be an ELABORATE and DETAILED summary suitable for students to copy as notes. Do not summarize briefly. Use full paragraphs, clear subheadings for every subtopic, and explain concepts in depth. Include at least 3 solved examples or illustrations where applicable).
        """

        with st.spinner("Consulting the curriculum... this may take about 30 seconds..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o", # Use gpt-3.5-turbo if you want to save money
                    messages=[
                        {"role": "system", "content": "You are a highly experienced Nigerian teacher and curriculum developer. You are detailed, formal, and strictly follow the requested structure."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                # Display Result
                st.success("Lesson Note Generated Successfully!")
                st.markdown("---")
                st.markdown(result)
                
                # Download Button
                filename = f"Week_{week_num}_{subject}_{class_level}.txt".replace(" ", "_")
               
            # --- WORD DOCUMENT GENERATION ---
            doc = Document()
            doc.add_heading(f"Lesson Note: {topic}", 0)

            # Add the generated content to the Word file
            doc.add_paragraph(result)

            # Save to memory buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            # Download Button for Word
            st.download_button(
                label="📄 Download as Word Document",
                data=buffer,
                file_name=f"{subject}_{week_num}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

                
            except Exception as e:
                st.error(f"An error occurred: {e}")
