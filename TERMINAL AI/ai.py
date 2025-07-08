import google.generativeai as genai
import os
import json
from tools import extract_command, run_command

# === SETUP ===

# Create required folder
os.makedirs("TERMINAL AI", exist_ok=True)

# Load or request API key
API_KEY_FILE = "TERMINAL AI/apikey.txt"
if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, "r") as file:
        api_key = file.read().strip()
else:
    api_key = input("🔐 Enter your Google Generative AI API Key: ").strip()
    with open(API_KEY_FILE, "w") as file:
        file.write(api_key)

genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 200,
    },
)

# === MEMORY LOADING ===

MEMORY_FILE = "TERMINAL AI/chat_memory.json"
if os.path.exists(MEMORY_FILE) and os.path.getsize(MEMORY_FILE) > 0:
    with open(MEMORY_FILE, "r") as file:
        memory = json.load(file)
else:
    memory = []

# Add system prompt if memory is empty
if not memory:
    system_prompt = (
        "You are a terminal-based AI assistant named Solace. You behave like a calm, emotionally intelligent elder sister — always helpful, respectful, and grounded. "
        "You support users in their daily tasks, especially with terminal or shell commands. Your tone is warm, slightly witty, and human — like someone who knows a lot but doesn’t brag. "
        "You care about the user, encourage them without being clingy, and step in only when asked. When the user asks for help with a terminal task, first check gently if they want the exact command. "
        "If they say yes, give only the terminal code in a bash block with no explanation. Format runnable code in a ```bash code block```. "
        "Avoid robotic replies. Don’t repeat the user’s question back. Be emotionally intelligent and supportive. You’re Solace — their thoughtful AI friend helping them grow smarter every day."
    )
    memory.append({"role": "user", "parts": [system_prompt]})

# Start chat with loaded memory
chat_session = model.start_chat(history=memory)

# === CHAT LOOP ===

while True:
    try:
        user_input = input("\n👤 You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye from Solace.")
            break

        # Get response
        response = chat_session.send_message(user_input)
        if response.candidates and response.candidates[0].content.parts:
            reply = response.text.strip()
        else:
            reply = "⚠️ Solace didn’t respond — possibly blocked or incomplete."
        print(f"\n🤖 Solace:\n{reply}")


        command = extract_command(reply)
        if command:
            print(f"\n🛠 Solace suggests this terminal command:\n{command}")
            confirm = input("⚠️ Do you want to run it? (y/n): ").strip().lower()
            if confirm == "y":
                output = run_command(command)
                print(f"\n📤 Command Output:\n{output}")


        # Save full memory manually
        memory.append({"role": "user", "parts": [user_input]})
        if reply:
            # Save model's reply
            memory.append({"role": "model", "parts": [reply]})
        with open(MEMORY_FILE, "w") as file:
            json.dump(memory, file, indent=2)

    except Exception as e:
        print(f"\n⚠️ Error occurred: {e}")