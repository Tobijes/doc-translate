import httpx
import typing as t
import json


def translate(text: str):
    url = "http://localhost:5000/translate"
    
    # Set up headers
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Prepare form data
    data = {
        "q": text,
        "source": "da",
        "target": "en",
        "format": "text"
    }
    
    # Make the POST request
    response = httpx.post(url, headers=headers, data=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data["translatedText"]
    else:
        raise Exception(f"Request failed with status code {response.status_code}")