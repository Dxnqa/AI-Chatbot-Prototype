from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass
class Document:
    """Simple in-memory representation of a document."""

    document_id: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)

    def matches(self, query: str) -> bool:
        """Return True when the document content contains the query."""

        query_lower = query.lower()
        return query_lower in self.content.lower() or any(
            query_lower in value.lower() for value in self.metadata.values()
        )


class DocumentStorage:
    """In-memory storage to manage knowledge base documents."""

    def __init__(self):
        self._documents: Dict[str, Document] = {}

    def add_document(
        self, document_id: str, content: str, metadata: Optional[Dict[str, str]] = None
    ) -> Document:
        document = Document(
            document_id=document_id,
            content=content,
            metadata=metadata or {},
        )
        self._documents[document_id] = document
        return document

    def get_document(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)

    def remove_document(self, document_id: str) -> Optional[Document]:
        return self._documents.pop(document_id, None)

    def list_documents(self) -> Iterable[Document]:
        return self._documents.values()

    def search(self, query: str) -> List[Document]:
        query = query.strip()
        if not query:
            return []
        return [doc for doc in self._documents.values() if doc.matches(query)]


class ChatBot:
    def __init__(self, client, storage: Optional[DocumentStorage] = None):
        self.client = client
        self.storage = storage or DocumentStorage()

    # Web search tool integration. Look into adding fields for filtering domains and formatting results based on user needs.
    def web_search(self, query):
        return self.client.responses.create(
            model="gpt-5",
            tools=[{"type": "web_search"}],
            input=query,
            include=["web_search_call.action.sources"],
        )
        # Return the full response object; caller can access response.output_text
    
    # File search tool. Connect to MCP database. Requires API key with file search access. Maybe use vector DB? 
    def file_search(self, query):
        return self.client.responses.create(
            model="gpt-5-mini",
            tools=[{"type": "file_search"}],
            input=query,
            include=["file_search_call.action.sources"],
        )

    # Local document storage helpers for knowledge management.
    def add_document(
        self, document_id: str, content: str, metadata: Optional[Dict[str, str]] = None
    ):
        return self.storage.add_document(document_id, content, metadata)

    def get_document(self, document_id: str):
        return self.storage.get_document(document_id)

    def remove_document(self, document_id: str):
        return self.storage.remove_document(document_id)

    def list_documents(self):
        return list(self.storage.list_documents())

    def search_documents(self, query: str):
        return self.storage.search(query)
    
    