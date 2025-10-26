from app.quiz_utils import extract_text_from_pdf

# Windows paths must use raw strings or double backslashes
pdf_path = r"C:\Users\Admin\quiz_game\study_guides\SOFTWARE ENGINEERING 700 STUDY GUIDE.pdf"

extract_text_from_pdf(pdf_path)