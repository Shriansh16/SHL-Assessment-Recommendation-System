# SHL Assessment Recommender System

## Overview

This AI-powered solution helps hiring managers quickly find the most relevant SHL assessments for their open positions. By analyzing job descriptions or natural language queries, the system automatically recommends suitable assessments.

## Technical Approach

### Hybrid Search in RAG Applications

Hybrid search is a powerful technique commonly used in Retrieval-Augmented Generation (RAG) applications to find relevant information from large collections of documents. This approach combines multiple search methodologies:

1. **Semantic Search** (Dense Retrieval):
   - Uses vector embeddings to understand meaning and context
   - Powered by OpenAI's embedding model in this implementation
   - Effective for conceptual similarity matching

2. **Syntactic Search** (Sparse Retrieval):
   - Uses traditional keyword-based matching (BM25 algorithm)
   - Effective for exact term matching and phrase searches
   - Maintains the benefits of lexical search

**Why Hybrid Search?**
- Combines strengths of both semantic and syntactic approaches
- Provides more comprehensive results than either method alone
- Better handles queries with both specific terms and conceptual meaning
- Reduces limitations of pure semantic search (e.g., missing exact matches)
- Mitigates vocabulary mismatch problem of pure keyword search

## Components

### 1. `data_extractor.py`

Scrapes the SHL product catalog website and extracts product information.

**Features:**
- Crawls through paginated product listings
- Extracts all product page links
- Visits each product page and saves content to a text file
- Handles errors and missing content gracefully
- Outputs structured text file with product titles, URLs, and content

### 2. creating_database.py

Processes extracted data and creates a hybrid search index using Pinecone.

**Features:**
- Creates Pinecone index with hybrid search capabilities
- Combines dense embeddings (OpenAI) with sparse BM25 encoding
- Indexes document chunks for efficient retrieval

### 3. app.py

Streamlit application providing the user interface.

**Features:**
- Chat-like interface
- Hybrid search functionality
- Conversation memory
- Powered by Groq's Llama 3 70B model
- Tabular output of recommendations

**Requirements:**
- Groq API key
- OpenAI API key
- Pinecone API key

**Output Format:**
- Recommendations include:
1. Assessment Name (hyperlinked)
2. Remote Testing Support
3. Adaptive/IRT Support
4. Duration
5. Test Type

