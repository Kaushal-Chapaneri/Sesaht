"""
filename : text_to_speech.py

This script holds the code to use Text-to-Speech API of Modzy.

command to run: python text_to_speech.py
"""

from utils import load_config
from modzy import ApiClient, error
import subprocess

config = load_config()
client = ApiClient(base_url= config["API_URL"], api_key= config["API_KEY"])

model = client.models.get_by_name("Text to Speech Conversion")

# write text here that needs to be converted to speech.
sources = {"source-key": {"input.txt": "Hello From Modzy."}}

job = client.jobs.submit_text("uvdncymn6q", '0.0.2', sources, explain=False)
job.block_until_complete(timeout=None)

result = job.get_result()
result_url = result.results["source-key"]["results.wav"]

# generating curl request to download audio, TTS API returns the url where audio is stored.
curl = 'curl -H "Authorization: ApiKey '+config["API_KEY"]+'" '+result_url+' --output output.wav'

subprocess.check_output(curl, shell=True)

print("Success...")
