from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# Specify the model name
model_name = "t5-small"

# Load the model and tokenizer directly from Hugging Face hub
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Create the pipeline for question generation
question_generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer
)

# Example input text
text = "This is a sample text to generate a question."

# Generate questions
questions = question_generator(text)
print(questions)