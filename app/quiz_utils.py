import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"❌ File not found at: {pdf_path}")
        return None

    doc = fitz.open(pdf_path)
    all_text = [page.get_text() for page in doc]
    doc.close()

    combined_text = "\n".join(all_text)
    txt_output_path = os.path.splitext(pdf_path)[0] + "_extracted.txt"

    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(combined_text)

    print(f"✅ PDF text extracted and saved to:\n{txt_output_path}")
    return combined_text


def extract_images_from_pdf(pdf_path, output_folder):
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    for page_number in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_number)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page{page_number+1}_img{img_index+1}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

    doc.close()
    print(f"✅ Images extracted to: {output_folder}")
