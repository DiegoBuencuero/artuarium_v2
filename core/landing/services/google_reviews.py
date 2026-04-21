import requests

# DIRECTO — sin settings
API_KEY = "AIzaSyApMDI1m24ACr1rcfOny7lwWme-SL5I35E"
PLACE_ID = "ChIJ5T6tCGcmJ5URWEuek8w8WAM"   # el de Innobrar

def get_google_reviews():
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={PLACE_ID}&key={API_KEY}&fields=reviews"
    )

    print("📌 URL:", url)
    response = requests.get(url)
    print("📌 STATUS:", response.status_code)
    print("📌 RAW:", response.text)

    return response.json()
