import requests
from bs4 import BeautifulSoup
import math
import csv
import time

# Define the base URL and headers
BASE_URL = "https://commission.europa.eu"
NEWS_LIST_URL = f"{BASE_URL}/news-and-media/news_en"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

def get_page_content(url, params=None):
    """Fetches the HTML content of a given URL."""
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_articles_from_soup(soup):
    """Parses a BeautifulSoup object to find a list of valid news articles."""
    articles = []
    article_containers = soup.find_all('div', class_='ecl-content-item-block__item')
    
    for container in article_containers:
        article = container.find('article', class_='ecl-content-item')
        if 'ecl-col-l-6' not in container.get('class', []) and article:
            articles.append(article)
    return articles

def extract_article_summary_data(article_tag):
    """Extracts summary data (title, link, date, summary) from a single article tag."""
    title_tag = article_tag.find('div', class_='ecl-content-block__title').find('a')
    title = title_tag.text.strip()
    link = title_tag['href']
    
    date_tag = article_tag.find('time')
    date = date_tag.text.strip() if date_tag else "No date available."
    
    summary_tag = article_tag.find('div', class_='ecl-content-block__description')
    summary = summary_tag.text.strip() if summary_tag else "No summary available."
    
    return {
        "title": title,
        "link": link,
        "date": date,
        "summary": summary
    }

def scrape_full_description(article_url):
    """
    Scrapes the full description from an article's page by trying a wider range of selectors.
    """
    if not article_url.startswith('http'):
        article_url = f"{BASE_URL}{article_url}"
    
    page_content = get_page_content(article_url)
    if not page_content:
        return "No full description found."
    
    soup = BeautifulSoup(page_content, 'html.parser')

    description_selectors = [
        'div.ecl-paragraph > p',
        'div.ecl-u-mt-l > p',
        'div#main-content p',
        'div.node-content-block p',
        'div.long-text > p',
        'div.ecl-content-block__description',
        'main.ecl-u-pb-xl p',
        'article div.content-wrapper p',
        'div.ecl-content-block__body p',
        'div.ecl-container div.ecl-row div.ecl-col-s-12 p'
    ]
    
    full_description = []
    
    for selector in description_selectors:
        paragraphs = soup.select(selector)
        if paragraphs:
            for p in paragraphs:
                text = p.text.strip()
                if text:
                    full_description.append(text)
            
            if full_description:
                return "\n".join(full_description)
    
    return "No full description found."

# --- Main Script Logic ---
if __name__ == "__main__":
    date_range = "oe_news_publication_date:bt|2025-09-11T19:48:17+02:00|2025-10-11T19:48:17+02:00"
    base_params = {"f[0]": date_range}

    try:
        print("Fetching first page to determine total news count...")
        initial_page_content = get_page_content(NEWS_LIST_URL, params=base_params)
        soup = BeautifulSoup(initial_page_content, 'html.parser')

        total_news_tag = soup.find('div', class_='ecl-u-border-bottom ecl-u-border-width-2 ecl-u-d-flex ecl-u-justify-content-between ecl-u-align-items-end').find('h4', class_='ecl-u-type-heading-4 ecl-u-mb-s')
        total_news_text = total_news_tag.find_all('span')[-1].text
        total_news_count = int("".join(filter(str.isdigit, total_news_text)))
        pages_to_crawl = math.ceil(total_news_count / 10)
        
        print(f"Total news articles found: {total_news_count}")
        print(f"Total pages to crawl: {pages_to_crawl}")
        print("-" * 30)

        all_articles_data = []

        for page_num in range(pages_to_crawl):
            print(f"Scraping articles from Page {page_num + 1}...")
            page_content = get_page_content(NEWS_LIST_URL, params={**base_params, "page": page_num})
            soup = BeautifulSoup(page_content, 'html.parser')
            
            articles_on_page = parse_articles_from_soup(soup)
            
            for article_tag in articles_on_page:
                summary_data = extract_article_summary_data(article_tag)
                
                full_description = scrape_full_description(summary_data['link'])
                
                article_data = {
                    "title": summary_data['title'],
                    "link": summary_data['link'],
                    "date": summary_data['date'],
                    "summary": summary_data['summary'],
                    "full_description": full_description
                }
                all_articles_data.append(article_data)
                
                time.sleep(1)

        output_file = 'eu_commission_news.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'link', 'date', 'summary', 'full_description']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_articles_data)

        print(f"\nScraping complete. A total of {len(all_articles_data)} articles have been saved to '{output_file}'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")