import requests
from bs4 import BeautifulSoup
import math
import csv
import time
from playwright.sync_api import sync_playwright

# Define the base URL and headers
BASE_URL = "https://commission.europa.eu"
NEWS_LIST_URL = f"{BASE_URL}/news-and-media/news_en"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"}

def scrape_description_with_playwright(article_url, selector_list):
    """
    Uses Playwright to render the page, execute JavaScript, and scrape the full description.
    """
    print(f"  -> Falling back to Playwright for {article_url}...")
    
    # Ensure URL is absolute
    if not article_url.startswith('http'):
        article_url = f"{BASE_URL}{article_url}"
    
    description = []
    
    try:
        with sync_playwright() as p:
            # Launch a headless Chromium browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to the URL and wait for the network to be idle, ensuring JS has executed
            page.goto(article_url, wait_until="networkidle", timeout=30000)
            
            # Use the page's content after rendering
            rendered_html = page.content()
            browser.close()
            
            soup = BeautifulSoup(rendered_html, 'html.parser')
            
            # Iterate through the selectors on the rendered HTML
            for selector in selector_list:
                paragraphs = soup.select(selector)
                if paragraphs:
                    for p in paragraphs:
                        text = p.text.strip()
                        if text:
                            description.append(text)
                    
                    if description:
                        # Return the first successful extraction
                        return "\n".join(description)

    except Exception as e:
        print(f"  -> Playwright Error for {article_url}: {e}")
        
    return "No full description found (Playwright failed)."


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

def scrape_description(article_url):
    """
    Scrapes the full description, first using requests/BeautifulSoup, then falling back to Playwright.
    """
    # 1. Prepare URL and selectors
    if not article_url.startswith('http'):
        full_article_url = f"{BASE_URL}{article_url}"
    else:
        full_article_url = article_url
        
    # Consolidated list of potential selectors
    description_selectors = [
        'div.ecl-paragraph p',
        'div.long-text p',
        'div.oe-text-body p',
        'div.ecl-u-mt-l p',
        'div#PressContent div.content p',
        'div.ecl-field-type-html-content p',
        'div.article-content p',
        'div.ecl-field-type-text-long p',
        'div.news-body p',
        'div.long-text p:not(:has(a))',
        'div.field-name-body p',
        'div.field-items p',
        'div.ecl-col-s-12.ecl-col-m-8 p',
        'div.ecl-content-block__description p',
        'div#main-content p',
        'article p',
        'main p'
    ]

    # 2. FIRST ATTEMPT: Static scraping with requests
    page_content = get_page_content(full_article_url)
    if not page_content:
        # If the request itself failed (404, timeout, etc.), no need for Playwright.
        return "No full description found (Request failed)."
    
    soup = BeautifulSoup(page_content, 'html.parser')
    description = []
    
    for selector in description_selectors:
        paragraphs = soup.select(selector)
        if paragraphs:
            for p in paragraphs:
                text = p.text.strip()
                if text:
                    description.append(text)
            
            if description:
                return "\n".join(description)

    # 3. FALLBACK: Dynamic scraping with Playwright
    # Only fall back if the static scrape yielded no content (likely due to JS loading)
    return scrape_description_with_playwright(full_article_url, description_selectors)

# --- Main Script Logic ---
if __name__ == "__main__":
    
    date_range = "oe_news_publication_date:bt|2025-09-11T19:48:17+02:00|2025-10-11T19:48:17+02:00"
    base_params = {"f[0]": date_range}

    try:
        print("Fetching first page to determine total news count...")
        initial_page_content = get_page_content(NEWS_LIST_URL, params=base_params)
        soup = BeautifulSoup(initial_page_content, 'html.parser')

        # Logic to find total news count and pages_to_crawl remains the same
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
                
                description = scrape_description(summary_data['link'])
                
                article_data = {
                    "title": summary_data['title'],
                    "link": summary_data['link'],
                    "date": summary_data['date'],
                    "summary": summary_data['summary'],
                    "description": description
                }
                all_articles_data.append(article_data)
                
                time.sleep(1)

        output_file = 'eu_commission_news.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'link', 'date', 'summary', 'description']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_articles_data)

        print(f"\nScraping complete. A total of {len(all_articles_data)} articles have been saved to '{output_file}'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")