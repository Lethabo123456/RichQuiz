import os

def chunk_text(input_path, output_folder, chunk_size=1000, overlap=100):
    """
    Splits a text file into overlapping chunks for LLM-based processing or QA generation.

    Args:
        input_path (str): Path to the input text file.
        output_folder (str): Where to save the chunks.
        chunk_size (int): Number of characters per chunk.
        overlap (int): Overlap between chunks (in characters).
    """
    if not os.path.isfile(input_path):
        print(f"❌ File not found: {input_path}")
        return

    os.makedirs(output_folder, exist_ok=True)

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()

    total_length = len(text)
    start = 0
    chunk_num = 1

    while start < total_length:
        end = min(start + chunk_size, total_length)
        chunk = text[start:end].strip()

        chunk_filename = os.path.join(output_folder, f"chunk_{chunk_num:03}.txt")
        with open(chunk_filename, 'w', encoding='utf-8') as chunk_file:
            chunk_file.write(chunk)

        print(f"✅ Saved: {chunk_filename}")
        chunk_num += 1
        start += chunk_size - overlap


if __name__ == "__main__":
    chunk_text(
        input_path=r"C:\Users\Admin\quiz_game\study_guides\year_3\SOFTWARE ENGINEERING 700 STUDY GUIDE_extracted.txt",
        output_folder=r"C:\Users\Admin\quiz_game\study_guides\year_3\SOFTWARE ENGINEERING 700 STUDY GUIDE_extracted_chunks"
    )
