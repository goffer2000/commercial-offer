import os
import requests
from datetime import datetime, timedelta

# Конфигурация из переменных среды
APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

# Кэшируем access_token в памяти (для 1 запуска)
access_token = None
access_token_expiry = None

def get_access_token():
    global access_token, access_token_expiry
    if access_token and access_token_expiry and datetime.utcnow() < access_token_expiry:
        return access_token

    print("🔄 Получаем новый access_token...")
    response = requests.post("https://api.dropboxapi.com/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }, auth=(APP_KEY, APP_SECRET))

    if not response.ok:
        raise Exception(f"Dropbox token refresh failed: {response.text}")

    data = response.json()
    access_token = data["access_token"]
    access_token_expiry = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 14400) - 60)
    return access_token

def upload_to_dropbox(file_path, dropbox_path):
    token = get_access_token()

    with open(file_path, "rb") as f:
        content = f.read()

    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Dropbox-API-Arg": str({
            "path": dropbox_path,
            "mode": "add",
            "autorename": True,
            "mute": False
        }).replace("'", '"'),
        "Content-Type": "application/octet-stream"
    }

    response = requests.post(url, headers=headers, data=content)
    if response.status_code != 200:
        raise Exception(f"Dropbox upload failed: {response.text}")

    print(f"✅ Успешно загружен в Dropbox: {dropbox_path}")
    return True
