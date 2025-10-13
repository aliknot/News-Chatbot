import requests
from bs4 import BeautifulSoup

# Define the base URL
base_url = "https://commission.europa.eu/news-and-media/news_en?"

# Define the parameters for the first page
params = {
    "f[0]": "oe_news_publication_date:bt|2025-09-11T19:48:17+02:00|2025-10-11T19:48:17+02:00",
    "page": "0"
}

# Define the headers
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

# Make the GET request
response = requests.get(base_url, params=params, headers=headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the parent div first
news_count_wrapper = soup.find('div', class_='ecl-u-border-bottom ecl-u-border-width-2 ecl-u-d-flex ecl-u-justify-content-between ecl-u-align-items-end')

# Now, search for the h4 and spans within that parent div
if news_count_wrapper:
    h4_tag = news_count_wrapper.find('h4', class_='ecl-u-type-heading-4 ecl-u-mb-s')
    
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
    
# Find all the news article containers
article_containers = soup.find_all('div', class_='ecl-content-item-block__item')

# Filter the containers to include only those without 'ecl-col-l-6' in their class list
filtered_containers = [
    container for container in article_containers 
    if 'ecl-col-l-6' not in container.get('class', [])
]

# Define the output file name
output_file = 'eu_commission_news.txt'

# Open the file in write mode
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("--- News Articles from European Commission ---\n\n")

    # Loop through the filtered containers to extract the articles
    for i, container in enumerate(filtered_containers, 1):
        article = container.find('article', class_='ecl-content-item')
        if article:
            # Extract the title and link
            title_tag = article.find('div', class_='ecl-content-block__title').find('a')
            title = title_tag.text.strip()
            link = title_tag['href']

            # Extract the publication date
            date_tag = article.find('time')
            date = date_tag.text.strip() if date_tag else "No date available."

            # Extract the description
            description_tag = article.find('div', class_='ecl-content-block__description')
            description = description_tag.text.strip() if description_tag else "No description available."
            
            # Write the extracted information to the file
            f.write(f"Article {i}:\n")
            f.write(f"Title: {title}\n")
            f.write(f"Link: {link}\n")
            f.write(f"Date: {date}\n")
            f.write(f"Description: {description}\n")
            f.write("-" * 30 + "\n\n")

print(f"Successfully scraped {len(filtered_containers)} news articles and saved them to {output_file}.")