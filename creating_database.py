
import os
import pickle
import nltk

from pinecone import Pinecone, ServerlessSpec
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.retrievers import PineconeHybridSearchRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from pinecone_text.sparse import BM25Encoder
nltk.download('punkt')

api_key = st.secrets["PINECONE_API_KEY"]
index_name = "shll-database"

pc = Pinecone(api_key=api_key)

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="dotproduct",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(index_name)
embedding = OpenAIEmbeddings(api_key=st.secrets["OPENAI_API_KEY"])
bm25_encoder = BM25Encoder()

loader = DirectoryLoader('content', glob='*.txt', loader_cls=TextLoader)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
splits = text_splitter.split_documents(documents)

# Fit BM25 encoder on corpus
corpus = [doc.page_content for doc in splits]
bm25_encoder.fit(corpus)

# Save BM25 encoder to file
with open('bm25_encoder.pkl', 'wb') as f:
    pickle.dump(bm25_encoder, f)

retriever = PineconeHybridSearchRetriever(
    embeddings=embedding,
    sparse_encoder=bm25_encoder,
    index=index
)

texts = [doc.page_content for doc in splits]
retriever.add_texts(texts)
print(retriever.invoke("Account Manager Solution"))
