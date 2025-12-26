# MentorBot - AI Onboarding Assistant

A production-ready **Retrieval-Augmented Generation (RAG)** system designed to help new hires get instant answers from company onboarding documents. Built as a portfolio demonstration for Data Engineering, Data Science, and Data Analytics roles.

## Overview

**MentorBot** is an AI-powered onboarding assistant that provides 24/7 support for new employees and interns. Instead of waiting for managers or teammates, new hires can upload onboarding guides and ask questions to get immediate, cited answers based on company documentation.

## Features

### Core Capabilities
- **Document Upload**: Support for PDF, Markdown, CSV, and TXT files
- **Intelligent Chunking**: Token-based chunking with configurable size and overlap
- **Semantic Search**: Vector similarity search using sentence-transformers
- **Grounded Q&A**: Answers based **only** on uploaded documents (no hallucinations)
- **Citations**: Every answer includes source references with file and location info
- **Quick-Start Questions**: Pre-populated common onboarding questions
- **Demo Content**: Sample Data Scientist onboarding guide for testing
- **Auto-Cleanup**: Automatic data cleanup to prevent abuse in public demos

### Technical Highlights
- **Idempotent Indexing**: Content hash-based deduplication prevents re-processing
- **Metadata Tracking**: Full lineage from source file to chunk level
- **Configurable Pipeline**: Adjustable chunking, retrieval, and embedding parameters
- **Persistent Storage**: ChromaDB with persistent vector storage
- **Error Handling**: Graceful failures with clear user feedback
- **Data Management**: Time-based and storage-limit cleanup for portfolio deployment

---

## Architecture

```
┌─────────────────┐
│  User Uploads   │
│  (PDF/MD/CSV)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  File Parser    │  ← PDFParser, MarkdownParser, CSVParser
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Token Chunker   │  ← Configurable size/overlap
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embedding Model │  ← all-MiniLM-L6-v2 (384-dim)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ChromaDB      │  ← Persistent vector storage
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Search   │  ← Top-k retrieval
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI GPT     │  ← Grounded answer generation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Answer + Cites  │
└─────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.9+ (or Docker & Docker Compose)
- OpenAI API Key

### Option 1: Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd upload-to-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and add your API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Run the application
streamlit run app/main.py
```

The app will be available at `http://localhost:8501`

### Option 2: Docker Deployment

```bash
# Clone and setup
git clone <your-repo-url>
cd upload-to-rag
cp .env.example .env

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Build and start
docker-compose up --build
```

### Using the Application

1. **Try Demo Content**:
   - Go to "Knowledge Base" tab
   - Check "Include demo onboarding guide"
   - Enter your OpenAI API key in the sidebar
   - Click "Process & Index Files"

2. **Ask Questions**:
   - Go to "Ask Your Mentor" tab
   - Click quick-start buttons like "Who is my manager?"
   - Or enter your own questions
   - View answers with citations

3. **Upload Your Own Docs**:
   - Upload PDF, MD, TXT, or CSV files in "Knowledge Base" tab
   - Process and index them
   - Ask questions specific to your documents

4. **View Demo Content**:
   - Go to "Demo Content" tab to see the sample onboarding guide

---

## Project Structure

```
upload-to-rag/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Streamlit UI
│   ├── config.py               # Configuration settings
│   ├── cleanup.py              # Auto-cleanup manager
│   ├── parsers/
│   │   ├── pdf_parser.py       # PDF document parser
│   │   ├── markdown_parser.py  # Markdown parser
│   │   └── csv_parser.py       # CSV parser
│   ├── chunking/
│   │   └── chunker.py          # Token-based chunking
│   ├── embeddings/
│   │   └── embedding_service.py # Sentence-transformer embeddings
│   ├── vectordb/
│   │   └── chroma_service.py   # ChromaDB integration
│   └── qa/
│       └── qa_service.py       # OpenAI Q&A with citations
├── demo_content/
│   ├── data_scientist_onboarding.md  # Sample onboarding guide
│   └── sample_questions.md           # Test questions
├── data/
│   ├── uploads/                # Uploaded files
│   └── chroma_db/              # ChromaDB persistence
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional LLM settings
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.1
MAX_TOKENS=1000

# Optional embedding settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional chunking settings
DEFAULT_CHUNK_SIZE=512
DEFAULT_CHUNK_OVERLAP=50
MIN_CHUNK_SIZE=100
MAX_CHUNK_SIZE=2000

# Optional retrieval settings
DEFAULT_TOP_K=5
MAX_TOP_K=20

# Auto-cleanup settings (for portfolio/demo deployment)
ENABLE_AUTO_CLEANUP=true
MAX_FILE_AGE_HOURS=1.0          # Delete files older than 1 hour
MAX_STORAGE_MB=100              # Max 100MB total storage
MAX_FILE_SIZE_MB=10             # Max 10MB per file
CLEANUP_INTERVAL_MINUTES=30     # Run cleanup every 30 minutes
```

### UI Controls

**Chunking Settings**
- Chunk Size: 100-2000 tokens (default: 512)
- Chunk Overlap: 0-200 tokens (default: 50)

**Retrieval Settings**
- Top K: 1-20 results (default: 5)
- Show Retrieved Chunks: Toggle to see raw context

---

## Design Decisions

### Why Token-Based Chunking?
Token-based chunking ensures compatibility with LLM token limits and provides more accurate chunk sizing compared to character-based methods. We use `tiktoken` with the `cl100k_base` encoding (GPT-3.5/4 standard).

### Why all-MiniLM-L6-v2?
- **Fast**: Efficient inference for demos
- **Good quality**: Strong retrieval performance for general text
- **Free**: No API costs
- **Small footprint**: 384-dimensional embeddings

### Why Citations Matter?
Citations provide:
1. **Transparency**: Users can verify answers
2. **Trust**: Reduces hallucination concerns
3. **Traceability**: Essential for onboarding and compliance

### Why Content Hashing?
Prevents duplicate processing by detecting identical files, saving compute and storage.

### Why Auto-Cleanup?
For portfolio/demo deployment, auto-cleanup prevents abuse by:
- Deleting old files after configurable time period
- Enforcing storage limits
- Running on background schedule
- Keeping demo fresh for new visitors

---

## Usage Examples

### Example 1: New Hire Onboarding

1. Upload your company's onboarding guide (PDF or Markdown)
2. Ask: "Who is my manager?"
3. Get answer with citations: `[1] onboarding_guide.pdf - Page 2`

### Example 2: Team Process Documentation

1. Upload team wiki pages as Markdown files
2. Ask: "How do I request data access?"
3. Get step-by-step instructions with source links

### Example 3: Tools and Setup

1. Upload tools documentation (PDF, CSV of tools list)
2. Ask: "What tools do I need access to?"
3. Get consolidated list from multiple sources

---

## Demo Content

The project includes sample onboarding content to demonstrate MentorBot's capabilities:

### Data Scientist Onboarding Guide
- **Location**: `demo_content/data_scientist_onboarding.md`
- **Contents**: Comprehensive fake onboarding guide including:
  - Team members and contacts
  - Tools and access requirements
  - Common workflows (data access, A/B testing, model deployment)
  - Meeting schedules
  - FAQ section

### Sample Questions
- **Location**: `demo_content/sample_questions.md`
- **Contents**: 80+ categorized test questions covering:
  - Getting started
  - Tools and systems
  - Workflows
  - Projects
  - Meetings
  - Career development

---

## Features in Detail

### Quick-Start Questions
Six pre-populated buttons for common onboarding queries:
- "Who is my manager?"
- "What tools do I need?"
- "How do I request data access?"
- "When are team meetings?"
- "What are my responsibilities?"
- "How do I deploy a model?"

### Analytics Dashboard
Track usage and storage:
- Total documents and chunks indexed
- Average chunks per document
- File types breakdown
- Storage usage (uploads + database)
- Auto-cleanup status

### Data Cleanup System
Automatic maintenance for demo deployment:
- **Time-based cleanup**: Delete files older than X hours
- **Storage limits**: Enforce max storage quota
- **Background scheduler**: Runs cleanup automatically
- **Manual reset**: Clear all data button in sidebar

---

## Limitations and Future Work

### Current Limitations
- **Single-user**: No authentication or multi-tenant support
- **Keyword search**: No hybrid BM25 + vector search
- **No reranking**: Results ordered by vector similarity only
- **Basic chunking**: No semantic chunking or sentence-aware splitting

### Planned Enhancements
- [ ] Hybrid search (BM25 + vector) for better keyword matching
- [ ] Reranking with cross-encoder models
- [ ] MMR (Maximal Marginal Relevance) for diversity
- [ ] Evaluation harness with hit rate and MRR metrics
- [ ] User sessions / collections for multi-user support
- [ ] Support for DOCX and Excel files
- [ ] Conversation history and follow-up questions

---

## Portfolio Highlights

This project demonstrates:

### For Data Engineering (DE)
- End-to-end data pipeline design
- Heterogeneous data ingestion (PDF, CSV, Markdown)
- Schema normalization and metadata tracking
- Idempotent processing with content hashing
- Infrastructure as code (Docker, docker-compose)
- Data persistence and volume management
- Automatic cleanup and data lifecycle management

### For Data Science (DS)
- Embedding model selection and integration
- Chunking strategy implementation
- Vector similarity search
- Prompt engineering for grounded generation
- Hallucination control techniques
- RAG pipeline optimization

### For Data Analytics (DA)
- Building tools for data-driven decision making
- Source traceability and citation systems
- User-facing analytics (statistics tab)
- Data quality considerations (deduplication, validation)
- Product-minded UX design

---

## Troubleshooting

### "Model not found" error
The embedding model will download automatically on first run. Ensure you have internet access and ~500MB disk space.

### "OpenAI API error"
Verify your API key is correct and has credits. Check `.env` file or sidebar input.

### ChromaDB persistence issues
Ensure data directories exist: `data/uploads/` and `data/chroma_db/`. The app will create them automatically.

### Memory issues
Large PDFs may require more RAM. Adjust Docker memory limits or process files in batches.

### Password autofill prompt
Some browsers may show password save prompts. This is due to the OpenAI API key input field and can be safely ignored.

---

## License

MIT License - Feel free to use for your portfolio!

---

## Contact

Built as a portfolio demonstration project.

**Skills demonstrated**: RAG pipeline, vector search, grounded Q&A, production deployment, data management, UX design

---

## Acknowledgments

- **Streamlit**: For the amazing web framework
- **ChromaDB**: For simple and effective vector storage
- **OpenAI**: For GPT models
- **Sentence Transformers**: For embedding models
- **LangChain Community**: For RAG best practices
