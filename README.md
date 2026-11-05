# 📚 CourseClarity AI

> **Understand More. Learn Better.**
> An IBM Granite-Powered Course Content Simplification Agent
>
> AICTE Problem Statement #19 | Powered by **IBM Granite** on **IBM watsonx.ai** | IBM Cloud Lite

---

## 🎯 Problem Statement

Many students — especially first-generation learners and those from non-English-medium backgrounds — struggle to understand complex academic course material. Textbooks, research papers, and lecture notes often use technical jargon or dense explanations, making it difficult for students to grasp core concepts independently.

This agent automatically simplifies educational content into clear, digestible formats.

---

## 🚀 Features

| Feature | Description |
|---|---|
| ✏️ **Simplify** | Converts dense academic text into plain-English explanations (Class 10 level) |
| 📋 **Summarize** | Generates concise bullet-point key-point summaries |
| ❓ **Quiz** | Auto-generates 5 MCQs for self-assessment |
| 📖 **Glossary** | Extracts and explains key technical terms |
| 🌐 **Translate** | Translates output into 11 Indian regional languages |
| 📄 **File Upload** | Supports PDF and DOCX input in addition to pasted text |

---

## 🧠 Technology Stack

- **AI Model**: IBM Granite (`ibm/granite-4-h-small`) via IBM watsonx.ai
- **IBM Cloud Service**: Watson Machine Learning (WML) — Lite plan
- **Frontend**: Streamlit
- **Text Extraction**: PyMuPDF (PDF), python-docx (DOCX)
- **Language**: Python 3.10+

---

## 📁 Project Structure

```
AICTE-Course Content Simplification Agent/
│
├── app.py               # Streamlit UI (main entry point)
├── agent.py             # Simplification agent logic + prompt templates
├── granite_client.py    # IBM Granite / watsonx.ai API client
├── utils.py             # PDF/DOCX text extraction, text chunking
├── requirements.txt     # Python dependencies
├── .env                 # IBM Cloud credentials (DO NOT commit)
└── README.md            # This file
```

---

## ⚙️ Setup Instructions

### 1. Clone / Download the project

```bash
cd "AICTE-Course Content Simplification Agent"
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure IBM Cloud credentials

Edit the `.env` file:

```env
IBM_API_KEY=<your IBM Cloud API key>
IBM_WML_URL=https://us-south.ml.cloud.ibm.com
IBM_PROJECT_ID=<your watsonx.ai project ID>
GRANITE_MODEL_ID=ibm/granite-4-h-small
```

**How to get your credentials:**

| Credential | Where to find it |
|---|---|
| `IBM_API_KEY` | [IBM Cloud → Manage → Access (IAM) → API keys](https://cloud.ibm.com/iam/apikeys) |
| `IBM_PROJECT_ID` | [IBM watsonx.ai → Projects → Your project → Manage → General](https://dataplatform.cloud.ibm.com) |
| `IBM_WML_URL` | Region-specific: `https://us-south.ml.cloud.ibm.com` (Dallas) |

### 5. Run the application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🌐 Supported Regional Languages (Translation)

Hindi · Tamil · Telugu · Marathi · Bengali · Kannada · Malayalam · Gujarati · Punjabi · Odia · Urdu

---

## 📝 Usage

1. **Paste text** or **upload a PDF / DOCX** in the sidebar.
2. (Optional) Select a regional language for translation.
3. Click the desired action tab:
   - **Simplify** → plain-English explanation
   - **Summary** → bullet-point recap
   - **Quiz** → 5 MCQs for practice
   - **Glossary** → key terms explained
4. Download results as `.txt` files.

---

## 🔒 Security Note

The `.env` file contains sensitive API keys. It is listed in `.gitignore` and should **never** be committed to version control.

---

## 📜 License

MIT License — free for educational use.

---

*CourseClarity AI · AICTE Problem Statement #19 · IBM Granite · IBM Cloud Lite*
