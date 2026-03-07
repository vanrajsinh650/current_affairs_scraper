import requests

def upload_url_to_imagebb(image_rul):
    print("Uploading image in imageBB...")

    IMGBB_API_KEY = "YOUR_IMGBB_API_KEY"

    payload = {
        "key": IMGBB_API_KEY,
        "image": image_rul
    }

    try:
        response = requests.post("https://api.imgbb.com/1/upload", data=payload)
        response.raise_for_status()

        final_url = response.json()["data"]["url"]
        print(f"Success! ImageBB hosted at: {final_url}")
        return final_url
    
    except requests.exceptions.RequestException as e:
        print(f"Error uploading imageBB: {e}")
        return None