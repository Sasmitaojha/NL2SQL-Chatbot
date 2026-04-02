# AI-Powered Natural Language to SQL System

This project is an AI-powered NL2SQL chatbot built with FastAPI and Vanna AI 2.0. Users can ask questions about a simulated Clinic Database in plain English, and the system intelligently generates, validates, and executes corresponding SQL queries to provide accurate results.

## Technology Stack

- **Python**: 3.10+
- **Vanna AI**: 2.0.x (Agent-based architecture)
- **FastAPI** & **Uvicorn**: REST API layer
- **SQLite**: Local built-in database (no manual installation necessary!)
- **LLM Provider**: **Google Gemini (gemini-2.5-flash)**
- **Visualization**: Plotly and Pandas 

> **Important**: This project intentionally implements the newer **Vanna 2.0.x** APIs (`Agent`, `ToolRegistry`, `DemoAgentMemory`, `GeminiLlmService`) and explicitly avoids legacy/deprecated 0.x patterns (e.g., `vn.train()` or `ChromaDB`).

## Setup Details

### Step 1: Install Dependencies
You can install all dependencies via `pip`:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Since we are using **Google Gemini**, you need to provide an API key.
1. Create a `.env` file in the root directory.
2. Add your Google API Key:
   ```env
   GOOGLE_API_KEY=your-google-api-key-here
   ```

### Step 3: Database Creation & Seeding
This project auto-generates a mock SQLite database containing tables for `patients`, `doctors`, `appointments`, `treatments`, and `invoices`. To build and populate the `clinic.db`:

```bash
python setup_database.py
```
*Expected Output*: "Created X patients, Y doctors, Z appointments... Database creation and seeding complete."

### Step 4: Seed Vanna Local Memory
In Vanna 2.0, the agent context is bootstrapped via `DemoAgentMemory`. Running the following script injects 15 fundamental and accurate Question-SQL semantic pairs to enhance prediction accuracy:
```bash
python seed_memory.py
```
*Expected Output*: "Agent memory seeded successfully."

## Running the API Server

Spin up the Uvicorn/FastAPI server:
```bash
uvicorn main:app --port 8000
```
*(Alternatively, append `--reload` parameter during local testing)*

The API provides two available endpoints:

### GET `/health`
Returns the status of both the internal components and SQLite connection hook.
**Example Request**: `GET http://localhost:8000/health`
**Example Response**:
```json
{
  "status": "ok",
  "database": "connected",
  "agent_memory_items": 15
}
```

### POST `/chat`
Responsible for interpreting NL strings to SQL logic, safely validating them (preventing `DROP`, `DELETE` instructions or arbitrary system calls), fetching the final output, and returning it uniformly.
**Example Request**: `POST http://localhost:8000/chat`
```json
{
  "question": "Show me the top 5 patients by total spending"
}
```

**Example Response**:
```json
{
  "message": "Results fetched successfully.",
  "sql_query": "SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spending FROM patients p JOIN invoices i ON p.id = i.patient_id GROUP BY p.id ORDER BY total_spending DESC LIMIT 5",
  "columns": ["first_name", "last_name", "total_spending"],
  "rows": [
    ["John", "Smith", 4500.0],
    ["Jane", "Doe", 3200.0]
  ],
  "row_count": 5,
  "chart": null,
  "chart_type": null
}
```

## Architecture & Logic Overivew

1. **Backend Layer**: A bare-bones `FastAPI` instance managing route requests and intercepting input variables. It includes a custom regex-based `validate_sql()` string detector to ensure read-only transactions.
2. **Vanna Tools & Overrides**: The agent has been instantiated using `AgentConfig`. The default `RunSqlTool` is wrapped in `ValidatedRunSqlTool` protecting runtime execution from accidental mutations. 
3. **Agent LLM Logic**: The context and inputs are dispatched to `GeminiLlmService`, guided contextually by `DemoAgentMemory` (injected via `ToolRegistry`).

## Test Results

Reference the [RESULTS.md](RESULTS.md) for a complete overview tracking Vanna LLM behaviour over the 20 test sequences requested.
