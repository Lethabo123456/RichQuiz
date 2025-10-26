import json

# Path to your current JSON
input_path = r"C:\Users\Admin\quiz_game\questions\programming_python_questions.json"
output_path = r"C:\Users\Admin\quiz_game\questions\programming_python_questions_cleaned.json"

with open(input_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

cleaned_questions = []

for entry in raw_data:
    # Some entries are grouped under a 'questions' multiline string
    if "questions" in entry:
        lines = entry["questions"].split('\n')
        current_q = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Q"):
                if current_q:
                    cleaned_questions.append(current_q)
                current_q = {"question": line[3:].strip(), "options": []}
            elif line.startswith("Type:"):
                current_q["type"] = line[5:].strip()
            elif line.startswith("Options:"):
                options_line = line[8:].strip()
                if options_line:
                    # Split options using known MCQ patterns
                    opts = options_line.split(", ")
                    current_q["options"] = [opt.strip() for opt in opts]
            elif line.startswith("Answer:"):
                current_q["correct_answer"] = line[7:].strip()

        if current_q:
            cleaned_questions.append(current_q)

# Fallback: ensure all questions have at least an empty options list
for q in cleaned_questions:
    if "options" not in q or not isinstance(q["options"], list):
        q["options"] = []

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_questions, f, indent=2, ensure_ascii=False)

print(f"✅ Cleaned questions saved to: {output_path}")
