# 100% private Agentic RAG API

This is a simple API that uses CrewAI and LitServe to create a 100% private Agentic RAG API.

## How to use

1. Clone the repo
2. Install the dependencies:

```bash
pip install crewai crewai-tools litserve
```

Download Ollama and run the following command to download the Qwen3 model:

```bash
ollama pull qwen3
```

3. Run the server:

```bash
python server.py
```

4. Run the client:

```bash
python client.py --query "What is the Qwen3?"
```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.


This project sets up a private agentic RAG (Retrieval-Augmented Generation) API using CrewAI, LitServe, and Ollama with the Qwen3 model.

  Based on this, here are a few different things we could implement or explore:

   1. Use a Different LLM: Instead of qwen3, we could configure it to use another model available through Ollama, like llama3 or mistral. This
      would let us compare the performance and output of different models for the same task.

   2. Containerize with Docker: We could create a Dockerfile and a docker-compose.yml to containerize the application. This would make it easier to
       manage dependencies (like Ollama) and run the entire stack with a single command.

   3. Add a Simple Web Interface: Instead of interacting with it via a command-line client, we could build a simple web interface using a framework
       like Flask or FastAPI. This would allow users to input their queries in a web browser.

   4. Expand the CrewAI Agents: The current implementation is likely a simple one. We could define more specialized agents and a more complex
      workflow in server.py to handle more sophisticated queries or tasks.
      why we need ollama ?  │
╰──────────────────────────╯

✦ That's an excellent question. Here’s the reasoning:

  1. The "Brain" of the Operation

  The AI agents defined in server.py (the "Researcher" and the "Writer") are essentially task managers. They can be given goals and tools, but
  they need a Large Language Model (LLM) to actually think, reason, understand language, and generate text. The LLM is the "brain" that powers
  the agents.

  2. The "100% Private" Requirement

  We could use a cloud-based LLM from a service like OpenAI (GPT-4) or Google (Gemini). However, this would involve sending your data over the
  internet to a third-party company.

  The goal of this project is to create a "100% private" API. This means all data and processing should happen directly on your own machine,
  ensuring nothing is sent to external servers.

  3. Ollama's Role: Your Personal AI Server

  This is where Ollama comes in. Ollama is a free and easy-to-use tool that allows you to download and run powerful, open-source LLMs (like
  qwen, llama3, etc.) directly on your computer.

  In simple terms, Ollama turns your machine into its own self-contained AI server.

  So, when our Python script runs, it doesn't call an external API. Instead, it communicates with the Ollama service running locally on your
  machine to get the "brainpower" it needs from the qwen model. This keeps everything local, private, and free.
