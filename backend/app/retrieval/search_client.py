from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
)
from app.config import settings, credential

index_client = SearchIndexClient(endpoint=settings.search_endpoint, credential=credential)
search_client = SearchClient(endpoint=settings.search_endpoint, index_name=settings.search_index, credential=credential)

from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile, VectorSearchAlgorithmKind,
)

def ensure_index():
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="page", type=SearchFieldDataType.Int32, filterable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="default-vector-profile",
        ),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
        profiles=[VectorSearchProfile(name="default-vector-profile", algorithm_configuration_name="default-hnsw")],
    )
    index = SearchIndex(name=settings.search_index, fields=fields, vector_search=vector_search)
    index_client.create_or_update_index(index)

def upload_chunks(docs: list[dict]):
    search_client.upload_documents(documents=docs)

def hybrid_search(query: str, query_vector: list[float], top: int = 5):
    from azure.search.documents.models import VectorizedQuery
    vq = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top, fields="content_vector")
    results = search_client.search(search_text=query, vector_queries=[vq], top=top)
    return [{"content": r["content"], "page": r.get("page"), "score": r["@search.score"]} for r in results]