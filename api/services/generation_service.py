# api/services/generation_service.py
# Service for handling the generation of AI responses.

from rag.qdrant import search_vectors, upsert_vector
from hf_integration.connect import get_hf_model, DEVICE
from sentence_transformers import SentenceTransformer
import torch

# Point-wise comment: Load the sentence transformer model for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Point-wise comment: Function to get an embedding for a text
async def get_embedding(text: str) -> list[float]:
    embeddings = embedding_model.encode([text])
    return embeddings[0].tolist()

# Point-wise comment: Placeholder for a cross-encoder re-ranking model
# In a real implementation, this would re-rank the retrieved documents for better relevance.
def rerank_documents(prompt: str, documents: list) -> list:
    print("Performing conceptual re-ranking of documents...")
    # For now, just return the original documents
    return documents

# Point-wise comment: Function to generate a response using the RAG pipeline
async def generate_response(prompt: str, user_id: str, adapter_id: str, top_k: int = 5) -> str:
    # 1. Get the embedding for the prompt
    prompt_embedding = await get_embedding(prompt)

    # 2. Search for similar vectors in Qdrant
    retrieved_docs = await search_vectors(prompt_embedding, top_k=top_k)

    # 3. (Conceptual) Re-rank the retrieved documents
    reranked_docs = rerank_documents(prompt, retrieved_docs)

    # 4. Load the Hugging Face model with the user's adapter
    model, tokenizer = get_hf_model(adapter_id)

    # 5. Construct a structured prompt with the retrieved context
    context = "\n".join([f"- {doc.payload.get('text', '')}" for doc in reranked_docs])
    augmented_prompt = f"You are a helpful AI assistant. Use the following context to answer the user's question.\n\nContext:\n{context}\n\nUser Question: {prompt}\n\nAI Answer:"

    # 6. Generate a response from the model
    inputs = tokenizer(augmented_prompt, return_tensors="pt", max_length=512, truncation=True).to(DEVICE)
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=100, 
            pad_token_id=tokenizer.eos_token_id, 
            do_sample=True, 
            top_k=50, 
            top_p=0.95
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # 7. (Optional) Store the new prompt and response as a vector for future context
    # await upsert_vector(user_id, await get_embedding(prompt), {"text": prompt})

    return response
