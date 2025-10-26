import os
import time
import json
import re
from dotenv import load_dotenv
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file.")

# Setup Hugging Face model pipeline
model_name = "t5-small"
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
question_pipeline = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer
)

# Paths
chunks_dir = r"C:/Users/Admin/quiz_game/study_guides/year_3/MOBILE APP DEVELOPMENT 700_extracted_chunks"
output_basename = "MOBILE APP DEVELOPMENT_700"

# Generate prompt with explicit instructions
def generate_prompt(text_chunk):
    return (
        "Create 20 quiz questions based on the following material.\n"
        "Format each question as:\n"
        "Q<number>. [question]\n"
        "Type: [MCQ / True/False / Short / Fill / Interpretation]\n"
        "Options:\n"
        "A. [option A]\n"
        "B. [option B]\n"
        "C. [option C]\n"
        "D. [option D]\n"
        "Answer: [correct answer]\n"
        "Reasoning: [why?]\n"
        "Difficulty: [easy, medium, hard]"
        "Separate each question with a line of dashes.\n\n"
        f"{text_chunk}"
    )

# Clean response
def clean_response(text):
    return re.sub(r"[*_]", "", text).strip()

# Truncate large input
def truncate_text(text, max_tokens=512):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return tokenizer.decode(tokens)

# Output paths
txt_output_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "study_guides", "year_1", f"{output_basename}_quiz_questions.txt"
)

json_output_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "study_guides", "year_1", f"{output_basename}_quiz_questions.json"
)

db_questions_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "study_guides", "year_1", f"{output_basename}_questions_for_db.json"
)

os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)

# Gather chunk files
chunk_files = sorted(
    [f for f in os.listdir(chunks_dir) if f.startswith("chunk_") and f.endswith(".txt")]
)

if not chunk_files:
    print("❌ No chunk files found.")
    exit(1)

all_questions_for_db = []

# Main processing
for i, filename in enumerate(chunk_files):
    chunk_path = os.path.join(chunks_dir, filename)
    print(f"\n🔍 Processing chunk {i + 1}/{len(chunk_files)}: {filename}")

    with open(chunk_path, "r", encoding="utf-8") as f:
        text_chunk = f.read()

    # Truncate large chunks
    text_chunk_truncated = truncate_text(text_chunk)

    prompt = generate_prompt(text_chunk_truncated)
    print("\n=== Generated Prompt ===\n")
    print(prompt)
    print("=========================\n")

    for attempt in range(3):
        try:
            # Generate questions
            response_list = question_pipeline(prompt)
            response_text = response_list[0]['generated_text']
            print("\n=== Raw Model Output ===\n")
            print(response_text)
            print("=========================\n")

            # Clean the output
            cleaned = clean_response(response_text)
            print("\n=== Cleaned Output ===\n")
            print(cleaned)
            print("======================\n")

            # Split questions on separator line of dashes
            questions_blocks = re.split(r"\n-+\n", cleaned)

            for block in questions_blocks:
                lines = block.strip().splitlines()
                if not lines:
                    continue

                question_text = ""
                q_type = ""
                options = {}
                answer = ""
                reasoning = ""

                for line in lines:
                    line = line.strip()

                    # Match question number and text
                    q_match = re.match(r"Q(\d+)\.\s*(.+)", line)
                    if q_match:
                        question_text = q_match.group(2)
                        continue

                    # Match question type
                    type_match = re.match(r"Type:\s*(.+)", line)
                    if type_match:
                        q_type = type_match.group(1)
                        continue

                    # Match options
                    option_match = re.match(r"([A-D])\.\s*(.+)", line)
                    if option_match:
                        options[option_match.group(1)] = option_match.group(2)
                        continue

                    # Match answer
                    answer_match = re.match(r"Answer:\s*(.+)", line)
                    if answer_match:
                        answer = answer_match.group(1)
                        continue

                    # Match reasoning
                    reasoning_match = re.match(r"Reasoning:\s*(.+)", line)
                    if reasoning_match:
                        reasoning = reasoning_match.group(1)
                        continue

                # Build question entry
                question_entry = {
                    "question_text": question_text,
                    "option_a": options.get("A", ""),
                    "option_b": options.get("B", ""),
                    "option_c": options.get("C", ""),
                    "option_d": options.get("D", ""),
                    "correct_option": "",
                    "reasoning": reasoning
                }

                # Determine correct option (letter) from answer text
                answer_lower = answer.lower()
                matched = False
                for opt, text in options.items():
                    if answer_lower == text.lower():
                        question_entry["correct_option"] = opt
                        matched = True
                        break
                # Fallback if no exact match
                if not matched:
                    question_entry["correct_option"] = answer

                # Debug: print parsed question
                print("Parsed Question:\n", question_entry)
                print("-" * 50)

                all_questions_for_db.append(question_entry)

            print(f"✅ Chunk {i + 1} questions parsed.")
            time.sleep(10)  # pause to avoid rate limits
            break
        except Exception as e:
            if "429" in str(e):
                print(f"⏳ Rate limit hit. Retrying in 15s... (Attempt {attempt + 1}/3)")
                time.sleep(15)
            else:
                print(f"❌ Error in chunk {i + 1} ({filename}): {e}")
                break

# Save as plain text with reasoning
with open(txt_output_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join([
        f"{q['question_text']}\nReasoning: {q.get('reasoning', '')}"
        for q in all_questions_for_db
    ]))
print(f"\n✅ Text questions saved to:\n{txt_output_path}")

# Save as JSON
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(all_questions_for_db, f, indent=2, ensure_ascii=False)
print(f"✅ JSON questions saved to:\n{json_output_path}")

# Save questions for DB
with open(db_questions_path, "w", encoding="utf-8") as f:
    json.dump(all_questions_for_db, f, indent=2, ensure_ascii=False)
print(f"✅ Questions formatted for DB saved to:\n{db_questions_path}")
