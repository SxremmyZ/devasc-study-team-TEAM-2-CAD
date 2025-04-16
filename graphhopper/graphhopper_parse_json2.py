import requests
import urllib.parse
# here i am loading my API key from env even if tutorial doesn't mention
# because harcoding it and pushing to Git is stupid
import os
from dotenv import load_dotenv


geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?" 
loc1 = "Washington, D.C."
loc2 = "Baltimore, Maryland"

load_dotenv()
key = os.getenv('GRAPHHOPPER_KEY')

url = geocode_url + urllib.parse.urlencode({"q":loc1, "limit": "1", "key":key})

reply_data = requests.get(url)
json_data = reply_data.json()
json_status = reply_data.status_code
print(json_data)