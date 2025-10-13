import requests
from bs4 import BeautifulSoup
import math
import csv

# Define the base URL and headers
base_url = "https://commission.europa.eu/news-and-media/news_en"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

def get_page_content(page_number, date_range):
    """Fetches the content of a specific page."""
    params = {
        "f[0]": date_range,
        "page": str(page_number)
    }
    response = requests.get(base_url, params=params, headers=headers)
    response.raise_for_status()
    return response.content

def parse_articles_from_soup(soup):
    """Parses news articles from a BeautifulSoup object."""
    articles = []
    # Find all the news article containers
    article_containers = soup.find_all('div', class_='ecl-content-item-block__item')
    
    # Filter the containers to include only those with a valid article
    for container in article_containers:
        # Check if the container has the unwanted class AND if it contains a valid article
        if 'ecl-col-l-6' not in container.get('class', []) and container.find('article', class_='ecl-content-item'):
            articles.append(container.find('article', class_='ecl-content-item'))
    return articles

def extract_article_data(article):
    """Extracts data from a single article tag."""
    title_tag = article.find('div', class_='ecl-content-block__title').find('a')
    title = title_tag.text.strip()
    link = title_tag['href']
    
    date_tag = article.find('time')
    date = date_tag.text.strip() if date_tag else "No date available."
    
    description_tag = article.find('div', class_='ecl-content-block__description')
    description = description_tag.text.strip() if description_tag else "No description available."
    
    return {
        "title": title,
        "link": link,
        "date": date,
        "description": description
    }

# Main script logic
if __name__ == "__main__":
    # Define the fixed date range
    date_range = "oe_news_publication_date:bt|2025-09-11T19:48:17+02:00|2025-10-11T19:48:17+02:00"

    try:
        # Step 1: Find the total number of articles to calculate pages
        print("Fetching first page to determine total news count...")
        first_page_content = get_page_content(0, date_range)
        soup = BeautifulSoup(first_page_content, 'html.parser')

        total_news_tag = soup.find('div', class_='ecl-u-border-bottom ecl-u-border-width-2 ecl-u-d-flex ecl-u-justify-content-between ecl-u-align-items-end').find('h4', class_='ecl-u-type-heading-4 ecl-u-mb-s')
        
        total_news_text = total_news_tag.find_all('span')[-1].text
        total_news_count = int("".join(filter(str.isdigit, total_news_text)))
        pages_to_crawl = math.ceil(total_news_count / 10)
        
        print(f"Total news articles found: {total_news_count}")
        print(f"Total pages to crawl: {pages_to_crawl}")
        print("-" * 30)

        # List to store all articles data
        all_articles_data = []
        
        # Step 2: Loop through all pages to scrape articles
        for page_num in range(pages_to_crawl):
            print(f"Scraping articles from Page {page_num + 1}...")
            page_content = get_page_content(page_num, date_range)
            soup = BeautifulSoup(page_content, 'html.parser')
            
            articles = parse_articles_from_soup(soup)
            
            # Step 3: Extract data and store in list
            for article in articles:
                data = extract_article_data(article)
                data['page'] = page_num + 1 # Add the page number
                all_articles_data.append(data)

        # Define the output file name
        output_file = 'eu_commission_news_all.csv'

        # Write the data to a CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['page', 'title', 'link', 'date', 'description']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_articles_data)

        print(f"\nSuccessfully scraped {len(all_articles_data)} articles and saved them to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")