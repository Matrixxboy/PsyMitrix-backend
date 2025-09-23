# PsyMitrix AI Backend

This project is a highly scalable and secure AI backend built with FastAPI. It features a modular architecture, dual-database setup with MongoDB and Qdrant, and personalized AI responses using PEFT/LoRA adapters from Hugging Face.

## Features

- **FastAPI Backend:** A modern, fast (high-performance) web framework for building APIs.
- **MongoDB Atlas:** Used for storing user data, designed for scalability with sharding.
- **Qdrant:** A vector database for Retrieval Augmented Generation (RAG) to provide context to the AI.
- **Hugging Face Integration:** Dynamically loads PEFT/LoRA adapters for personalized AI responses.
- **Blockchain Audit Trail:** A middleware logs all API requests to the Polygon Mumbai Testnet for an immutable audit trail.
- **JWT Authentication:** Secure user authentication using JSON Web Tokens.

## Project Structure

```
/
├───adapters/             # Storage for PEFT/LoRA adapters
├───api/
│   ├───routers/          # API endpoints (auth, generation, user)
│   └───services/         # Business logic for each feature
├───blockchain/
│   └───middleware.py     # Middleware for blockchain logging
├───core/
│   ├───config.py         # Application configuration
│   └───db.py             # Database connection management
├───models/
│   ├───mongo_models.py   # MongoDB models (if needed)
│   └───pydantic_models.py# Pydantic data validation models
├───rag/
│   └───qdrant.py         # Qdrant service for vector search
├───hf_integration/
│   └───connect.py        # Hugging Face model and adapter loading
├───main.py               # Main FastAPI application entry point
├───requirements.txt      # Python dependencies
└───README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB Atlas account
- Qdrant instance
- An account with a wallet on the Polygon Mumbai Testnet

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd PsyMitrix-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    - Rename the `.env.example` file to `.env`.
    - Fill in the required values for your database connections, secret keys, and blockchain wallet.

### Running the Application

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- **`POST /api/users/`**: Create a new user.
- **`POST /api/auth/token`**: Log in and receive a JWT access token.
- **`POST /api/generate/`**: Generate a personalized AI response (requires authentication).





