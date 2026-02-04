"""
fine_tune_chat.py - Fine-tune DistilGPT-2 for personality responses
"""

import json
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import Dataset

def prepare_training_data():
    """Load and format training data"""
    with open("data/fine_tune_data.json", "r") as f:
        data = json.load(f)

    formatted = []
    for sample in data:
        scores = sample["personality_scores"]
        prompt = (
            f"Personality: Neuroticism={scores['neuroticism']:.2f}, "
            f"Agreeableness={scores['agreeableness']:.2f}, "
            f"Conscientiousness={scores['conscientiousness']:.2f}, "
            f"Extraversion={scores['extraversion']:.2f}, "
            f"Openness={scores['openness']:.2f}\n"
            f"Message: {sample['scam_message']}\n"
            f"Response: {sample['response']}"
        )
        formatted.append({"text": prompt})

    return Dataset.from_list(formatted)

def fine_tune_model():
    """Fine-tune DistilGPT-2"""
    print("Loading model and tokenizer...")
    model_name = "distilgpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(model_name)

    print("Preparing dataset...")
    dataset = prepare_training_data()

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Split dataset
    train_test_split = tokenized_dataset.train_test_split(test_size=0.1)
    train_dataset = train_test_split["train"]
    eval_dataset = train_test_split["test"]

    print("Setting up training...")
    training_args = TrainingArguments(
        output_dir="./personality_chatbot",
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        save_total_limit=2,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer
    )

    print("Starting training...")
    trainer.train()

    print("Saving model...")
    model.save_pretrained("./personality_chat_model")
    tokenizer.save_pretrained("./personality_chat_model")

    print("Fine-tuning complete!")
    return "./personality_chat_model"

if __name__ == "__main__":
    fine_tune_model()