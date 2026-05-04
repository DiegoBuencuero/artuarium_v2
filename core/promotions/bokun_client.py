import base64
import datetime
import hashlib
import hmac

import requests
from django.conf import settings

BASE_URL = "https://api.bokun.io"


def _headers(method: str, path: str) -> dict:
    date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
    # Formato oficial Bókun: date + accessKey + METHOD + path (sin separadores)
    msg = f"{date}{settings.BOKUN_API_KEY}{method.upper()}{path}"
    sig = base64.b64encode(
        hmac.new(settings.BOKUN_SECRET.encode(), msg.encode(), hashlib.sha1).digest()
    ).decode()
    return {
        "X-Bokun-Date": date,
        "X-Bokun-AccessKey": settings.BOKUN_API_KEY,
        "X-Bokun-Signature": sig,
        "Content-Type": "application/json;charset=UTF-8",
    }


def get_activities() -> list:
    path = "/activity.json/search"
    r = requests.post(
        BASE_URL + path,
        headers=_headers("POST", path),
        json={},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data
    return data.get("items", data.get("results", []))


def get_activity(bokun_id: int) -> dict:
    path = f"/activity.json/{bokun_id}"
    r = requests.get(BASE_URL + path, headers=_headers("GET", path), timeout=15)
    r.raise_for_status()
    return r.json()
