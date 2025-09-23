# PsyMitrix AI Backend - API Documentation

This document provides details and examples for all available API endpoints.

**Base URL**: `http://127.0.0.1:8000`

---

## Authentication

Most endpoints require a Bearer Token for authentication. To get a token, you must first create a user and then log in.

### 1. Create a New User

Creates a new user record in the database. The entire user data structure is based on the `appData.json` template, which is then encrypted and stored.

- **Method**: `POST`
- **Path**: `/api/users/`
- **Authentication**: None

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "a-very-strong-password"
}
```

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
-H "Content-Type: application/json" \
-d '{
  "email": "newuser@example.com",
  "password": "a-very-strong-password"
}'
```

**Example Success Response (200 OK):**
```json
{
    "id": "a-unique-uuid",
    "email": "newuser@example.com",
    "name": "Utsav Lankapati",
    "avatarUrl": "https://avatars.githubusercontent.com/u/1?v=4",
    "preferences": {
        "theme": "system",
        "notifications": true,
        "language": "en"
    },
    "stats": {
        "streakDays": 4,
        "level": 3,
        "xp": 1240
    },
    "hashed_password": "..."
}
```

---


### 2. Log In and Get Token

Authenticates a user and returns a JWT access token.

- **Method**: `POST`
- **Path**: `/api/auth/token`
- **Authentication**: None

**Request Body (Form Data):**
- `username`: The user's email address.
- `password`: The user's plain-text password.

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=newuser@example.com&password=a-very-strong-password"
```

**Example Success Response (200 OK):**
```json
{
  "access_token": "your-jwt-token-here",
  "token_type": "bearer"
}
```

---

## User Data

### Get Full User Data

Retrieves the complete, decrypted data structure for the currently authenticated user.

- **Method**: `GET`
- **Path**: `/api/users/me/data`
- **Authentication**: Bearer Token required.

**Example Request:**
```bash
# Replace YOUR_TOKEN with the access token from the login step
curl -X GET "http://127.0.0.1:8000/api/users/me/data" \
-H "Authorization: Bearer YOUR_TOKEN"
```

**Example Success Response (200 OK):**
*The response will be the full user object from your data structure, similar to the `user` object in `appData.json`.*

---

## Hugging Face Integration

### Store Hugging Face API Key

Allows an authenticated user to securely store their Hugging Face API key. This key will be used for interactions with Hugging Face services, such as model training or inference.

- **Method**: `POST`
- **Path**: `/api/hf-key/store-hf-key`
- **Authentication**: Bearer Token required.

**Request Body:**
```json
{
  "hf_api_key": "hf_YOUR_HUGGING_FACE_API_KEY"
}
```

**Example Request:**
```bash
# Replace YOUR_TOKEN with the access token
# Replace hf_YOUR_HUGGING_FACE_API_KEY with your actual Hugging Face API key
curl -X POST "http://127.0.0.1:8000/api/hf-key/store-hf-key" \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{"hf_api_key": "hf_YOUR_HUGGING_FACE_API_KEY"}'
```

**Example Success Response (200 OK):**
```json
{
  "message": "Hugging Face API key stored successfully."
}
```

---

## AI & Machine Learning

### Generate AI Response

Generates a personalized, context-aware AI response using the RAG pipeline and the user's fine-tuned adapter.

- **Method**: `POST`
- **Path**: `/api/generate/`
- **Authentication**: Bearer Token required.

**Query Parameters:**
- `prompt`: The text prompt for the AI.

**Example Request:**
```bash
# Replace YOUR_TOKEN with the access token
curl -X POST "http://127.0.0.1:8000/api/generate/?prompt=What%20is%20one%20small%20thing%20I%20can%20do%20today%3F" \
-H "Authorization: Bearer YOUR_TOKEN"
```

**Example Success Response (200 OK):**
```json
"Based on your recent mood logs, taking a short 5-minute walk has often lifted your spirits. Perhaps you could try that?"
```

### Trigger User Model Training

Starts the fine-tuning process for the user's personal AI model adapter. **Note:** This is a long-running task.

- **Method**: `POST`
- **Path**: `/api/users/me/train`
- **Authentication**: Bearer Token required.

**Request Body:**
An array of strings, where each string is a piece of text for training.
```json
[
  "I find that writing in my journal helps me clear my head.",
  "A short walk in the morning really boosts my energy.",
  "I feel most anxious when I have a lot of deadlines approaching."
]
```

**Example Request:**
```bash
# Replace YOUR_TOKEN with the access token
curl -X POST "http://127.0.0.1:8000/api/users/me/train" \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '["I find that writing in my journal helps me clear my head.", "A short walk in the morning really boosts my energy."]'
```

**Example Success Response (200 OK):**
```json
{
  "message": "Training complete. Adapter saved at: ./adapters/a-unique-uuid"
}
```
