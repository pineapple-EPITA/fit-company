import requests
import os
from dotenv import load_dotenv

load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASS = os.getenv("USER_PASS")


# get token by logging in with user credentials
def get_token():
    """
    Get the API token for the user.
    """
    url = f"http://localhost:12101/oauth/token"
    response = requests.post(url, json={"email": USER_EMAIL, "password": USER_PASS})
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise RuntimeError(f"Failed to get token: {response.status_code} - {response.text}")
    
    
# call the create WOD endpoint for all users with token
def call_create_wod_for_all_users(token):
    url = f"http://localhost:12101/users/wod_for_all"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("WOD created for all users successfully.")
    else:
        print(f"Failed to create WOD: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        token = get_token()
        call_create_wod_for_all_users(token)
    except Exception as e:
        print(f"Error: {e}")
