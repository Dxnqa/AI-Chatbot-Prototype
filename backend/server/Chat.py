from openai import OpenAI
from config import OPENAI_API_KEY

class Chat:
    """
    Chat class for handling user queries and generating responses using OpenAI LLMs.
    
    Args:
        model (str): The OpenAI model to use for generating responses. Default is "gpt-5o".
        key (str): The OpenAI API key for authentication. Default is taken from config.
        user (str): Optional user identifier for containerized sessions.
    """
    
    def __init__(self, model: str = "gpt-4o", key: str = OPENAI_API_KEY, user: str = None):
        self.client = OpenAI(api_key=key)
        self.model = model
        self.user = user

# System configuration variables
    content_not_found = "I'm sorry, but I couldn't find any relevant information to answer your question."

    INSTRUCTIONS = (
        f"Use the provided context to return a helpful answer for the user's query. Format the response clearly and concisely. "
        f"If the answer is not within context, respond with: {content_not_found}"
    )

# Class methods
    def receive_query(self, query: str, system: str = INSTRUCTIONS, context: list[str] = None) -> str:
        # Format user input with context
        user_context_format = f"Context:\n{context}\n\nQuestion:\n{query}".strip()
        
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_context_format},
            ]
        )
        return response.output_text.replace("\n", " ").strip()