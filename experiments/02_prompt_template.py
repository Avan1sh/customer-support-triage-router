"""
Phase 1 - Module 2 - PromptTemplate
-----------------------------------
Goal: stop hand-building prompt strings with f-strings. Separate the
prompt (a reusable, named-variable template) from the code that runs it.

Run:  python experiments/02_prompt_template.py
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
model = ChatGroq(model=GROQ_MODEL, temperature=0)

# 1) Define the prompt ONCE, as a reusable template.
#    - "system" message = the model's standing role / rules
#    - "human"  message = the actual input, with a {ticket} placeholder
classifier_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a customer-support triage assistant. "
            "Classify the ticket into EXACTLY ONE category from this list: "
            "Billing, Technical, Account, Feature Request, Complaint. "
            "Reply with ONLY the category word - nothing else.",
        ),
        ("human", "Ticket:\n{ticket}"),
    ]
)

# 2) Fill the template. This returns a PromptValue (structured messages),
#    NOT a plain string.
ticket = "Hi, I was charged twice for my subscription this month. Please help!"
prompt_value = classifier_prompt.invoke({"ticket": ticket})

print("MESSAGES SENT TO THE MODEL:")
for m in prompt_value.to_messages():
    print(f"  [{m.type:6}] {m.content}")

# 3) Manually feed the prompt into the model.
#    NOTE: we are wiring step1 -> step2 BY HAND. Remember this friction -
#    Phase 2 (LCEL) collapses it into:   chain = classifier_prompt | model
response = model.invoke(prompt_value)

print("\nCATEGORY:", response.content)
print("TOKENS  :", response.usage_metadata)
