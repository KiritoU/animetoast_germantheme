from time import sleep

from base import Crawler
from helper import helper
from settings import CONFIG

crawler = Crawler()


def main():
    for page in range(1, 10000):
        url = CONFIG.ANIMETOAST_SEARCHPAGE.format(page)

        is_crawled = crawler.crawl_page(url)

        if not is_crawled:
            break


if __name__ == "__main__":
    while True:
        main()
        sleep(CONFIG.WAIT_BETWEEN_ALL)
