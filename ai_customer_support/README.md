# AI Customer Support Assistant

A Streamlit chat app that uses LangChain with either a local Ollama model or an OpenRouter chat model. Conversation history is retained for follow-up questions for the current browser session.

## Setup

From this directory, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For **Ollama**, install Ollama, start its service, and download a model, for example:

```bash
ollama pull llama3.2
```

For **OpenRouter**, copy `.env.example` to `.env` and set `OPENROUTER_API_KEY` to a key from your OpenRouter account. Do not commit `.env`.

Run the app:

```bash
streamlit run app.py
```

Choose the provider and model in the sidebar. You can also adjust the provider URLs and default models in `.env`.

## Try these questions

- My order is two days late. What should I do?
- The item arrived damaged. How can I resolve this?
- Can I return an item I bought last month?
- How long does a refund usually take?
- Follow up: What information should I include when contacting support?

The assistant does not have access to orders or store policies and cannot perform account actions. Confirm eligibility, timelines, and actual refunds with the store. Evaluate answers for relevance, accuracy against your store's policies, and consistency across follow-up questions before using this with customers.