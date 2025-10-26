from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Specify the model name
model_name = "mrm8488/t5-base-finetuned-question-generation-ap"

# Specify the folder where you want to cache/download the model
cache_dir = r"C:\Users\Admin\quiz_game\models"

# Download and cache the model and tokenizer
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=cache_dir)
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)

print("Model downloaded and cached.")