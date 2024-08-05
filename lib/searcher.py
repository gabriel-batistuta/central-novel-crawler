from requests import get
from bs4 import BeautifulSoup
from typing import Union
import json

def make_json(series: dict) -> None:
    with open('series.json', 'w') as f:
        json.dump(series, f, indent=4, ensure_ascii=False)

def get_page(url:str) -> BeautifulSoup:
    return BeautifulSoup(get(url).content, 'html.parser')

def get_page_soup(url: Union[str, BeautifulSoup]) -> BeautifulSoup:
    if isinstance(url, str):
        page = get_page(url)
    else:
        page = url
    return page

def crawl_series_urls(page: BeautifulSoup, site_location: str) -> list:
    def get_chapter_urls(page:BeautifulSoup):
        container = page.find('div', attrs={'class':'bixbox bxcl epcheck'})
        links = container.find_all('a')
        urls = []
        for url in links:
            urls.append(url['href'])
        return urls
    
    if site_location == 'series page':
        return get_chapter_urls(page)
    elif site_location == 'series chapter':
        series_url = page.find('a', attrs={'aria-label':'Índice'})
        series_url = get_page_soup(series_url['href'])
        return get_chapter_urls(series_url)

def scrape_series_info(page: BeautifulSoup) -> dict:
    series_info = {}
    container = page.find('div', {'class': 'epheader'})
    title = container.find('h1', attrs={'class':'entry-title'}).text.strip()
    chapter_title = container.find('div', attrs={'class':'cat-series'}).text.strip()
    infos = container.find('div', attrs={'class':'entry-info'})
    publisher = infos.find('span', {'class':'vcard author'}).text
    views = infos.find('span', {'id':'post-views'}).text.strip().replace(' Visualizações','').strip()
    date_published = infos.find('span', {'class':'updated'}).text.strip()

    return {
        'series_title': title,
        'chapter_title': chapter_title,
        'publisher': publisher,
        'views': views,
        'date_published': date_published,
    }

def scrapes_series_chapter(page: BeautifulSoup) -> str:
    chapter = page.find('div', {'class':'epcontent entry-content'})
    ps = chapter.find_all('p')
    chapter = ''
    for p in ps:
        chapter += p.text.strip() + '\n'

    return chapter

def main_handler(url:str):
    page = get_page_soup(url)
    if '/series/' in url:
        urls = crawl_series_urls(page, 'series page')
    else:
        urls = crawl_series_urls(page, 'series chapter')
    series = {}
    for url in urls:
        print(f'Crawling: {url}')
        series_info = scrape_series_info(get_page_soup(url))
        series_info['chapter'] = scrapes_series_chapter(get_page_soup(url))
        series[url] = series_info
    make_json(series)

if __name__ == "__main__":
    url = 'https://centralnovel.com/the-beginning-after-the-end-capitulo-0/'
    series_info = scrape_series_info(get_page_soup(url))
    series_info['chapters'] = scrapes_series_chapter(get_page_soup(url))
    make_json(series_info)