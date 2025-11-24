from qdrant_client import QdrantClient, models
from config import QDRANT_URL, QDRANT_COLLECTION_NAME, QDRANT_API_KEY
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

print(f"Number of points in {QDRANT_COLLECTION_NAME}: {client.get_collection(QDRANT_COLLECTION_NAME).points_count}")

retrieve_points = client.scroll(collection_name=QDRANT_COLLECTION_NAME,
                                limit=100, 
                                with_payload=True, 
                                with_vectors=False,
                                scroll_filter=models.Filter(
                                    must=[
                                        models.FieldCondition(
                                            key="title",
                                            match=models.MatchValue(value="candlesticks.pdf")
                                        ),
                                    ]
                                )
                                )

for point in retrieve_points[0]:
    print(f"ID: {point.id}")
    print(f"Title: {point.payload.get('title')}")
    print(f"Text preview: {point.payload.get('text', '')[:100]}...")
    print("-" * 80)