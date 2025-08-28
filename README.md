# 🤖 GenAI RAG Support Bot Framework

[![Python Application CI](https://github.com/Khojee/KnowledgeBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Khojee/KnowledgeBot/actions/workflows/ci.yml)

An intelligent, multilingual Telegram support bot powered by Google's Gemini Pro and a Retrieval-Augmented Generation (RAG) architecture. This project serves as a production-ready framework for building chatbots that can answer questions based on a custom knowledge base.

This framework was developed to solve a real-world business problem at Agrobank, providing instant IT support to employees across 168 branches.

✨ Features

-   **Intelligent RAG Core:** Uses a vector database (ChromaDB) to find relevant information from a private knowledge base before generating answers, ensuring accuracy and preventing hallucination.
-   **Multilingual Support:** Automatically detects the user's language (English, Russian, Uzbek, etc.) and responds in the same language.
-   **Cross-Lingual Search:** Can find answers in an English knowledge base even when the user asks a question in another language.
-   **Production-Ready:** Containerized with Docker for easy and reproducible deployment.
-   **CI/CD Pipeline:** Includes an automated testing pipeline with GitHub Actions to ensure code quality and stability.
-   **Secure by Design:** Securely manages API keys and sensitive data using environment variables and a `.gitignore` file.

🛠️ Tech Stack

-   **AI & Machine Learning:** Google Gemini Pro, Gemini Embedding Models (RAG)
-   **Backend:** Python 3.11
-   **Bot Framework:** `python-telegram-bot`
-   **Vector Database:** ChromaDB
-   **DevOps:** Docker, GitHub Actions
-   **Libraries:** `langdetect`, `pytest`, `python-dotenv`

🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

Prerequisites

-   Python 3.9+
-   Git
-   Docker (Recommended for easiest setup)

1. Local Installation (Without Docker):

    1.  **Clone the repository:**
        ```bash
        git clone https://github.com/YourUsername/YourRepoName.git
        cd YourRepoName
        ```

    2.  **Set up the Knowledge Base:**
        This project uses a private knowledge base. To get started, rename the example folder:
        ```bash
        mv knowledge_base_examples knowledge_base
        ```
        You can now add your own `.txt` files to the `knowledge_base` directory.

    3.  **Configure Environment Variables:**
        Create your own environment file from the example and fill in your secret API keys:
        ```bash
        cp .env.example .env
        # Now, open the .env file and add your keys.
        ```

    4.  **Install Dependencies:**
        ```bash
        pip install -r requirements.txt
        ```

    5.  **Create the Vector Database:**
        Run the embeddings script to process your knowledge base and create the local `chroma_db` database.
        ```bash
        python3 embeddings.py
        ```

    6.  **Run the Bot:**
        ```bash
        python3 main.py
        ```

2. Running with Docker (Recommended)

    1.  **Clone the repository:**
        ```bash
        git clone https://github.com/YourUsername/YourRepoName.git
        cd YourRepoName
        ```

    2.  **Set up the Knowledge Base & Environment:**
        Follow steps 2 and 3 from the "Local Installation" section above to create your `knowledge_base` folder and your `.env` file.

    3.  **Build the Docker Image:**
        ```bash
        docker build -t knowledge-bot .
        ```

    4.  **Run the Docker Container:**
        This command will run the bot in the background and ensure your database persists.
        ```bash
        docker run -d --name my-bot-container --env-file .env -v "$(pwd)/chroma_db":/app/chroma_db knowledge-bot
        ```

    5.  **To view the bot's logs:**
        ```bash
        docker logs my-bot-container
        ```

    6.  **To stop the bot:**
        ```bash
        docker stop my-bot-container
        ```