import os
import streamlit as st
import re

from streamlit_chat import message
from pinecone import Pinecone as PineconeClient
from pinecone_text.sparse import BM25Encoder
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import pickle
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import PineconeHybridSearchRetriever
import nltk
nltk.download('punkt_tab')

bm25_encoder=BM25Encoder()

embedding=OpenAIEmbeddings(api_key=st.secrets["OPENAI_API_KEY"])
def find_match(input_text):
    # Ensure the Pinecone index is correctly initialized
    
    pc = PineconeClient(api_key=st.secrets["PINECONE_API_KEY"])
    
    
    # Ensure the Pinecone index is correctly initialized
    index_name = 'shll-database'
    index = pc.Index(index_name)
    with open('bm25_encoder.pkl', 'rb') as f:
        bm25_encoder = pickle.load(f)
    
    # Initialize Pinecone retriever
    retriever = PineconeHybridSearchRetriever(
        embeddings=embedding,  # Dense embedding model
        sparse_encoder=bm25_encoder,  # Sparse BM25 encoder
        index=index
    )
    
    # Perform hybrid similarity search
    results = retriever.invoke(
        input=input_text
    )
    return results
from langchain_groq import ChatGroq
api_key1=st.secrets["GROQ_API_KEY"]

# Streamlit setup  

st.subheader("SHL Assessment Recommender")

# Initialize session state variables
if 'responses' not in st.session_state:
    st.session_state['responses'] = ["Welcome to the SHL Assessment Recommender! Just drop a job description or a query, and we’ll find the best-fit SHL assessments."]
if 'requests' not in st.session_state:
    st.session_state['requests'] = []

# Initialize the language model
llm=ChatGroq(groq_api_key=api_key1,model_name="llama-3.3-70b-versatile",temperature=0.6)

# Initialize conversation memory
if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory = ConversationBufferWindowMemory(k=1, return_messages=True)

# Define prompt templates
system_msg_template = SystemMessagePromptTemplate.from_template(template="""You are an AI assistant that recommends SHL assessments based on a user's query, job description, or job post URL. You will receive relevant context from the SHL product catalog through retrieval.
Based only on the provided context, return a list of up to 10 relevant SHL individual assessments (minimum 1).
For each recommended assessment, provide the following attributes in a tabular format:

1. Assessment Name (hyperlinked to the SHL catalog URL)
2. Remote Testing Support (Yes/No)
3. Adaptive/IRT Support (Yes/No)
4. Duration
5. Test Type

📌 Strict Guidelines:
1. Do not generate information outside of the provided context.
2. If the context is insufficient to answer, politely ask the user for more details.
3. Do not include the phrase "Based on the provided context".
4. Keep the tone professional and concise.""")                                                                        
human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])
link='logo.png'
# Create conversation chain
conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

# Container for chat history
response_container = st.container()
# Container for text box
text_container = st.container()



with text_container:
    user_query =st.chat_input("Enter your query")

    if user_query:
        with st.spinner("typing..."):
            context = find_match(user_query)
            response = conversation.predict(input=f"Context:\n{context}\n\nQuery:\n{user_query}")
            


        
        # Append the new query and response to the session state  
        st.session_state.requests.append(user_query)
        st.session_state.responses.append(response)
st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"] p{
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True
)


# Display chat history
with response_container:
    if st.session_state['responses']:
        for i in range(len(st.session_state['responses'])):
            with st.chat_message('Momos', avatar=link):
                st.write(st.session_state['responses'][i])
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')