from time import sleep

from base import Crawler
from helper import helper
from settings import CONFIG

crawler = Crawler()


def get_last_page() -> int:
    try:
        soup = crawler.crawl_soup(CONFIG.KINOXTOP_HOMEPAGE)
        bottom_navi = soup.find("div", class_="bottom_navi")
        pages = bottom_navi.find("div", class_="pages")
        aElements = pages.find_all("a")
        lastPage = aElements[-1].text

        return int(lastPage)
    except:
        return 0


def main():
    lastPage = get_last_page()

    for page in range(1, lastPage):
        url = f"{CONFIG.KINOXTOP_HOMEPAGE}/page/{page}/"
        try:
            crawler.crawl_page(url)
        except Exception as e:
            helper.log(log_msg=f"Failed in crawl.py\n{e}", log_file="crawl.log")


if __name__ == "__main__":
    while True:
        main()
        sleep(CONFIG.WAIT_BETWEEN_ALL)
