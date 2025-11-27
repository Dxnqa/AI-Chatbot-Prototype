from ..database.Agent import RAG
from openai import OpenAI
from config import OPENAI_API_KEY, QDRANT_COLLECTION_NAME
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class Chat:
    """
    Chat class for handling user queries and generating responses using OpenAI LLMs.
    
    Args:
        model (str): The OpenAI model to use for generating responses. Default is "gpt-5-mini".
        key (str): The OpenAI API key for authentication. Default is taken from config.
        user (str): Optional user identifier for containerized sessions.
    """
    
    def __init__(
        self,
        model: str = "gpt-5-mini",
        key: str = OPENAI_API_KEY,
        user: str = None, rag_agent: RAG | None = None
        ):
        if not key:
            raise ValueError("OpenAI API key must be provided.")
        if not model:
            raise ValueError("Model name must be provided.")
        self.client = OpenAI(api_key=key)
        self.model = model
        self.user = user
        self.agent = rag_agent

# System configuration variables
    content_not_found = "I'm sorry, but I couldn't find any relevant information to answer your question."

    INSTRUCTIONS = (
        f"Use the provided context to return a helpful answer for the user's query. Format the response clearly and concisely. "
        f"If the answer is not within context, respond with: {content_not_found}"
    )

# Main methods
    def model_response(self, query: str, system: str = INSTRUCTIONS) -> str:
        # Format user input with context
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": query.strip()},
            ]
        )
        return response.output_text.replace("\n", " ").strip()
    
    def query_pipeline(self, query:str) -> str:
        # Step 1: Embed the user query
        embeddings = self.embed_queries(query=query)

        # Step 2: Retrieve relevant context using RAG agent
        context = self.retrieve_context(embeddings=embeddings, limit=6)

        # Step 3: Generate final response using LLM with context
        final_response = self.model_response(query=query, system=f"{self.INSTRUCTIONS}\n\nContext:\n{context}")
        
        logging.info("Generated final response for user query.")
        return final_response
    
    # Helper methods        
    def embed_queries(self, query:str, model:str="text-embedding-3-small") -> list[float]:
        embedding = self.client.embeddings.create(model=model, input=query, dimensions=1536).data[0].embedding
        logging.info(f"Generated embedding for query of length {len(query)}.")
        return embedding

    def retrieve_context(self, embeddings: list[float], limit:int=6) -> str:
        if self.agent is None:
            raise ValueError("RAG agent is not initialized. Cannot retrieve context.")

        documents = self.agent.similarity_search(query_embedding=embeddings, top_k=limit)
        
        if results := [doc.payload.get("text", "") for doc in documents]:
            logging.info(f"Formatting {len(results)} results for response.")
            return self.format_results(results=results)
        else:
            logging.warning("No relevant documents found for the given query embedding.")
            return self.content_not_found
        
    
    def format_results(self, results:list[str], model:str = "gpt-5-nano", max_chars:int = 8000) -> str:
        if not results:
            return self.content_not_found
        
        context = "\n\n".join(results).strip()
        
        if not context:
            return self.content_not_found

        if len(context) > max_chars:
            context = context[:max_chars]

        try:
            formatted_results = self.client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes context for downstream QA."},
                    {"role": "developer", "content": "Read the provided context and rewrite it concisely as one clear summary. Avoid speculation."},
                    {"role": "user", "content": f"Context:\n{context}"}
                ]
            )
            logging.info("Successfully formatted results using LLM.")
            return formatted_results.output_text.replace("\n", " ").strip()
        except Exception as e:
            logging.error(f"Error formatting results: {e}")
            return self.content_not_found