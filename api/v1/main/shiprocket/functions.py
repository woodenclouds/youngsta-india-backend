import requests
import json
from django.conf import settings


def login_shiprocket():
    url = "https://apiv2.shiprocket.in/v1/external/auth/login"
    data = {
        "email": settings.SHIPROCKET_EMAIL,
        "password": settings.SHIPROCKET_PASSWORD,
    }
    try:
        json_data = json.dumps(data)
        response = requests.post(
            url, data=json_data, headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            response_data = response.json()
            return response_data

        else:
            return {"error": "Request failed", "status_code": response.status_code}

    except requests.RequestException as e:
        return {"error": str(e), "status_code": 500}
