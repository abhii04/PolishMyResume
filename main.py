import streamlit as st
import cohere
from fpdf import FPDF
import tempfile
import os

# Initialize Cohere client
cohere_api_key = st.secrets["cohere"]["api_key"]
co = cohere.Client(cohere_api_key)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Professional Resume', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def main():
    st.title("AI-Powered Resume Builder")
    st.image('img.png', use_column_width=True)

    # Initialize session state
    if 'personal_info' not in st.session_state:
        st.session_state.personal_info = {}
    if 'summary' not in st.session_state:
        st.session_state.summary = ""
    if 'experiences' not in st.session_state:
        st.session_state.experiences = []
    if 'education' not in st.session_state:
        st.session_state.education = []
    if 'skills' not in st.session_state:
        st.session_state.skills = ""

    # User input sections
    personal_info()
    summary()
    experience()
    education()
    skills()

    if st.button("Generate Professional Resume"):
        generate_resume()


def personal_info():
    st.header("Personal Information")
    st.session_state.personal_info['name'] = st.text_input("Full Name", st.session_state.personal_info.get('name', ''))
    st.session_state.personal_info['email'] = st.text_input("Email", st.session_state.personal_info.get('email', ''))
    st.session_state.personal_info['phone'] = st.text_input("Phone", st.session_state.personal_info.get('phone', ''))


def summary():
    st.header("Professional Summary")
    summary_text = st.text_area("Enter your professional summary", st.session_state.summary)
    if summary_text:
        st.session_state.summary = summary_text
        if st.button("Enhance Professional Summary"):
            with st.spinner("Generating enhanced summary..."):
                improved_summary = suggest_improvements(summary_text)
                st.session_state.summary = improved_summary
                st.write("Enhanced summary:", improved_summary)


def experience():
    st.header("Work Experience")
    num_experiences = st.number_input("Number of experiences", min_value=0, max_value=10,
                                      value=len(st.session_state.experiences))

    experiences = []
    for i in range(num_experiences):
        st.subheader(f"Experience {i + 1}")
        exp = st.session_state.experiences[i] if i < len(st.session_state.experiences) else {}
        company = st.text_input(f"Company {i + 1}", exp.get('company', ''))
        position = st.text_input(f"Position {i + 1}", exp.get('position', ''))
        start_date = st.date_input(f"Start Date {i + 1}", exp.get('start_date', None))
        end_date = st.date_input(f"End Date {i + 1}", exp.get('end_date', None))
        description = st.text_area(f"Description {i + 1}", exp.get('description', ''))

        if st.button(f"Enhance Description {i + 1}"):
            with st.spinner("Generating enhanced description..."):
                improved_description = improve_work_description(description)
                st.write("Enhanced description:", improved_description)
                description = improved_description

        experiences.append({
            'company': company,
            'position': position,
            'start_date': start_date,
            'end_date': end_date,
            'description': description
        })
    st.session_state.experiences = experiences


def education():
    st.header("Education")
    num_education = st.number_input("Number of educational entries", min_value=0, max_value=5,
                                    value=len(st.session_state.education))

    education = []
    for i in range(num_education):
        st.subheader(f"Education {i + 1}")
        edu = st.session_state.education[i] if i < len(st.session_state.education) else {}
        institution = st.text_input(f"Institution {i + 1}", edu.get('institution', ''))
        degree = st.text_input(f"Degree {i + 1}", edu.get('degree', ''))
        graduation_date = st.date_input(f"Graduation Date {i + 1}", edu.get('graduation_date', None))
        education.append({
            'institution': institution,
            'degree': degree,
            'graduation_date': graduation_date
        })
    st.session_state.education = education


def skills():
    st.header("Skills")
    st.session_state.skills = st.text_area("Enter your skills (comma-separated)", st.session_state.skills)
    if st.button("Suggest Additional Skills"):
        with st.spinner("Suggesting additional skills..."):
            suggested_skills = suggest_skills(st.session_state.skills)
            st.write("Suggested additional skills:", suggested_skills)


def generate_resume():
    pdf = PDF()
    pdf.add_page()

    # Personal Information
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, st.session_state.personal_info['name'], 0, 1, 'C')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 5,
             f"Email: {st.session_state.personal_info['email']} | Phone: {st.session_state.personal_info['phone']}", 0,
             1, 'C')
    pdf.ln(5)

    # Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Professional Summary', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 5, st.session_state.summary)
    pdf.ln(5)

    # Experience
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Work Experience', 0, 1)
    for exp in st.session_state.experiences:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 5, f"{exp['position']} - {exp['company']}", 0, 1)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 5, f"{exp['start_date']} - {exp['end_date']}", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 5, exp['description'])
        pdf.ln(5)

    # Education
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Education', 0, 1)
    for edu in st.session_state.education:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 5, edu['institution'], 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 5, f"{edu['degree']} - Graduated: {edu['graduation_date']}", 0, 1)
    pdf.ln(5)

    # Skills
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Skills', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 5, st.session_state.skills)

    # Save the PDF
    pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_output.name)

    # Provide download link
    with open(pdf_output.name, "rb") as file:
        st.download_button(
            label="Download Professional Resume (PDF)",
            data=file,
            file_name="professional_resume.pdf",
            mime="application/pdf"
        )

    # Clean up the temporary file
    os.unlink(pdf_output.name)


def suggest_improvements(text):
    response = co.generate(
        model='command-nightly',
        prompt=f"Enhance the following professional summary, making it more impactful, concise, and tailored for a resume:\n\n{text}\n\nEnhanced version:",
        max_tokens=150,
        temperature=0.7,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE')
    return response.generations[0].text.strip()


def improve_work_description(description):
    response = co.generate(
        model='command-nightly',
        prompt=f"Enhance the following work experience description for a resume, making it more impactful and using strong action verbs:\n\n{description}\n\nEnhanced version:",
        max_tokens=200,
        temperature=0.7,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE')
    return response.generations[0].text.strip()


def suggest_skills(current_skills):
    response = co.generate(
        model='command-nightly',
        prompt=f"Given the following skills for a resume:\n\n{current_skills}\n\nSuggest 5 additional relevant skills:",
        max_tokens=100,
        temperature=0.7,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE')
    return response.generations[0].text.strip()


if __name__ == "__main__":
    main()
