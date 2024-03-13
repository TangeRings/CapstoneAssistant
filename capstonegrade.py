import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

st.title('Capstone 2 Midterm Feedback')

# Function to create a block for each evaluation rubric
def create_evaluation_block(rubric_name, description, score_name, improvement_name, strength_name):
    st.header(rubric_name)
    st.markdown(description)
    score_options = ['Select'] + [str(num) for num in range(1, 11)]
    score = st.radio(score_name, options=score_options, key=f"score_{rubric_name}", horizontal=True)
    improvement = st.text_area("Points to Consider for Improvement", key=f"improve_{rubric_name}")
    strength = st.text_area("Areas of Strength", key=f"strength_{rubric_name}")
    return score, improvement, strength


# Input fields
col1, col2 = st.columns([1, 1])
with col1:
    instructor_name = st.text_input("Instructor Name", placeholder="Enter the instructor's name")

col3, col4 = st.columns(2)
with col3:
    student_name = st.text_input("Student Name", placeholder="Enter the student's name", key='student_name')
with col4:
    project_name = st.text_input("Project Name", placeholder="Enter the project name")


# Detailed rubric descriptions with formatting
rubrics = {
    "1.Evidence of Value Creation": """
    **User/prototype testing process that supports your insights and value map including how you are measuring that value and impact. Use of Prototypes & MVP to test.**
    - Validation of customer/user needs
    - Benchmarking against existing solutions
    - Quantitative metrics/data demonstrating improvement
    - Qualitative feedback from users/experts/partners
    """,
    "2.Connection to Business Context": """
    **Understanding of Commercial context and demand for solution**
    - Market analysis - size, competitors, trends
    - Brandenburger Value map (not value proposition canvas)
    - Business model canvas (if advised by mentor)
    - Intellectual property considerations
    - Commercialization/Impact plan
    - Financial / sustainability projections
    - Potential funding sources/investors
    """,
    "3.Spoken Presentation": """
    **Current ability to present your project to others**
    - Clarity of speech and enunciation
    - Pacing and ability to stay within time constraints
    - Poise and presence
    - Ability to effectively respond to questions
    """,
    "4.Visual Communication and Design": """
    **How the visual communication impacts understanding.**
    - Visual appeal - use of color, images, layout, and white space to clearly communicate
    - Clarity and readability of charts/graphs/diagrams
    - Use of appropriate consistent formatting
    - Quality of physical/virtual prototype/model
    """
}

# Create blocks for each evaluation rubric and collect scores and feedback
scores_and_feedback = [create_evaluation_block(rubric, description, f"Score for {rubric}", f"Improvement for {rubric}", f"Strength for {rubric}") for rubric, description in rubrics.items()]

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def generate_pdf(data, scores_feedback):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    # Define custom styles
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('bold_style', parent=styles['Normal'], fontName='Helvetica-Bold')

    Story = []

    # Helper function to add paragraphs to the Story list with dynamic spacing
    def add_paragraph(text, style, space_after=0.1):
        Story.append(Paragraph(text, style))
        Story.append(Spacer(1, space_after * inch))  # Dynamically add vertical space after each paragraph

    # Basic Info
    add_paragraph(f"<b>Instructor Name:</b> {data['Instructor Name']}", bold_style)
    add_paragraph(f"<b>Student Name:</b> {data['Student Name']}", bold_style)
    add_paragraph(f"<b>Project Name:</b> {data['Project Name']}", bold_style, space_after=0.2)

    # Scores, Improvements, and Strengths
    for rubric_index, (rubric, details) in enumerate(scores_feedback.items(), start=1):
        score, improvement, strength = details
        add_paragraph(f"<b>{rubric} - Score:</b> {score if score != 'Select' else 'Not Selected'}", bold_style)
        add_paragraph(f"<b>Improvement:</b> {improvement if improvement else 'None'}", normal_style)
        add_paragraph(f"<b>Strength:</b> {strength if strength else 'None'}", normal_style, space_after=0.2 if rubric_index < len(scores_feedback) else 0.1)

    doc.build(Story)
    buffer.seek(0)
    return buffer.getvalue()


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Function to send email
def send_email(student_email, pdf_data):
    # Email configuration
    from_email = "cw3715@nyu.edu"  # Change this to your email address
    password = "wcptonmscvnffuut"  # Change this to your email password
    to_email = student_email

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Capstone 2 Midterm Feedback"

    # Attach the PDF to the email
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Capstone_Feedback.pdf"')
    msg.attach(part)

    # Connect to the SMTP server and send the email
    # Connect to the SMTP server and send the email
   

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        print(f"Failed to send email: {e}")


# Submit Review Button
if st.button('Submit Review', key='submit_review'):
    # Check required fields: student name and that all scores are selected
    if student_name and all(score != 'Select' for score, _, _ in scores_and_feedback):
        review_data = {
            "Instructor Name": instructor_name,
            "Student Name": student_name,
            "Project Name": project_name,
        }

        # Prepare scores, improvements, and strengths
        scores_feedback_dict = {}
        for rubric, (score, improvement, strength) in zip(rubrics.keys(), scores_and_feedback):
            scores_feedback_dict[rubric] = (score, improvement if improvement else "None", strength if strength else "None")

        # Generate PDF
        pdf_bytes = generate_pdf(review_data, scores_feedback_dict)

        # Provide a download link for the PDF
        st.download_button(
            label="Download Review PDF",
            data=pdf_bytes,
            file_name=f"{student_name}_review.pdf",
            mime="application/pdf"
        )

        # Email input field
        student_email = st.text_input("Enter Your Email Address", key='student_email')

        # Send email button
        if st.button("Send Email"):
            if student_email:
                # Send email with PDF attachment
                send_email(student_email, pdf_bytes)
                st.success("Email sent successfully!")
            else:
                st.error("Please enter your email address.")
    else:
        # If required fields are missing
        st.error("Please fill in all required fields (student name and all scores). Ensure no score is set to 'Select'.")






