import requests
import urllib.parse

def generate_and_host_thumbnail(quiz_title):
    prompt = f"Professional news thumbnail for daily current affairs, clean modern flat design. Topic: {quiz_title}"

    encoded_prompt = urllib.parse.quote(prompt)

    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    