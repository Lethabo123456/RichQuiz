import json
import os

# Paths
json_path = os.path.join("questions", "Programming_621-622_questions_for_db.json")
sql_output = os.path.join("questions", "questions_import.sql")

# Set the module ID to 19 Software_Science_700_questions_for_db

MODULE_ID = 8

# Load JSON (unwrap if needed)
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Top-level type:", type(data))
print("First element type:", type(data[0]))

# If accidentally double-wrapped in a list
if isinstance(data, list) and data and isinstance(data[0], list):
    data = data[0]

sql_lines = []

for q in data:
    if not isinstance(q, dict):
        print("⚠️ Skipping non-dictionary entry:", q)
        continue  # Skip invalid entries

    question = q.get("question", "").replace("'", "''")
    options = q.get("options") or {}
    reasoning = q.get("reasoning", "").replace("'", "''")
    difficulty = q.get("difficulty", "medium").lower()  # default to medium if missing
    correct_letter = q.get("correct_answer", "").strip().upper()

    # Debug print to check options format
    print("Options raw:", options)
    print("Options type:", type(options))

    # Extract options safely depending on type
    if isinstance(options, dict):
        option_a = options.get("A", "").replace("'", "''")
        option_b = options.get("B", "").replace("'", "''")
        option_c = options.get("C", "").replace("'", "''")
        option_d = options.get("D", "").replace("'", "''")
    elif isinstance(options, list):
        option_a = options[0].replace("'", "''") if len(options) > 0 else ""
        option_b = options[1].replace("'", "''") if len(options) > 1 else ""
        option_c = options[2].replace("'", "''") if len(options) > 2 else ""
        option_d = options[3].replace("'", "''") if len(options) > 3 else ""
    else:
        option_a = option_b = option_c = option_d = ""

    # Validate correct_letter; fallback if invalid
    if correct_letter not in ['A', 'B', 'C', 'D']:
        # Try to find correct letter by matching option text (rare case)
        correct_text = q.get("correct_answer", "").strip().lower()
        correct_letter = ""
        for label, opt in zip("ABCD", [option_a, option_b, option_c, option_d]):
            if opt.lower() == correct_text:
                correct_letter = label
                break
        if not correct_letter:
            correct_letter = 'A'  # default fallback

    sql = f"""INSERT INTO questions 
(module_id, question_text, option_a, option_b, option_c, option_d, correct_option, reasoning, difficulty)
VALUES ({MODULE_ID}, '{question}', '{option_a}', '{option_b}', '{option_c}', '{option_d}', '{correct_letter}', '{reasoning}', '{difficulty}');"""

    sql_lines.append(sql)

# Save SQL file
with open(sql_output, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print(f"✅ SQL INSERTs saved to: {sql_output}")
