## README File

### 1. How to Set Up and Run the Assistant

**A. Clone the Repository**
```bash
git clone https://github.com/sukrithpvs/HSBC.git

```

**B. Install Dependencies**
- Make sure you have **Python 3.10+** installed.
- Install required packages:
```bash
pip install -r requirements.txt
```

**C. (Optional) Set API Keys**
- For best results, set your `GROQ_API_KEY` environment variable for LLM-based intent recognition and response generation.  
  Example:
  ```bash
  export GROQ_API_KEY=your_groq_api_key_here
  ```

**D. Run the FastAPI Server**
```bash
uvicorn main:app --reload
```
- The API will now be available at: `http://localhost:8000`
- Swagger UI for REST API documentation: `http://localhost:8000/docs`
- WebSocket endpoint: `ws://localhost:8000/ws`

**E. Database**
- The system uses a local SQLite database (`banking_system.db`). On first launch, it auto-populates demo users, accounts, cards, and transactions.

### 2. Supported Flows with Example Prompts

**A. Loan Application**
- Example prompts:
  - `"I want to apply for a loan"`
  - `"Can I get 15,000 dollars for home renovation?"`

**B. Card Blocking**
- Example prompts:
  - `"Block my credit card ending 7890"`
  - `"I lost my debit card"`

**C. Account Queries**
- Example prompts:
  - `"What is my balance?"`
  - `"Show me my last 5 transactions"`

**D. Card Application**
- Example prompts:
  - `"I need a new credit card"`
  - `"How do I get a debit card?"`

**E. Loan Status/Inquiry**
- Example prompts:
  - `"Show my loan applications"`
  - `"What is the status of my loan?"`

**F. Greetings & General Inquiries**
- Example prompts:
  - `"Hello"`
  - `"Thank you, goodbye"`

**Features**  
- Handles multi-step workflows: will ask follow-up questions as needed (e.g., DOB for security, amount needed, etc.).
- Context-aware: remembers current workflow, supports context switching (user can say: "Wait, block my card instead").
- Recovers from ambiguity: will prompt user to clarify missing information.
- All flows support real-time backend interaction with mock/demo data.

### 3. Dependency List and Usage Guide

**A. Core Dependencies**
- `Python 3.10+`
- `fastapi` (Web framework)
- `uvicorn` (ASGI server)
- `aiosqlite`, `sqlite3`  (Database layer)
- `pydantic`  (Data schemas)
- `groq` (Large Language Model API; can swap for OpenAI client)
- `CORS middleware`  (For frontend compatibility)

**Check `requirements.txt` for the complete list.**

**B. Usage Guide**
- **REST API usage**:  
  Send a POST request to `/api/v1/chat` with a JSON body:
  ```json
  {
    "message": "Block my debit card"
  }
  ```
  Include (optionally) a `user_id`. Returns assistant reply and state info.

- **WebSocket usage**:  
  Connect to `ws://localhost:8000/ws`
  Send and receive JSON-formatted messages for a real-time conversation.
  - On connect, a welcome/help message is sent.
  - Continue exchanging `{"message": ""}` and get structured responses.

- **Demo users for testing**:
  - `user_demo1` : John Smith
  - `user_demo2` : Sarah Johnson

**C. Customization**
- To add new flows: extend intent enums in `models.py`, add handler logic in `services.py`, and update database/model code as needed.
- The backend can be switched from SQLite to real APIs with minimal code changes (`database.py`).
- Frontend can be added easily on top of API/WebSocket for web/mobile chatbot.

**D. Example Workflows**
- The assistant handles context, clarifies missing info, and manages interruptions automatically.
- Try switching tasks mid-conversation:  
  - User: `"I want to apply for a loan"`
  - Assistant: ... (asks purpose, amount etc.)
  - User: `"Actually, block my card instead"`  
    (Assistant switches to card blocking flow, preserves previous workflow state)


