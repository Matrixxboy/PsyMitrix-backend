# hf_integration/training_service.py
# Service for handling model fine-tuning and adapter management.

from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import Dataset
import os

from hf_integration.connect import BASE_MODEL_NAME

# Point-wise comment: Function to prepare and tokenize the dataset
def prepare_dataset(tokenizer, data):
    # For this example, we assume `data` is a list of strings.
    # Each string is a document for training.
    text_data = [" ".join(item) for item in data]
    dataset = Dataset.from_dict({"text": text_data})

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    return tokenized_dataset

# Point-wise comment: Function to fine-tune the model with LoRA
def train_adapter(user_id: str, training_data: list):
    # --- 1. Load Base Model and Tokenizer ---
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME)

    # --- 2. Configure LoRA ---
    lora_config = LoraConfig(
        r=16, # Rank
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)

    # --- 3. Prepare Dataset ---
    tokenized_dataset = prepare_dataset(tokenizer, training_data)

    # --- 4. Set up Trainer ---
    output_dir = f"./adapters/{user_id}_training_output"
    adapter_dir = f"./adapters/{user_id}"

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1, # For demonstration purposes
        per_device_train_batch_size=1,
        save_steps=500,
        save_total_limit=2,
        logging_dir=f"{output_dir}/logs",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # --- 5. Train and Save ---
    print(f"Starting LoRA training for user: {user_id}")
    trainer.train()
    print(f"Training complete. Saving adapter to: {adapter_dir}")
    model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    return adapter_dir
