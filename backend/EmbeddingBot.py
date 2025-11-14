from typing import Optional
import chromadb
import uuid
import logging
from pathlib import Path
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI
from .config import OPENAI_API_KEY ,DB_PATH, SOURCE_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s")

class EmbeddingBot:
    def __init__(self, api_key: str, db_path: Path = DB_PATH):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding = OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base_openai",
            embedding_function=self.embedding
        )
        self.llm = OpenAI(api_key=OPENAI_API_KEY)

    # Method: Delete collection
    def delete_collection(self):
        self.client.delete_collection("knowledge_base_openai")
        logging.info("Collection 'knowledge_base_openai' deleted.")

    # Method: Querying collection
    def query_collection(self, query_text: str, n_results: Optional[int] = 1) -> dict:
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            logging.info(f"Query successful for text: {query_text}")
            return results
        except Exception as e:
            logging.exception("Failed to query collection.")
            return {"status": "error", "error": str(e)} 


    # Method: collect .txt files from the source directory        
    def collect_files(self, source_dir: Path = SOURCE_DIR) -> list[Path]:
        file_list = []
        file_list.extend(file for file in source_dir.rglob("*.txt") if file.is_file())
        return file_list

    # Method: read file content
    def read_file(self, file_path: Path):
        return file_path.read_text(encoding="utf-8", errors="ignore").strip()

    # Method: chunk text with a limit of 1500 characters. Return list of chunks
    def chunk_text(self, text: str, chunk_size: int = 1500) -> list[str]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")

        chunks: list[str] = []
        for start_index in range(0, len(text), chunk_size):
            if chunk := text[start_index : start_index + chunk_size]:
                chunks.append(chunk)

        return chunks

    # Method: Create a unique id for each chunk.
    def content_chunk_id(self, chunk: str) -> str:
        if not chunk:
            raise ValueError("Chunk cannot be empty")
        return str(uuid.uuid4().hex)
    
    # Method: Process files for logging. Returns a summary of results.
    def file_processing(self, log_list: list[str]) -> dict[str, int | list[dict[str, str]] | str]:
        results = {
            "status": "success",
            "files_processed": 0,
            "files_skipped": 0,
            "errors": []
        }
        for file in log_list:
            try:
                content = self.read_file(file)
                if not content:
                    logging.warning(f"Empty content in file: {file}")
                    results["files_skipped"] += 1
                else:
                    results["files_processed"] += 1
            except Exception as e:
                logging.exception(f"Failed to read file: {file}")
                results["files_skipped"] += 1
                results["errors"].append({"file": str(file), "error": str(e)})
        return results
    
    # Method: Process embeddings and chunks for logging.
    def embedding_logs(self, chunks: list[str]) -> dict[str, int | list[dict[str, str]] | str]:
        results = {
            "status": "success",
            "chunks_embedded": 0,
            "errors": []
        }
        for chunk in chunks:
            try:
                if not chunk:
                    logging.warning("Empty chunk encountered.")
                    results["errors"].append({"chunk": chunk, "error": "Empty chunk"})
                else:
                    results["chunks_embedded"] += 1
                    logging.info({results["status"]})
            except Exception as e:
                logging.exception("Failed to process chunk.")
                results["errors"].append({"chunk": chunk, "error": str(e)})
        return results
    
    # Main Method: Embed chunked pieces from "chunks" => add to collection.
    # For parameter embedding_list: use collect_files() to get list of files.
    def embed_files(self, embedding_list):
        processed_files = self.file_processing(embedding_list)
        for file in embedding_list:
            content = self.read_file(file)
            chunks = self.chunk_text(content, chunk_size=1500)
            embedding_logs = self.embedding_logs(chunks)
            chunk_ids = [f"{file.stem}_{self.content_chunk_id(chunk)}" for chunk in chunks]
            
            self.collection.add(
                documents=chunks,
                ids=chunk_ids,
                metadatas=[{"source_file": file.name} for _ in chunks]
            )
        return embedding_logs, processed_files
    
    # Instructions for LLM response.
    content_not_found = "Context not found. Would you like me to improvise using web search?"
    
    instructions = (
        f"Use the provided context to return a helpful answer for the user's query. Format the response clearly and concisely. "
        f"If the answer is not within context, respond with: {content_not_found}"
    )
    
    # Method: Get LLM response from OpenAI <= Pass embedded context as prompt
    def llm_response(self, prompt:str, context: list[str]) -> str:
        response = self.llm.responses.create(
            model="gpt-5",
            input=[
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{prompt}".strip()},
                {"role": "system", "content": self.instructions}
            ]
        )
        return response.output_text.replace("\n", " ").strip()
        
    def web_search(self, prompt: str, verbosity: str = "medium"):
        web_instructions = (
            "Use web search to provide a helpful, concise answer for the user's query. "
            "Cite or draw from the retrieved sources when relevant."
        )
        response = self.llm.responses.create(
            model="gpt-5-mini",
            tools=[
                {
                    "type": "web_search",
                    "filters": {
                        "allowed_domains": [
                            "geeksforgeeks.org",
                            "w3schools.com",
                            "stackoverflow.com",
                            "developer.mozilla.org",
                        ]
                    },
                }
            ],
            input=[
                {"role": "system", "content": web_instructions},
                {"role": "user", "content": prompt.strip()},
            ],
            text={"verbosity": verbosity}
        )
        return response.output_text.replace("\n", " ").strip()
    
    def response(self, prompt: str, n_results: Optional[int] = 1) -> str:
        query = self.query_collection(query_text=prompt, n_results=n_results).get("documents", [])[0]
        context_text = [f"{i}. {doc}" for i, doc in enumerate(query, start=1)]
        return self.llm_response(prompt=prompt, context=context_text)