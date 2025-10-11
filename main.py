import requests
import urllib.parse

# Define the base URL
base_url = "https://commission.europa.eu/news-and-media/news_en?"

# Define the parameters
params = {
    "f[0]": "oe_news_publication_date:bt|2025-09-18T19:48:17+02:00|2025-10-18T19:48:17+02:00",
    "page": "0"
}

# URL-encode the query string
encoded_query_string = urllib.parse.urlencode(params)

# Combine the base URL with the encoded query string
url = base_url + encoded_query_string

# Define the headers
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

# Make the GET request
response = requests.get(url, headers=headers)

print(response.content.decode('UTF-8'))

# Write the response content to a file
with open("news.html", "w") as f:
    f.write(response.content.decode('UTF-8'))