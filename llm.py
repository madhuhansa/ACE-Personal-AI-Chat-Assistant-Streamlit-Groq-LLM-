import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


X_MODEL = "llama-3.1-8b-instant"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def stream_reply(messages):
    """
    Streams a reply from the LLM given a full message history.
    """
    response = client.chat.completions.create(
        model=X_MODEL,
        messages=messages, # Pass the full history
        stream=True
    )

    full_reply = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            full_reply += delta.content
            yield delta.content

    return full_reply


def generate_chat_title(first_message):
    """
    Generates a short (2-4 word) title for a chat based on the first message.
    """
    try:
        prompt = f"Generate a very short, 2-4 word title for a chat that starts with this user message. Only output the title, nothing else.\n\nMessage: \"{first_message}\"\n\nTitle:"
        
        response = client.chat.completions.create(
            model=X_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            max_tokens=20, # Limit output
            temperature=0.2 # Be deterministic
        )
        
        title = response.choices[0].message.content.strip().strip('"')
        return title if title else "Chat"
    except Exception as e:
        print(f"Error generating title: {e}")
        return "Chat" # Fallback title