from dotenv import load_dotenv
import sys
from pathlib import Path
from EmbeddingBot import EmbeddingBot
from config import OPENAI_API_KEY, DB_PATH, SOURCE_DIR

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY environment variable is not set.\nPlease set it and re-run the script.")
    sys.exit(1)

assistant = EmbeddingBot(api_key=OPENAI_API_KEY, db_path=DB_PATH)

collect_files = assistant.collect_files(source_dir=SOURCE_DIR)

# embedding_logs = assistant.embed_files(collect_files)

while True:
    print(f"\nCollection count: {assistant.collection.count()}")
    print("----------------------------------------------------\n")
    user_query = input("Enter your query: ")
    if user_query.strip().lower() in {"/exit", "exit", "quit", "q"}:
        print("Goodbye!")
        break

    query = assistant.query_collection(query_text=user_query, n_results=1).get("documents", [])[0]

    context = [f"{i}. {doc}" for i, doc in enumerate(query, start=1)]

    response =  assistant.llm_response(prompt=user_query, context=context)

    print("----------------------------------------------------\n")
    if response == assistant.content_not_found:
        print(assistant.content_not_found)
        use_web_search = input("\nConduct web search?: ").strip().lower()
        verbosity = input("Select verbosity (low, medium, high) [default: medium]: ").strip().lower()
        if use_web_search in {"yes", "y"}:
            print("Performing web search...\n")
            web_response = assistant.web_search(prompt=user_query, verbosity=verbosity)
            print(f"\nWeb Search Response:\n")
            print(f"{web_response}\n")
        else:
            continue
    else:
        print(f"LLM Response:\n{response}\n")
    print("----------------------------------------------------")
    
# print("\nContext results:\n")