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

# Find the parent div first
parent_div = soup.find('div', class_='ecl-u-border-bottom ecl-u-border-width-2 ecl-u-d-flex ecl-u-justify-content-between ecl-u-align-items-end')

# Now, search for the h4 and spans within that parent div
if parent_div:
    h4_tag = parent_div.find('h4', class_='ecl-u-type-heading-4 ecl-u-mb-s')
    
    if h4_tag:
        # Check if there are any span tags inside the h4
        span_tags = h4_tag.find_all('span')
        if len(span_tags) >= 2:
            total_news_text = span_tags[-1].text.strip()
            total_news_count = int(total_news_text.strip('()'))
            print(f"Total news articles found: {total_news_count}")
        else:
            print("Could not find the total news count span tag inside the h4.")
    else:
        print("Could not find the h4 tag containing the news count inside the div.")
else:
    print("Could not find the parent div element.")