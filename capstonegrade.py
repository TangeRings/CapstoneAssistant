import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import gspread
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders
import json
from google.oauth2.service_account import Credentials
import gspread


# Initialize session state variables
if 'review_submitted' not in st.session_state:
    st.session_state.review_submitted = False
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'inferred_full_name' not in st.session_state:
    st.session_state.inferred_full_name = ""
if 'student_email' not in st.session_state:
    st.session_state.student_email = ""
    
student_info = {
    "Nicole": {"full_name": "Nicole Wang", "email": "cw3715@nyu.edu"},
    "Lucy": {"full_name": "Lucy Liu", "email": "nicolecheyennew@gmail.com"},
}


st.title('Capstone 2 Midterm Feedback')

# Function to create a block for each evaluation rubric
def create_evaluation_block(rubric_name, description, score_name, improvement_name, strength_name):
    st.header(rubric_name)
    st.markdown(description, unsafe_allow_html=True)  # Enable HTML rendering
    score_options = ['Select'] + [str(num) for num in range(1, 11)]
    score = st.radio(score_name, options=score_options, key=f"score_{rubric_name}", horizontal=True)
    improvement = st.text_area("Points to Consider for Improvement (<1000 words)", key=f"improve_{rubric_name}")
    strength = st.text_area("Areas of Strength (<1000 words)", key=f"strength_{rubric_name}")
    return score, improvement, strength


# Input fields
col1, col2 = st.columns([1, 1])
with col1:
    instructor_name = st.text_input("Feedback Provider", placeholder="Enter the feedback provider's name")

col3, col4 = st.columns(2)
with col3:
    student_name = st.text_input("Student First Name", placeholder="Enter the student's first name", key='student_name')
with col4:
    project_name = st.text_input("Project Name (can be short abbreviations)", placeholder="Enter the project name")


# Detailed rubric descriptions with formatting
rubrics = {
    "1.Evidence of Value Creation": """
    **User/prototype testing process that supports your insights and value map including how you are measuring that value and impact. Use of Prototypes & MVP to test.**
    <br><br><span style="color:red;">Suggested Rubrics Only (not all required)</span>
    - Validation of customer/user needs
    - Benchmarking against existing solutions
    - Quantitative metrics/data demonstrating improvement
    - Qualitative feedback from users/experts/partners
    """,
    "2.Connection to Business Context": """
    **Understanding of Commercial context and demand for solution**
    <br><br><span style="color:red;">Suggested Rubrics Only (not all required)</span>
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
    <br><br><span style="color:red;">Suggested Rubrics Only (not all required)</span>
    - Clarity of speech and enunciation
    - Pacing and ability to stay within time constraints
    - Poise and presence
    - Ability to effectively respond to questions
    """,
    "4.Visual Communication and Design": """
    **How the visual communication impacts understanding.**
    <br><br><span style="color:red;">Suggested Rubrics Only (not all required)</span>
    - Visual appeal - use of color, images, layout, and white space to clearly communicate
    - Clarity and readability of charts/graphs/diagrams
    - Use of appropriate consistent formatting
    - Quality of physical/virtual prototype/model
    """
}


# Create blocks for each evaluation rubric and collect scores and feedback
scores_and_feedback = [create_evaluation_block(rubric, description, f"Score for {rubric}", f"Improvement for {rubric}", f"Strength for {rubric}") for rubric, description in rubrics.items()]



# Logic for dynamically updating full name and email based on student's first name input
student_name_keyed = student_name.strip().capitalize()  # Normalize the input for matching
matching_full_name, matching_email = "", ""

if student_name_keyed in student_info:
    matching_full_name = student_info[student_name_keyed]["full_name"]
    matching_email = student_info[student_name_keyed]["email"]
