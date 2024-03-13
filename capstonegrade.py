import streamlit as st

# Title for the grading form
st.title('Capstone 2 Midterm Feedback')

# Input fields for instructor, student, and project names
col1, _ = st.columns([1, 1])  # Adjust for half-width for the instructor name
with col1:
    instructor_name = st.text_input("Instructor Name", placeholder="Enter the instructor's name")

col_student, col_project = st.columns(2)
with col_student:
    student_name = st.text_input("Student Name", placeholder="Enter the student's name", key='student_name')
with col_project:
    project_name = st.text_input("Project Name", placeholder="Enter the project name")

# Function to create a block for each evaluation rubric
def create_evaluation_block(rubric_name, description, score_name, improvement_name, strength_name):
    st.header(rubric_name)
    st.markdown(description)
    # Adding a default 'Select' option for scores
    score_options = ['Select'] + [str(num) for num in range(1, 11)]
    score = st.radio(score_name, options=score_options, key=f"score_{rubric_name}", horizontal=True)
    improvement = st.text_area("Points to Consider for Improvement", key=f"improve_{rubric_name}")
    strength = st.text_area("Areas of Strength", key=f"strength_{rubric_name}")
    return score, improvement, strength

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

# Submit button and validation of required fields
if st.button('Submit Review'):
    # Checking that student name is filled and all scores are selected (not 'Select')
    if student_name.strip() and all(score != 'Select' for score, _, _ in scores_and_feedback):
        st.success("Thank you for submitting the review!")
    else:
        st.error("Please fill in all required fields (student name and all scores).")
