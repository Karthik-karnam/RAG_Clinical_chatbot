import os
import zipfile
import logging
from langchain_community.document_loaders import (
    PyPDFLoader, 
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_chain import ClinicalRAG
from langchain_community.document_loaders import UnstructuredFileLoader


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("document_ingestion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_documents(docs_path="docs"):
    """Load and process documents from a directory"""
    loaders = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".txt": TextLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".csv": UnstructuredFileLoader,  # Add CSV support
        ".pptx": UnstructuredFileLoader,  # Add PowerPoint support
    }
    
    documents = []
    total_files = 0
    skipped_files = []
    supported_extensions = list(loaders.keys())

    for file in os.listdir(docs_path):
        file_path = os.path.join(docs_path, file)
        _, ext = os.path.splitext(file)
        ext = ext.lower()

        if ext in loaders:
            total_files += 1
            try:
                logger.info(f"Processing: {file}")
                loader = loaders[ext](file_path)
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                logger.info(f"✅ Success: {file} ({len(loaded_docs)} chunks)")
            except zipfile.BadZipFile:
                logger.error(f"❌ Invalid document (corrupted?): {file}")
                skipped_files.append(file)
            except Exception as e:
                logger.error(f"❌ Failed to process {file}: {str(e)}")
                skipped_files.append(file)
        else:
            logger.warning(f"⚠️ Unsupported file type: {file} (extension: {ext})")
            skipped_files.append(file)

    if not documents:
        logger.warning("⚠️ No valid documents found to ingest.")
        return [], skipped_files

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Add source metadata
    for chunk in chunks:
        if "source" not in chunk.metadata:
            chunk.metadata["source"] = os.path.basename(file_path)
    
    return chunks, skipped_files


def ingest_documents(docs_path="docs"):
    rag = ClinicalRAG()
    chunks, skipped_files = process_documents(docs_path)
    
    if not chunks:
        logger.error("No documents to ingest. Exiting.")
        return

    # Ingest into vector database
    try:
        rag.vector_db.add_documents(chunks)
        rag.vector_db.persist()
        logger.info(f"\n✅ Ingest complete: {len(chunks)} chunks from {len(chunks) - len(skipped_files)} files")
        
        if skipped_files:
            logger.warning(f"⚠️ Skipped files: {', '.join(skipped_files)}")
            
    except Exception as e:
        logger.error(f"❌ Failed to ingest documents: {str(e)}")
    # rag = ClinicalRAG()
    # loaders = {
    #     ".pdf": PyPDFLoader,
    #     ".docx": Docx2txtLoader,
    #     ".txt": TextLoader,
    #     ".xlsx": UnstructuredExcelLoader
    # }
    
    # documents = []
    # total_files = 0
    # skipped_files = []

    # # for file in os.listdir(docs_path):
    # #     ext = os.path.splitext(file)[1]
    # #     if ext in loaders:
    # #         loader = loaders[ext](os.path.join(docs_path, file))
    # #         documents.extend(loader.load())
    # for file in os.listdir(docs_path):
    #     ext = os.path.splitext(file)[1].lower()
    #     file_path = os.path.join(docs_path, file)

    #     if ext in loaders:
    #         total_files += 1
    #         try:
    #             loader = loaders[ext](file_path)
    #             loaded_docs = loader.load()
    #             documents.extend(loaded_docs)
    #             print(f"✅ Loaded: {file} ({len(loaded_docs)} docs)")
    #         except zipfile.BadZipFile:
    #             print(f"❌ Invalid .docx file (not a zip): {file}")
    #             skipped_files.append(file)
    #         except Exception as e:
    #             print(f"❌ Failed to load {file}: {e}")
    #             skipped_files.append(file)
    #     else:
    #         print(f"⚠️ Skipped unsupported file type: {file}")
    
    # if not documents:
    #     print("⚠️ No valid documents found to ingest.")
    #     return


    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=1000,
    #     chunk_overlap=200
    # )
    # chunks = text_splitter.split_documents(documents)
    
    # # Add source metadata
    # for chunk in chunks:
    #     chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])
    
    # rag.vector_db.add_documents(chunks)
    # rag.vector_db.persist()
    # # print(f"Ingested {len(chunks)} chunks from {len(documents)} documents")
    # print(f"\n✅ Ingest complete: {len(chunks)} chunks from {total_files} files")
    # if skipped_files:
    #     print(f"⚠️ Skipped files: {skipped_files}")

if __name__ == "__main__":
    ingest_documents()