from time import sleep

from base import Crawler
from helper import helper
from settings import CONFIG

crawler = Crawler()


def main():
    for page in range(1, CONFIG.KINOXTOP_AKTUELLE_KINOFILME_PAGE_LAST_PAGE):
        url = f"{CONFIG.KINOXTOP_AKTUELLE_KINOFILME_PAGE}/page/{page}/"
        try:
            crawler.crawl_page(url, isHomePage=False)
        except Exception as e:
            helper.log(log_msg=f"Failed in crawl.py\n{e}", log_file="update.log")


if __name__ == "__main__":
    while True:
        main()
        sleep(CONFIG.WAIT_BETWEEN_LATEST)
