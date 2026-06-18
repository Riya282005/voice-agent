import os
import subprocess
import pyautogui
import webbrowser
from datetime import datetime

def execute(action, params):

    if action == "open_folder":
        path = params.get("path", "")
        shortcuts = {
            "desktop": os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "documents": os.path.join(os.path.expanduser("~"), "OneDrive", "Documents"),
            "pictures": os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures"),
            "music": os.path.join(os.path.expanduser("~"), "OneDrive", "Music"),
        }
        folder = shortcuts.get(path.lower(), path)
        os.startfile(folder)
        return True

    elif action == "open_camera":
        os.system("explorer.exe shell:AppsFolder\\Microsoft.WindowsCamera_8wekyb3d8bbwe!App")
        return True

    elif action == "close_camera":
        os.system("taskkill /f /im WindowsCamera.exe")
        return True

    elif action == "open_app":
        app = params.get("app_name", "").lower()
        apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "code": "code.exe",
            "vscode": "code.exe",
            "mspaint": "mspaint.exe",
            "explorer": "explorer.exe",
            "taskmgr": "taskmgr.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
        }
        cmd = apps.get(app, app)
        try:
            subprocess.Popen(cmd, shell=True)
        except:
            os.system(f"start {cmd}")
        return True

    elif action == "search_web":
        query = params.get("query", "")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return True

    elif action == "take_screenshot":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        print(f"Screenshot saved: {path}")
        return True

    elif action == "volume_up":
        for _ in range(5):
            pyautogui.press("volumeup")
        return True

    elif action == "volume_down":
        for _ in range(5):
            pyautogui.press("volumedown")
        return True

    elif action == "mute":
        pyautogui.press("volumemute")
        return True

    elif action == "type_text":
        import pyperclip
        text = params.get("text", "")
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        return True

    else:
        return False