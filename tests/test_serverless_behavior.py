import httpx
import subprocess
import time

BASE_URL = "http://localhost:8000"
USERNAME = "persist_user"
PASSWORD = "StrongPassword123"
EMAIL = "persist@example.com"

def signup():
    r = httpx.post(f"{BASE_URL}/auth/signup", json={
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    })
    if r.status_code == 200:
        print("✅ Signup OK")
    elif r.status_code == 400:
        print("⚠️ User already exists")
    else:
        print("❌ Signup failed:", r.text)

def login():
    r = httpx.post(f"{BASE_URL}/auth/login", data={
        "username": USERNAME,
        "password": PASSWORD
    })
    if r.status_code == 200:
        print("✅ Login OK")
        return r.json()["access_token"]
    print("❌ Login failed:", r.text)
    return None

def generate_api_key(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = httpx.post(f"{BASE_URL}/apikeys", json={"expires_in_seconds": 300}, headers=headers)
    if res.status_code == 200:
        key = res.json()["key"]
        print("✅ API key created:", key)
        return key
    else:
        print("❌ API key failed:", res.text)
        return None

def run_power_test(key_to_test):
    r = httpx.get(f"{BASE_URL}/api/v1/power", params={"base": 2, "exponent": 3}, headers={"X-API-Key": key_to_test})
    if r.status_code == 200:
        print("✅ Power OK:", r.json())
    else:
        print("❌ Power failed:", r.text)

def get_current_user_info(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = httpx.get(f"{BASE_URL}/users/me", headers=headers)
    if r.status_code == 200:
        user = r.json()
        print("👤 Current user after restart:", user)
        return user
    else:
        print("❌ Failed to get current user:", r.text)
        return None

def restart_container():
    print("🔄 Restarting container (simulated serverless cold start)...")
    subprocess.run(["docker", "compose", "-f", "docker-compose.serverless.yml", "stop", "api-serverless"])
    time.sleep(2)
    subprocess.run(["docker", "compose", "-f", "docker-compose.serverless.yml", "start", "api-serverless"])
    time.sleep(5)

if __name__ == "__main__":
    signup()
    session_token = login()

    if session_token:
        api_key_value = generate_api_key(session_token)
        if api_key_value:
            run_power_test(api_key_value)

            restart_container()

            session_token = login()
            if session_token:
                get_current_user_info(session_token)
                api_key_value = generate_api_key(session_token)
                if api_key_value:
                    run_power_test(api_key_value)
