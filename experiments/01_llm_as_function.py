"""
Phase 1 - Module 1 - The LLM as a Function
------------------------------------------
Goal: make our first call to Groq *through LangChain* and understand
exactly what an LLM "invocation" returns. No chains, no agents yet -
just: text in, structured message out.

Run:  python experiments/01_llm_as_function.py
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1) Load key=value pairs from the .env file into the process environment.
#    This does NOT print or expose the key - it just makes os.getenv() see it.
load_dotenv()

# 2) Fail fast with a helpful message if config is missing.
if not os.getenv("GROQ_API_KEY"):
    raise SystemExit(
        "GROQ_API_KEY is not set. Copy .env.example to .env and paste your key."
    )

# 3) Read config from the environment. Secrets are NEVER hardcoded in source.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# 4) Build the model client.
#    - temperature=0  -> as deterministic as possible (we want consistent triage)
#    - the api key is auto-read from the GROQ_API_KEY env var by langchain-groq
model = ChatGroq(model=GROQ_MODEL, temperature=0)

# 5) A sample support ticket (we'll automate ticket intake in later modules).
ticket = "Hi, I was charged twice for my subscription this month. Please help!"

# 6) Invoke the model. .invoke() is the universal LangChain "call" method -
#    every model, chain, and agent we build will expose this SAME method.
response = model.invoke(
    f"In one sentence, summarize what this support ticket is about:\n\n{ticket}"
)

# 7) Inspect the response. It is NOT a plain string - it's an AIMessage object.
print("RETURN TYPE :", type(response).__name__)
print("CONTENT     :", response.content)
print("TOKENS USED :", response.usage_metadata)
print("MODEL META  :", response.response_metadata.get("model_name"))
