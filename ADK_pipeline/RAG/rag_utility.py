
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
import os


#   Load API keys
load_dotenv()
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]

#   Initialize Groq + Embedding
llm = Groq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")

Settings.llm = llm
Settings.embed_model = embed_model

#   Connect to Pinecone
index_name = "holiday-ads-llama3-groq"
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

#   Load existing index
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

# -------------------------------------------------------
# FUNCTION TOOL: RAG Query Engine
# -------------------------------------------------------
def query_promotional_offers(query: str, top_k: int = 5):
    """
    Retrieves relevant promotional offers using the RAG index.
    - query: natural language question (e.g., "offers available for groceries in October")
    - top_k: number of top matches to retrieve
    """
    try:
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)
        return {
            "query": query,
            "response": str(response),
            "top_k": top_k
        }
    except Exception as e:
        return {"error": str(e)}




# def retrieve_offers(keywords: str):
#     """
#     RAG Tool: Retrieves relevant promotional offers based on keywords.
#     - Searches the loaded offers for matches (case-insensitive).
#     - Returns a list of matching offers or a message if none found.
#     - Keywords can be a comma-separated string (e.g., "winter, sale").
#     """
#     try:
#         keyword_list = [kw.strip().lower() for kw in keywords.split(',')]
#         matching_offers = [
#             offer for offer in promotional_offers
#             if any(kw in offer.lower() for kw in keyword_list)
#         ]
#         if matching_offers:
#             return matching_offers
#         else:
#             return ["No relevant offers found for the given keywords."]
#     except Exception as e:
#         print(f"Error retrieving offers for keywords '{keywords}': {e}")
#         return ["Error retrieving offers."]