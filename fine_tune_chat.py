from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import Dataset
import json

# Load DistilGPT-2
model_name = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load data
with open("data/fine_tune_data.json", "r") as f:
    data = json.load(f)

texts = [f"[Personality: {d['personality']}] Message: {d['message']}" for d in data]
responses = [d['response'] for d in data]

dataset = Dataset.from_dict({"input_text": texts, "target_text": responses})

# Tokenize
def tokenize_function(example):
    model_inputs = tokenizer(example["input_text"], padding="max_length", truncation=True, max_length=128)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(example["target_text"], padding="max_length", truncation=True, max_length=128)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./models/personality_gpt",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    save_steps=50,
    save_total_limit=2,
    logging_steps=10,
    learning_rate=5e-5
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

trainer.train()
trainer.save_model("./models/personality_gpt")
tokenizer.save_pretrained("./models/personality_gpt")

print("✅ Fine-tuning complete and model saved!")
