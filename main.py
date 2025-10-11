import requests
from bs4 import BeautifulSoup

# Define the base URL
base_url = "https://commission.europa.eu/news-and-media/news_en?"

# Define the parameters
params = {
    "f[0]": "oe_news_publication_date:bt|2025-09-18T19:48:17+02:00|2025-10-18T19:48:17+02:00",
    "page": "0"
}

# Define the headers
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

# Make the GET request
response = requests.get(base_url, params=params, headers=headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the total number of news articles with error handling
total_news_tag = soup.find('div', class_='ecl-u-border-bottom ecl-u-border-width-2 ecl-u-d-flex ecl-u-justify-content-between ecl-u-align-items-end')
print(total_news_tag)