# 🇪🇺 RAG News Chatbot: European Commission News Analyzer

This repository contains a Retrieval-Augmented Generation (RAG) system designed to answer questions based on recent news releases from the official European Commission website (`https://commission.europa.eu/news/`).

The primary goal of this project is to implement and conduct a **comparative benchmark** of different Large Language Models (LLMs) and Embedding Models to analyze their impact on RAG performance, latency, and factual accuracy, fulfilling the "plus" requirement of the Text Mining course project.

## 📁 Project Structure

The repository is organized into three core components:

| File                           | Purpose                                                                                                                                                               |
| :----------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data_crawler.py`              | **Data Preparation:** Python script responsible for scraping news from the source URL and performing initial cleaning.                                                |
| `eu_commission_news.csv`       | **Source Data:** The raw dataset containing the crawled news articles (input for the RAG pipeline).                                                                   |
| `news_chatbot_benchmark.ipynb` | **Main Execution:** Jupyter Notebook where the RAG pipeline is built, models are dynamically loaded, comparative tests are run, and evaluation metrics are generated. |

---

## 🎯 Benchmark Objectives

The project's key focus is exploring the performance trade-offs across four different model combinations by changing the components in the RAG architecture:

### 1. LLM Performance (The Generator)

We compare two state-of-the-art open-source Instruction-Tuned LLMs. Both models are loaded using **4-bit quantization (QLoRA)** via Hugging Face to ensure they fit efficiently on a GPU (e.g., Kaggle T4 or Colab GPU).

| Model                        | Parameter Size | Primary Comparison Point                                   |
| :--------------------------- | :------------- | :--------------------------------------------------------- |
| **Llama 3.1 8B Instruct**    | 8 Billion      | High **accuracy** and **reasoning** capabilities.          |
| **Mistral-7B-Instruct-v0.2** | 7 Billion      | Superior **inference speed** and **throughput** (latency). |

### 2. Embedding Model Performance (The Retriever)

We compare two efficient Sentence Transformer models to measure their impact on document retrieval quality (semantic match).

| Embedding Model  | ID (Hugging Face)                        | Primary Comparison Point                                      |
| :--------------- | :--------------------------------------- | :------------------------------------------------------------ |
| **E5-Small-v2**  | `intfloat/e5-small-v2`                   | High **semantic relevance** and overall balanced performance. |
| **MiniLM-L6-v2** | `sentence-transformers/all-MiniLM-L6-v2` | Extremely **fast** vector generation and retrieval times.     |

---

## 📊 Evaluation Metrics (The Three Pillars of RAG)

The notebook includes an Automated Evaluation Loop that measures the three core pillars of RAG quality, plus efficiency:

| Metric                                     | RAG Component Measured                                                                         | Ideal Result                                                                                             |
| :----------------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| **1. Relevance** (`sim_q_a`)               | **Answer Quality:** Semantic match between the **Query** and the **Answer**.                   | Should be **High** (The LLM directly addresses the user's question).                                     |
| **2. Faithfulness** (`sim_c_a`)            | **Grounding:** Semantic match between the **Retrieved Context** and the **Answer**.            | Should be **High** (The answer is solely derived from the provided documents, minimizing hallucination). |
| **3. Recall Proxy** (`completeness_score`) | **Retrieval Completeness:** Ratio of retrieved chunks to maximum requested chunks (e.g., 5/5). | Should be **High** (Ensures the Retriever is actively providing sufficient evidence).                    |
| **Response Time**                          | **Efficiency:** Time elapsed between query submission and final answer (Latency).              | Should be **Low** (Faster inference is better for user experience).                                      |

The results of these benchmarks will form the basis of the final project presentation slides, detailing the performance trade-offs between the 4 model combinations.
