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
 
 # Add your email list    
student_info = {
    "Nicole": {"full_name": "Nicole Wang", "email": "nicolewag@example.edu"},
    "Lucy": {"full_name": "Lucy Liu", "email": "lucyliu@example.com"},
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
scores_and_feedback = [(rubric,) + create_evaluation_block(rubric, description, f"Score for {rubric}", f"Improvement for {rubric}", f"Strength for {rubric}") for rubric, description in rubrics.items()]



# Logic for dynamically updating full name and email based on student's first name input
student_name_keyed = student_name.strip().capitalize()  # Normalize the input for matching
matching_full_name, matching_email = "", ""

if student_name_keyed in student_info:
    matching_full_name = student_info[student_name_keyed]["full_name"]
    matching_email = student_info[student_name_keyed]["email"]


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
        Story.append(Spacer(1, space_after * inch))

    # Basic Info
    add_paragraph(f"<b>Instructor Name:</b> {data['Instructor Name']}", bold_style)
    add_paragraph(f"<b>Student Name:</b> {data['Student Name']}", bold_style)
    add_paragraph(f"<b>Project Name:</b> {data['Project Name']}", bold_style, space_after=0.2)

    # Use actual rubric names from the tuples
    for rubric_name, score, improvement, strength in scores_feedback:
        add_paragraph(f"<b>{rubric_name} - Score:</b> {score if score != 'Select' else 'Not Selected'}", bold_style)
        add_paragraph(f"<b>Improvement:</b> {improvement if improvement else 'No Comment'}", normal_style)
        add_paragraph(f"<b>Strength:</b> {strength if strength else 'No Comment'}", normal_style, space_after=0.8)

    doc.build(Story)
    buffer.seek(0)
    return buffer.getvalue()





# Email sending function
# Put your email and App password here
def send_email(student_email, pdf_data):
    from_email = "nicolewang@example.edu"
    password = "put your password here"
    to_email = student_email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Capstone 2 Midterm Feedback"
    attachment = MIMEApplication(pdf_data, Name="Capstone_Feedback.pdf")
    attachment['Content-Disposition'] = 'attachment; filename="Capstone_Feedback.pdf"'
    msg.attach(attachment)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        
        

#Name your google API keys as gcp_service_account and copy them to Streamlit Keys
        
def append_data_to_sheet(data):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open('capstone2mid').sheet1 

    # Find the first empty row
    all_rows = sheet.get_all_values()
    first_empty_row = len(all_rows) + 1  # Add 1 because row indices start at 1

    # Construct the range string for the update
    # Assuming 'data' is a list of values you want to insert in a single row
    update_range = f"A{first_empty_row}"  # Starts from column A, adjust if needed

    # Update the sheet with data starting from the first empty row
    sheet.update(update_range, [data])  # Data needs to be a list of lists for a row


     

scores_feedback_tuples = []

for item in scores_and_feedback:
    rubric_name, score, improvement, strength = item
    scores_feedback_tuples.append((rubric_name, score, improvement, strength))



# Generate feedback and email logic
if st.button('Generate Feedback', key='submit_review'):
    if student_name and all(score_data[0] != 'Select' for score_data in scores_feedback_tuples):
        # Gather the input data
        review_data = {
            "Instructor Name": instructor_name,
            "Student Name": student_name,
            "Project Name": project_name,
        }

        # Store scores and feedback in session state
        st.session_state['scores_feedback_tuples'] = scores_feedback_tuples

        # Generate PDF and store the bytes
        print(scores_feedback_tuples)
        pdf_bytes = generate_pdf(review_data, scores_feedback_tuples)
        st.session_state['pdf_bytes'] = pdf_bytes
        st.download_button("Download Review PDF", pdf_bytes, f"{student_name}_review.pdf", "application/pdf")

        # Indicate that the review has been generated
        st.session_state.review_submitted = True

        # Update full name and email based on student's input
        st.session_state.inferred_full_name = matching_full_name
        st.session_state.student_email = matching_email
    else:
        st.error("Please fill in all required fields (Student First Name and all Scores).")

# Display the Email sending functionality only after review submission
if st.session_state.review_submitted:
    # Display the student's full name for confirmation, not editable
    st.text(f"Student Full Name: {st.session_state.inferred_full_name}")

    # Allow editing of the email field
    edited_email = st.text_input("Student Email", value=st.session_state.student_email, key='student_email_editable')

    # Send Email button
    if st.button("Send Email", key='send_email'):
        if edited_email:
            try:
                send_email(edited_email, st.session_state['pdf_bytes'])
                st.success(f"Email sent successfully to {edited_email}")

                # Now append data to the Google Sheet
                if 'scores_feedback_tuples' in st.session_state:
                    # Combine all data to be appended to the Google Sheet
                    sheet_data = [
                        instructor_name,
                        student_name,
                        project_name
                    ] + [item for tup in st.session_state['scores_feedback_tuples'] for item in tup] + [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    append_data_to_sheet(sheet_data)

                    # Clear the session state after appending to the sheet
                    del st.session_state['scores_feedback_tuples']
                    del st.session_state['pdf_bytes']
                    st.session_state.review_submitted = False  # Reset the flag to allow new submissions

            except Exception as e:
                st.error(f"Failed to send email: {e}")
        else:
            st.error("Please make sure the student's email address is filled in.")