"""Central config. Loaded once, imported everywhere (no more repeating this)."""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not os.getenv("GROQ_API_KEY"):
    raise SystemExit("GROQ_API_KEY not set. Copy .env.example to .env and add your key.")
