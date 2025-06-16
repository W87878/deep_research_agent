import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re
import random
import trafilatura

def contains_date(url: str) -> bool:
    # 匹配格式：2025/06/13 或 1999/01/01
    pattern = r'\b\d{4}/\d{2}/\d{2}\b'
    return bool(re.search(pattern, url))


def get_webdriver(user_data_dir: str = None, profile_directory: str = "Default", set_profile: bool = False, headless: bool = True):
    driver=None
    for attempt in range(3):  # 嘗試最多 3 次
        try:
            options = uc.ChromeOptions()
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            if headless:
                options.add_argument("headless")
            if set_profile:
                options.add_argument(f"--user-data-dir={user_data_dir}")
                options.add_argument(f'--profile-directory={profile_directory}')
            driver=uc.Chrome(options=options, version_main=136, use_subprocess=True)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver

        except Exception as e:
            print(f'Error: {e}')
            print(f"WebDriver 啟動失敗，第 {attempt + 1} 次嘗試...")
            if attempt == 2:
                raise e
            time.sleep(2)  # 等待 2 秒後重試


# news
def crawl_news_articles(query: str, user_data_dir, profile_directory, max_results: int = 10):
    driver = get_webdriver(user_data_dir, profile_directory)
    search_query = quote(query)
    url = f'https://technews.tw/google-search/?googlekeyword={search_query}'
    driver.get(url)
    time.sleep(1)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    print(f"🔍 正在搜尋：{query}")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div_search = soup.find('div', id='___gcse_0').find('div', class_='gsc-resultsbox-visible').find('div', class_='gsc-expansionArea')
    # print(div_search)
    news_items = []

    for g in div_search.find_all("a", {'class':'gs-title'})[0:max_results*2:2]:
        title = g.text
        link = g['href']
        print('title:', title)
        print('link:', link)
        if not contains_date(link):
            continue
        link_soup = BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')
        # 取得新聞內容
        if link_soup.find('body') is None:
            print(f"⚠️ 無法解析新聞內容：{link}")
            continue
        content = link_soup.find('body').find('div', id='main').text
        if not content.strip():
            print(f"⚠️ 無法取得新聞內容：{link}")
            continue 

        news_items.append(f"標題：{title}\n\n內容：{content.strip()}\n\n來源：{link}\n")

    return news_items

def crawl_news_articles_stream(query: str, user_data_dir, profile_directory, set_profile: bool = False, headless: bool = True, max_results: int = 10):
    driver = get_webdriver(user_data_dir, profile_directory, set_profile, headless)
    prefix_lst=['https://searx.ox2.fr/','https://searx.rhscz.eu/','https://searx.tiekoetter.com/','https://priv.au/','https://search.hbubli.cc/','https://search.ononoki.org/','https://opnxng.com/','https://search.sapti.me/','https://searxng.site/','https://search.catboy.house/','https://search.leptons.xyz/','https://searx.dresden.network/','https://searxng.shreven.org/','https://search.url4irl.com/','https://searx.oloke.xyz/','https://search.nerdvpn.de/','https://searx.lunar.icu/']
    prefix=random.choice(prefix_lst)
    search_query = quote(query)
    # 查找符合條件的搜尋引擎 - time_range= 'day'/'week'/'month'/year
    url = prefix+'search?q={}&language=zh-TW&time_range=week'.format(search_query)
    driver.get(url)
    time.sleep(1)
    print(f"🔍 正在搜尋：{query}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div_search = soup.find('div', id='results')
    if not div_search:
        print("⚠️ 找不到搜尋結果容器")
        return []

    articles = div_search.find_all("article") if div_search else []
    # print(div_search)
    news_items = []

    for g in articles[:max_results]:
        title = g.find('h3').text
        link = g.find('a')['href']
        print('title:', title)
        print('link:', link)
        downloaded = trafilatura.fetch_url(link)
        content = trafilatura.extract(downloaded, include_comments=False) if downloaded else ""
        # print("爬取的內容：", content[:1000])  # 只打印前1000個字符以避免過長輸出
        if content is None:
            print(f"⚠️ 無法解析新聞內容：{link}")
            continue
        if not content.strip():
            print(f"⚠️ 無法取得新聞內容：{link}")
            continue

        news_items.append({
            "title": title,
            "content": content.strip(),
            "url": link
        })

    return news_items


if __name__ == "__main__":
    user_data_dir = '/Users/steve.wang/Library/Application\\ Support/Google/Chrome'
    profile_directory = 'Profile 1'  # Profile 1, Profile 2, Default, etc.
    query = "AI新聞"
    articles = crawl_news_articles_stream(query, user_data_dir, profile_directory)
    for article in articles:
        print(article)

