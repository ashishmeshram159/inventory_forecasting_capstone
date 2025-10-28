from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
import os

# Load API Keys
load_dotenv()
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]

# Initialize Groq + Embedding
llm = Groq(model="llama-3.1-8b-instant")
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")

Settings.llm = llm
Settings.embed_model = embed_model

# Connect to Existing Pinecone Index
index_name = "holiday-ads-llama3-groq"
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(index_name)

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load the existing index (no re-embedding)
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

# Query the RAG System
query_engine = index.as_query_engine(similarity_top_k=5)
# question = "What are the offers available for groceries in October?"
question = "What are the offers available for new year?"
response = query_engine.query(question)

print("\n Query:")
print(question)
print("\n Response:")
print(response)
