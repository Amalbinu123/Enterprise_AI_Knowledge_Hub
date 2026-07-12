# Major Project: Enterprise AI Knowledge Hub (RAG)

An intelligent enterprise knowledge assistant capable of processing multiple document formats (PDF, DOCX, TXT, MD, HTML), indexing them into a persistent ChromaDB vector store, and performing conversational retrieval-augmented generation (RAG) using Google Gemini.

---

## 🔗 Live Application Website
You can access and test the live running application here:
👉 **[Live Demo Website](https://enterpriseaiknowledgeapp-fef3tkgx4qpguycyyhz2e8.streamlit.app/)**

---

## 🚀 How to Run the Project

### 1. Clone the Repository
```bash
git clone https://github.com/Amalbinu123/Enterprise_AI_Knowledge_Hub.git
cd Enterprise_AI_Knowledge_Hub
```

### 2. Install Dependencies
Ensure you have Python installed, then set up the virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate          # On Windows
# source .venv/bin/activate     # On Mac/Linux

pip install -r requirements.txt
```

### 3. API Key Authentication (No Key Hardcoded)
For security, no API keys are stored in this repository. You can authenticate in **one of two ways**:
* **Option A (Recommended)**: Create a `.env` file in the root folder and add your key:
  ```env
  GOOGLE_API_KEY=your_gemini_api_key
  ```
* **Option B**: Run the app and paste your API key directly into the **Gemini API Key** password box in the sidebar interface.

### 4. Launch the Application
```bash
streamlit run app.py
```
This will open the web interface in your browser at `http://localhost:8501`.

---

## 🛠️ Features
* **Multi-Format Support**: Upload and analyze PDFs, Word Documents (`.docx`), Plain Text (`.txt`), Markdown (`.md`), and HTML.
* **Persistent Vector DB**: Documents are chunked and embedded in a persistent `ChromaDB` local store.
* **Document Management Console**: Ingest, list, and delete documents dynamically from the sidebar.
* **Conversational QA**: Natural language chatting with full session memory and page/file citations.
