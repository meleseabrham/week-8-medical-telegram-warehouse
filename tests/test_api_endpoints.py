import requests
import sys

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("--- Testing API Endpoints ---")

    # Test 1: Top Products
    try:
        r = requests.get(f"{base_url}/api/reports/top-products?limit=5")
        print(f"\n[GET] /api/reports/top-products : {r.status_code}")
        if r.status_code == 200:
            print(r.json())
    except Exception as e:
        print(f"Top Products Failed: {e}")

    # Test 2: Channel Activity (using 'yenehealth' as known channel)
    try:
        r = requests.get(f"{base_url}/api/channels/yenehealth/activity")
        print(f"\n[GET] /api/channels/yenehealth/activity : {r.status_code}")
        if r.status_code == 200:
            print(r.json())
        elif r.status_code == 404:
            print("Channel 'yenehealth' not found, trying 'CheMed123'")
            r = requests.get(f"{base_url}/api/channels/CheMed123/activity")
            print(r.json())
    except Exception as e:
        print(f"Channel Activity Failed: {e}")

    # Test 3: Search
    try:
        r = requests.get(f"{base_url}/api/search/messages?query=price&limit=2")
        print(f"\n[GET] /api/search/messages : {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Found {len(data)} messages.")
            if data:
                print(data[0])
    except Exception as e:
        print(f"Search Failed: {e}")

    # Test 4: Visual Content
    try:
        r = requests.get(f"{base_url}/api/reports/visual-content")
        print(f"\n[GET] /api/reports/visual-content : {r.status_code}")
        if r.status_code == 200:
            print(r.json())
    except Exception as e:
        print(f"Visual Content Failed: {e}")

if __name__ == "__main__":
    test_api()
