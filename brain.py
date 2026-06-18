import requests
import config
import json

history = []

# ── Local commands — AI ki zaroorat nahi ──────────────────
LOCAL_COMMANDS = {
    "open desktop": {"action": "open_folder", "params": {"path": "desktop"}, "response": "Desktop khol raha hoon!"},
    "open downloads": {"action": "open_folder", "params": {"path": "downloads"}, "response": "Downloads khol raha hoon!"},
    "open documents": {"action": "open_folder", "params": {"path": "documents"}, "response": "Documents khol raha hoon!"},
    "open pictures": {"action": "open_folder", "params": {"path": "pictures"}, "response": "Pictures khol raha hoon!"},
    "take screenshot": {"action": "take_screenshot", "params": {}, "response": "Screenshot le raha hoon!"},
    "screenshot": {"action": "take_screenshot", "params": {}, "response": "Screenshot le raha hoon!"},
    "open camera": {"action": "open_camera", "params": {}, "response": "Camera khol raha hoon!"},
    "camera": {"action": "open_camera", "params": {}, "response": "Camera khol raha hoon!"},
    "volume up": {"action": "volume_up", "params": {}, "response": "Volume badha raha hoon!"},
    "volume down": {"action": "volume_down", "params": {}, "response": "Volume kam kar raha hoon!"},
    "mute": {"action": "mute", "params": {}, "response": "Mute kar raha hoon!"},
    "open chrome": {"action": "open_app", "params": {"app_name": "chrome"}, "response": "Chrome khol raha hoon!"},
    "open notepad": {"action": "open_app", "params": {"app_name": "notepad"}, "response": "Notepad khol raha hoon!"},
    "open calculator": {"action": "open_app", "params": {"app_name": "calc"}, "response": "Calculator khol raha hoon!"},
    "open vs code": {"action": "open_app", "params": {"app_name": "code"}, "response": "VS Code khol raha hoon!"},
    "open vscode": {"action": "open_app", "params": {"app_name": "code"}, "response": "VS Code khol raha hoon!"},
    "open explorer": {"action": "open_app", "params": {"app_name": "explorer"}, "response": "File Explorer khol raha hoon!"},
    "open paint": {"action": "open_app", "params": {"app_name": "mspaint"}, "response": "Paint khol raha hoon!"},
    "open task manager": {"action": "open_app", "params": {"app_name": "taskmgr"}, "response": "Task Manager khol raha hoon!"},
}

SYSTEM_PROMPT = """
You are Jarvis, an AI desktop voice assistant for Windows.
User will give you voice commands in English or Hinglish.

Your job is to return ONLY a JSON response like this:
{
  "action": "open_folder",
  "params": {"path": "Desktop"},
  "response": "Opening Desktop folder for you!"
}

Available actions:
- open_folder: params = {path}
- create_file: params = {path, filename}
- delete_file: params = {path}
- open_app: params = {app_name}
- search_web: params = {query}
- take_screenshot: params = {}
- volume_up: params = {}
- volume_down: params = {}
- mute: params = {}
- type_text: params = {text}
- open_camera: params = {}
- unknown: params = {}

Rules:
- ONLY return JSON, nothing else
- response field mein friendly reply likho
- Hinglish commands bhi samjho
"""

def think(user_input):
    text = user_input.lower().strip()

    # ── Local match pehle check karo ──
    for key, value in LOCAL_COMMANDS.items():
        if key in text:
            return value

    # ── Search command ──
    if text.startswith("search "):
        query = text.replace("search ", "")
        return {"action": "search_web", "params": {"query": query}, "response": f"Searching {query}!"}

    # ── AI fallback ──
    try:
        history.append(f"User: {user_input}")
        full_prompt = SYSTEM_PROMPT + "\n\nConversation so far:\n"
        full_prompt += "\n".join(history[-6:])
        full_prompt += f"\n\nUser command: {user_input}"

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Jarvis Voice Agent"
            },
            json={
                "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
                "messages": [{"role": "user", "content": full_prompt}]
            },
            timeout=10
        )

        resp_json = response.json()
        if "error" in resp_json:
            return {"action": "unknown", "params": {}, "response": "Samajh nahi aaya, dobara bolo!"}

        raw = resp_json["choices"][0]["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        history.append(f"Assistant: {result.get('response', '')}")
        return result

    except Exception as e:
        return {"action": "unknown", "params": {}, "response": "Samajh nahi aaya, dobara bolo!"}