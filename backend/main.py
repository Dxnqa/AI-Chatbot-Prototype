from openai import OpenAI
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from Chatbot import ChatBot

# Path configurations
DIR = Path(__file__).resolve().parent
DB_PATH = DIR / "testing" / "database"
SOURCE_DIR = DIR / "testing" / "Notes"

def print_command_help() -> None:
    print(
        "\nCommands:\n"
        "  /add <id> <content>       Add or update a document in storage.\n"
        "  /get <id>                 Display a single document.\n"
        "  /remove <id>              Remove a document from storage.\n"
        "  /list                     List all stored documents.\n"
        "  /search <query>           Search stored documents.\n"
        "  /help                     Show this help message.\n"
        "  exit                      Quit the assistant."
    )

# Load API key from .env file. Make sure you have a .env file with OPENAI_API_KEY set.
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY environment variable is not set.\nPlease set it and re-run the script.")
    sys.exit(1)

client = OpenAI(api_key=api_key)


# Initialize the chatbot object from prompt.py with the OpenAI client
# Conversation array for conversation management
conversation_history = []
chatBot = ChatBot(client)

print("\nType 'exit' to end the conversation.")
print_command_help()

while True:
    user_input = input("\nAssistant: How can I help you today?\nPrompt: ")
    stripped_input = user_input.strip()
    if not stripped_input:
        continue

    if stripped_input.lower() in {"exit", "quit", "q"}:
        print("Goodbye!")
        break

    if stripped_input.startswith("/add "):
        try:
            _, remainder = stripped_input.split(" ", 1)
            document_id, content = remainder.split(" ", 1)
        except ValueError:
            print("Usage: /add <id> <content>")
            continue

        chatBot.add_document(document_id, content)
        print(f"Stored document '{document_id}'.")
        continue

    if stripped_input.startswith("/get "):
        _, document_id = stripped_input.split(" ", 1)
        document = chatBot.get_document(document_id)
        if not document:
            print(f"No document found for id '{document_id}'.")
            continue
        print(
            f"Document {document.document_id}:\n{document.content}\nMetadata: {document.metadata}"
        )
        continue

    if stripped_input.startswith("/remove "):
        _, document_id = stripped_input.split(" ", 1)
        removed = chatBot.remove_document(document_id)
        if not removed:
            print(f"No document found for id '{document_id}'.")
        else:
            print(f"Removed document '{document_id}'.")
        continue

    if stripped_input == "/list":
        documents = chatBot.list_documents()
        if not documents:
            print("No documents stored yet.")
        else:
            print("Stored documents:")
            for document in documents:
                preview = document.content[:60]
                if len(document.content) > 60:
                    preview += "..."
                print(f"- {document.document_id}: {preview}")
        continue

    if stripped_input.startswith("/search "):
        _, query = stripped_input.split(" ", 1)
        results = chatBot.search_documents(query)
        if not results:
            print("No documents matched the query.")
        else:
            print("Search results:")
            for document in results:
                preview = document.content[:60]
                if len(document.content) > 60:
                    preview += "..."
                print(f"- {document.document_id}: {preview}")
        continue

    if stripped_input == "/help":
        print_command_help()
        continue

    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = chatBot.web_search(conversation_history)
    except Exception as error:
        print(f"Assistant: Sorry, something went wrong ({error}). Let's try again.")
        continue

    assistant_reply = response.output_text
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    print(f"\nResponse: {assistant_reply}\n")