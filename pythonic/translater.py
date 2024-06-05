import requests

def translate_arabic_to_english(api_key, arabic_text):
    endpoint = "https://api.openai.com/v1/engines/davinci/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": arabic_text,
        "max_tokens": 100,
        "temperature": 0,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    else:
        return None

# استبدل 'YOUR_API_KEY' بمفتاح API الخاص بك
api_key = "sk-proj-zFIthCMUBQeYi2TLRL1GT3BlbkFJ40GSFwi7ITEkQdcAdjf6"
arabic_text = "اهلاً وسهلاً"

english_text = translate_arabic_to_english(api_key, arabic_text)
print("Translated text:", english_text)