# hf_integration/connect.py
# Module for connecting to Hugging Face and loading models.

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os
import torch

# Point-wise comment: Define the base model from Hugging Face
BASE_MODEL_NAME = "distilgpt2"

# Point-wise comment: Determine the device to run the model on (GPU or CPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Point-wise comment: Function to load the Hugging Face model and tokenizer
# This function loads the base model and applies a LoRA adapter if one is provided.
def get_hf_model(adapter_id: str = None):
    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    # Set the padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load the base model
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME)

    # If an adapter_id is provided, load the LoRA adapter
    if adapter_id:
        adapter_path = f"./adapters/{adapter_id}"
        if os.path.exists(adapter_path):
            print(f"Loading adapter from: {adapter_path}")
            model = PeftModel.from_pretrained(model, adapter_path)
        else:
            print(f"Adapter not found at: {adapter_path}. Using base model.")

    # Move the model to the correct device
    model.to(DEVICE)

    return model, tokenizer
