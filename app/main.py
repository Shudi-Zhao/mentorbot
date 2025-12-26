"""MentorBot - AI Onboarding Assistant for New Hires"""
import streamlit as st
import logging
from pathlib import Path
import hashlib
from typing import List, Dict, Any
import time

# Import application modules
from config import settings
from parsers import PDFParser, MarkdownParser, CSVParser
from chunking import TokenBasedChunker
from embeddings import EmbeddingService
from vectordb import ChromaService
from qa import QAService
from cleanup import DataCleanupManager, schedule_cleanup

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="MentorBot - Your AI Onboarding Guide",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chroma_service" not in st.session_state:
        st.session_state.chroma_service = None
    if "embedding_service" not in st.session_state:
        st.session_state.embedding_service = None
    if "qa_service" not in st.session_state:
        st.session_state.qa_service = None
    if "indexed_files" not in st.session_state:
        st.session_state.indexed_files = set()
    if "processing_log" not in st.session_state:
        st.session_state.processing_log = []
    if "last_chunk_size" not in st.session_state:
        st.session_state.last_chunk_size = settings.DEFAULT_CHUNK_SIZE
    if "last_chunk_overlap" not in st.session_state:
        st.session_state.last_chunk_overlap = settings.DEFAULT_CHUNK_OVERLAP

    # Initialize cleanup manager
    if "cleanup_manager" not in st.session_state:
        st.session_state.cleanup_manager = DataCleanupManager(
            upload_dir=settings.UPLOAD_DIR,
            chroma_dir=settings.CHROMA_DIR,
            max_age_hours=settings.MAX_FILE_AGE_HOURS,
        )

        # Start background cleanup if enabled
        if settings.ENABLE_AUTO_CLEANUP and "cleanup_scheduled" not in st.session_state:
            schedule_cleanup(
                cleanup_manager=st.session_state.cleanup_manager,
                interval_minutes=settings.CLEANUP_INTERVAL_MINUTES,
            )
            st.session_state.cleanup_scheduled = True
            logger.info("Auto-cleanup enabled")


def get_file_hash(file_bytes: bytes) -> str:
    """Calculate hash of file content."""
    return hashlib.sha256(file_bytes).hexdigest()


def parse_document(file_path: Path) -> List[Dict[str, Any]]:
    """Parse document based on file type."""
    suffix = file_path.suffix.lower()

    try:
        if suffix == ".pdf":
            return PDFParser.parse(file_path)
        elif suffix == ".md" or suffix == ".txt":
            return MarkdownParser.parse(file_path)
        elif suffix == ".csv":
            return CSVParser.parse(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    except Exception as e:
        logger.error(f"Error parsing {file_path.name}: {str(e)}")
        raise


def auto_load_demo_content(chunk_size: int, chunk_overlap: int) -> bool:
    """
    Automatically load demo content on first launch.

    Returns:
        True if demo content was loaded, False otherwise
    """
    # Only auto-load if collection is empty
    if st.session_state.chroma_service is None:
        return False

    stats = st.session_state.chroma_service.get_stats()
    if stats["total_chunks"] > 0:
        return False  # Already has content

    # Check if we've already attempted auto-load in this session
    if st.session_state.get("demo_auto_loaded", False):
        return False

    demo_file_path = settings.BASE_DIR / "demo_content" / "data_scientist_onboarding.md"
    if not demo_file_path.exists():
        return False

    try:
        st.session_state.demo_auto_loaded = True

        # Read demo file
        with open(demo_file_path, "rb") as f:
            file_bytes = f.read()

        file_hash = get_file_hash(file_bytes)

        # Check if already indexed
        if st.session_state.chroma_service.check_document_exists(file_hash):
            st.session_state.indexed_files.add(demo_file_path.name)
            return False

        # Initialize chunker
        chunker = TokenBasedChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Save temporarily for parsing
        temp_path = settings.UPLOAD_DIR / demo_file_path.name
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        # Parse document
        documents = parse_document(temp_path)

        # Chunk documents
        chunks = chunker.chunk_documents(documents)

        # Generate embeddings
        chunk_texts = [chunk["chunk_text"] for chunk in chunks]
        embeddings = st.session_state.embedding_service.embed_batch(chunk_texts, show_progress=False)

        # Add to vector database
        st.session_state.chroma_service.add_chunks(chunks, embeddings)
        st.session_state.indexed_files.add(demo_file_path.name)

        logger.info(f"Auto-loaded demo content: {demo_file_path.name}")
        return True

    except Exception as e:
        logger.error(f"Error auto-loading demo content: {str(e)}")
        return False


def process_uploaded_files(uploaded_files, chunk_size: int, chunk_overlap: int, openai_api_key: str, include_demo_file: bool = False):
    """Process uploaded files and add to vector database."""
    # Build list of files to process
    files_to_process = []

    # Add uploaded files
    if uploaded_files:
        files_to_process.extend(uploaded_files)

    # Add demo file if selected
    if include_demo_file:
        demo_file_path = settings.BASE_DIR / "demo_content" / "data_scientist_onboarding.md"
        if demo_file_path.exists():
            # Create a pseudo uploaded file object for demo file
            class DemoFile:
                def __init__(self, path):
                    self.path = path
                    self.name = path.name
                    self._content = None

                def read(self):
                    if self._content is None:
                        with open(self.path, 'rb') as f:
                            self._content = f.read()
                    return self._content

            files_to_process.append(DemoFile(demo_file_path))

    if not files_to_process:
        st.warning("Please upload at least one file or select the demo content.")
        return

    if not openai_api_key:
        st.error("Please provide your OpenAI API key in the sidebar.")
        return

    # Initialize services
    if st.session_state.embedding_service is None:
        with st.spinner("Loading embedding model..."):
            st.session_state.embedding_service = EmbeddingService(settings.EMBEDDING_MODEL)
            st.success(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")

    if st.session_state.chroma_service is None:
        st.session_state.chroma_service = ChromaService(
            persist_directory=settings.CHROMA_DIR,
            collection_name=settings.CHROMA_COLLECTION_NAME,
        )

    if st.session_state.qa_service is None:
        st.session_state.qa_service = QAService(api_key=openai_api_key, model=settings.OPENAI_MODEL)

    # Initialize chunker
    chunker = TokenBasedChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_files = len(files_to_process)
    processed_count = 0

    for idx, uploaded_file in enumerate(files_to_process):
        try:
            # Calculate file hash
            file_bytes = uploaded_file.read()
            file_hash = get_file_hash(file_bytes)

            # Check file size limit
            file_size_mb = len(file_bytes) / (1024 * 1024)
            if file_size_mb > settings.MAX_FILE_SIZE_MB:
                st.error(
                    f"⚠️ File '{uploaded_file.name}' is too large ({file_size_mb:.1f}MB). "
                    f"Maximum allowed size is {settings.MAX_FILE_SIZE_MB}MB."
                )
                processed_count += 1
                progress_bar.progress(processed_count / total_files)
                continue

            # Check storage limits
            if settings.ENABLE_AUTO_CLEANUP:
                st.session_state.cleanup_manager.enforce_storage_limits(max_size_mb=settings.MAX_STORAGE_MB)

            # Check if already indexed
            if st.session_state.chroma_service.check_document_exists(file_hash):
                st.info(f"⏭️ Skipping {uploaded_file.name} (already indexed)")
                st.session_state.indexed_files.add(uploaded_file.name)
                processed_count += 1
                progress_bar.progress(processed_count / total_files)
                continue

            status_text.text(f"Processing {uploaded_file.name}...")

            # Save file to disk
            file_path = settings.UPLOAD_DIR / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            # Parse document
            documents = parse_document(file_path)
            st.session_state.processing_log.append(f"✅ Parsed {uploaded_file.name}: {len(documents)} sections")

            # Chunk documents
            chunks = chunker.chunk_documents(documents)
            st.session_state.processing_log.append(f"✂️ Created {len(chunks)} chunks")

            # Generate embeddings
            status_text.text(f"Generating embeddings for {uploaded_file.name}...")
            chunk_texts = [chunk["chunk_text"] for chunk in chunks]
            embeddings = st.session_state.embedding_service.embed_batch(chunk_texts, show_progress=False)
            st.session_state.processing_log.append(f"🔢 Generated {len(embeddings)} embeddings")

            # Add to vector database
            st.session_state.chroma_service.add_chunks(chunks, embeddings)
            st.session_state.processing_log.append(f"💾 Added to vector database\n")

            st.session_state.indexed_files.add(uploaded_file.name)
            processed_count += 1
            progress_bar.progress(processed_count / total_files)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            logger.error(f"Error processing {uploaded_file.name}: {str(e)}")

    status_text.text("✅ Processing complete!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()


def main():
    """Main application."""
    initialize_session_state()

    # Title and welcome message
    st.title("🤖 MentorBot - Your AI Onboarding Assistant")
    st.markdown(
        """
    **Welcome to your 24/7 onboarding companion!** 👋

    MentorBot helps new hires get instant answers from company knowledge. Upload your onboarding guides,
    handbooks, and documentation, then ask questions anytime - no need to wait for your manager or teammates.

    **Get started:**
    1. Upload your onboarding documents (or try our demo content)
    2. Process & index the files
    3. Ask questions and get answers with citations

    **Try asking:** "Who is my manager?" or "How do I request data access?"
    """
    )

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    # OpenAI API Key
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Required for question answering")

    st.sidebar.markdown("---")

    # Chunking parameters
    st.sidebar.subheader("Chunking Settings")
    chunk_size = st.sidebar.slider(
        "Chunk Size (tokens)",
        min_value=settings.MIN_CHUNK_SIZE,
        max_value=settings.MAX_CHUNK_SIZE,
        value=settings.DEFAULT_CHUNK_SIZE,
        step=50,
        help="Maximum number of tokens per chunk",
    )
    st.session_state.last_chunk_size = chunk_size

    chunk_overlap = st.sidebar.slider(
        "Chunk Overlap (tokens)",
        min_value=0,
        max_value=200,
        value=settings.DEFAULT_CHUNK_OVERLAP,
        step=10,
        help="Number of overlapping tokens between chunks",
    )
    st.session_state.last_chunk_overlap = chunk_overlap

    st.sidebar.markdown("---")

    # Retrieval parameters
    st.sidebar.subheader("Retrieval Settings")
    top_k = st.sidebar.slider(
        "Top K Results",
        min_value=1,
        max_value=settings.MAX_TOP_K,
        value=settings.DEFAULT_TOP_K,
        help="Number of chunks to retrieve",
    )

    show_chunks = st.sidebar.checkbox("Show Retrieved Chunks", value=False)

    st.sidebar.markdown("---")

    # Reset button
    if st.sidebar.button("🗑️ Clear All Data", type="secondary"):
        if st.session_state.chroma_service:
            st.session_state.chroma_service.reset_collection()
        st.session_state.indexed_files = set()
        st.session_state.processing_log = []
        st.sidebar.success("All data cleared!")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Knowledge Base", "💬 Ask Your Mentor", "📊 Analytics", "📖 Demo Content"])

    # Tab 1: Knowledge Base
    with tab1:
        st.header("Company Knowledge Base")

        # Demo content section
        demo_file_path = settings.BASE_DIR / "demo_content" / "data_scientist_onboarding.md"
        demo_file_exists = demo_file_path.exists()

        if demo_file_exists:
            st.subheader("📋 Demo Content")
            include_demo = st.checkbox(
                "Include demo onboarding guide (Data Scientist role)",
                value=False,
                help="Process the sample Data Scientist onboarding guide to try out MentorBot"
            )
            if include_demo:
                st.info("💡 Demo file will be processed when you click 'Process & Index Files' below.")
        else:
            include_demo = False

        st.markdown("---")

        # File uploader
        st.subheader("📁 Upload Your Documents")
        uploaded_files = st.file_uploader(
            "Choose files (PDF, MD, TXT, CSV)",
            type=["pdf", "md", "txt", "csv"],
            accept_multiple_files=True,
            help="Upload one or more documents to index",
        )

        # Enable button if either uploaded files or demo selected
        can_process = bool(uploaded_files) or include_demo

        if st.button("🚀 Process & Index Files", type="primary", disabled=not can_process):
            process_uploaded_files(uploaded_files, chunk_size, chunk_overlap, openai_api_key, include_demo_file=include_demo)

        # Show processing log
        if st.session_state.processing_log:
            with st.expander("📋 Processing Log", expanded=True):
                for log_entry in st.session_state.processing_log[-10:]:  # Show last 10 entries
                    st.text(log_entry)

        # Show indexed files
        if st.session_state.indexed_files:
            st.subheader("Indexed Files")
            for filename in sorted(st.session_state.indexed_files):
                st.text(f"✓ {filename}")

    # Tab 2: Ask Questions
    with tab2:
        st.header("Ask Your Mentor")

        if not openai_api_key:
            st.warning("⚠️ Please provide your OpenAI API key in the sidebar to use the Q&A feature.")
        elif not st.session_state.indexed_files:
            st.info("ℹ️ Please upload and index documents first in the Knowledge Base tab.")
        else:
            # Quick question buttons
            st.subheader("Quick Start Questions")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("👤 Who is my manager?", use_container_width=True):
                    st.session_state.selected_question = "Who is my manager?"
                if st.button("📊 What tools do I need?", use_container_width=True):
                    st.session_state.selected_question = "What tools do I need access to?"

            with col2:
                if st.button("📁 How do I request data access?", use_container_width=True):
                    st.session_state.selected_question = "How do I request data access?"
                if st.button("📅 When are team meetings?", use_container_width=True):
                    st.session_state.selected_question = "When are the team meetings?"

            with col3:
                if st.button("🎯 What are my responsibilities?", use_container_width=True):
                    st.session_state.selected_question = "What are my main responsibilities?"
                if st.button("🚀 How do I deploy a model?", use_container_width=True):
                    st.session_state.selected_question = "How do I deploy a machine learning model to production?"

            st.markdown("---")

            # Handle quick-start button clicks - always override current question
            if "selected_question" in st.session_state:
                st.session_state.current_question = st.session_state.selected_question
                del st.session_state.selected_question

            # Question input with unique key to prevent browser password autofill
            question = st.text_input(
                "Or enter your own question:",
                value=st.session_state.get("current_question", ""),
                placeholder="Ask anything about your role, team, or processes...",
                key="mentor_question_input",
            )

            # Update current question when user types
            if question != st.session_state.get("current_question", ""):
                st.session_state.current_question = question

            if st.button("🔍 Get Answer", type="primary", disabled=not question):
                if st.session_state.qa_service is None:
                    st.error("QA service not initialized. Please check your API key.")
                else:
                    with st.spinner("Searching and generating answer..."):
                        # Embed question (use the current question value)
                        question_embedding = st.session_state.embedding_service.embed_text(question)

                        # Retrieve chunks
                        results = st.session_state.chroma_service.query(
                            query_embedding=question_embedding,
                            top_k=top_k,
                        )

                        # Generate answer
                        qa_result = st.session_state.qa_service.answer_question(
                            question=question,
                            retrieved_chunks=results["documents"],
                            metadatas=results["metadatas"],
                        )

                        # Display answer
                        st.subheader("Answer")
                        st.markdown(qa_result["answer"])

                        # Display citations
                        if qa_result["citations"]:
                            st.subheader("📎 Citations")
                            for citation in qa_result["citations"]:
                                cite_text = f"**[{citation['source_number']}]** {citation['filename']}"

                                if "page" in citation:
                                    cite_text += f" - Page {citation['page']}"
                                elif "section" in citation:
                                    cite_text += f" - {citation['section']}"
                                elif "row" in citation and citation["row"] > 0:
                                    cite_text += f" - Row {citation['row']}"

                                st.markdown(cite_text)

                        # Show retrieved chunks if enabled
                        if show_chunks and results["documents"]:
                            with st.expander("📄 Retrieved Chunks"):
                                for i, (chunk, metadata) in enumerate(
                                    zip(results["documents"], results["metadatas"]), start=1
                                ):
                                    st.markdown(f"**Chunk {i}** - {metadata.get('filename', 'Unknown')}")
                                    st.text(chunk[:500] + "..." if len(chunk) > 500 else chunk)
                                    st.markdown("---")

    # Tab 3: Statistics
    with tab3:
        st.header("Collection Statistics")

        if st.session_state.chroma_service:
            stats = st.session_state.chroma_service.get_stats()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Documents", stats["total_documents"])

            with col2:
                st.metric("Total Chunks", stats["total_chunks"])

            with col3:
                avg_chunks = (
                    stats["total_chunks"] / stats["total_documents"] if stats["total_documents"] > 0 else 0
                )
                st.metric("Avg Chunks/Doc", f"{avg_chunks:.1f}")

            if stats["file_types"]:
                st.subheader("File Types")
                for file_type, count in stats["file_types"].items():
                    st.text(f"{file_type}: {count} chunks")

        else:
            st.info("No data indexed yet.")

        # Storage usage section
        st.markdown("---")
        st.subheader("📊 Storage Usage")

        if st.session_state.cleanup_manager:
            storage_stats = st.session_state.cleanup_manager.get_storage_usage()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Uploaded Files", storage_stats["upload_count"])

            with col2:
                st.metric("Uploads Size", f"{storage_stats['upload_size_mb']:.2f} MB")

            with col3:
                st.metric("Database Size", f"{storage_stats['chroma_size_mb']:.2f} MB")

            # Progress bar for storage limit
            if settings.ENABLE_AUTO_CLEANUP:
                storage_percent = (storage_stats["total_size_mb"] / settings.MAX_STORAGE_MB) * 100
                st.progress(min(storage_percent / 100, 1.0))
                st.caption(
                    f"Total: {storage_stats['total_size_mb']:.2f} MB / {settings.MAX_STORAGE_MB} MB "
                    f"({storage_percent:.1f}%)"
                )

                st.info(
                    f"ℹ️ **Auto-cleanup enabled**: Files older than {settings.MAX_FILE_AGE_HOURS} hour(s) "
                    f"will be automatically deleted."
                )

    # Tab 4: Demo Content
    with tab4:
        st.header("Demo Content Preview")
        st.info("This is the sample Data Scientist onboarding guide included with MentorBot. You can use this to test the system without uploading your own documents.")

        demo_file_path = settings.BASE_DIR / "demo_content" / "data_scientist_onboarding.md"

        if demo_file_path.exists():
            try:
                with open(demo_file_path, 'r', encoding='utf-8') as f:
                    demo_content = f.read()

                st.markdown(demo_content)

            except Exception as e:
                st.error(f"Error reading demo file: {str(e)}")
        else:
            st.warning("Demo content file not found.")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
    ### About MentorBot
    Your AI-powered onboarding assistant that provides instant answers from company knowledge.

    **How it works:**
    1. Upload onboarding guides & docs
    2. Ask questions anytime
    3. Get cited answers instantly

    **Perfect for:**
    - New hire onboarding
    - Team knowledge sharing
    - Process documentation
    - Training materials

    **Tech Stack:** RAG · OpenAI · ChromaDB
    """
    )


if __name__ == "__main__":
    main()
