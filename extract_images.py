# extract_images.py

from app.quiz_utils import extract_images_from_pdf

pdf_path = r"C:\Users\Admin\Documents\Year 1\Maths\Maths 511.pdf"
output_folder = r"C:\Users\Admin\quiz_game\study_guides\Mathematics 511_IMAGES"

extract_images_from_pdf(pdf_path, output_folder)
