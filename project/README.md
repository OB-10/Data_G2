AI Database Generator and Conversational Data Analyst
====================================================

This project allows users to:
- Generate relational databases from natural language descriptions.
- Populate them with realistic synthetic data.
- Query the data conversationally using natural language.
- Inspect the generated SQL, ER diagrams, and download datasets.

Key technologies:
- Backend: FastAPI (Python)
- Frontend: Streamlit
- Database: MySQL (via SQLAlchemy)
- AI: LangChain, OpenAI API, ChromaDB (RAG)
- Data generation: Faker
- Visualization: Graphviz

## Running the project

### 1. Prerequisites

- Python 3.10+
- MySQL server running and accessible (local or remote)
- An OpenAI API key

### 2. Setup

1. Create and activate a virtual environment, then install dependencies:

```bash
cd project
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt
```

2. Configure environment variables (create a `.env` file in `project/backend` or `project` root):

```bash
OPENAI_API_KEY=your_openai_api_key_here
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=ai_generated_db
```

You can also override any setting defined in `backend/config.py`.

### 3. Run the FastAPI backend

From the `project` directory:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`.

### 4. Run the Streamlit frontend

In a separate terminal, from the `project` directory:

```bash
streamlit run frontend/streamlit_app.py
```

By default, the frontend expects the backend at `http://localhost:8000`. If you run the backend elsewhere, set:

```bash
set BACKEND_URL=http://your-backend-host:port  # Windows
export BACKEND_URL=http://your-backend-host:port  # Unix-like
```

### 5. Usage

- Use the **Generate Database** tab to describe the database (e.g., hotels in Goa) and create/populate it.
- Use the **Query Database** tab to ask natural language questions; the app will show the generated SQL and results.
- Use the **Schema & Export** tab to view the ER diagram and download the dataset as CSV.

