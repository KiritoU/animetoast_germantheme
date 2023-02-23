from time import sleep

from base import Crawler
from helper import helper
from settings import CONFIG

crawler = Crawler()


def main():
    try:
        crawler.crawl_page(CONFIG.ANIMETOAST_HOMEPAGE, is_home_page=True)
    except Exception as e:
        helper.log(log_msg=f"Failed in crawl.py\n{e}", log_file="update.log")


if __name__ == "__main__":
    while True:
        main()
        sleep(CONFIG.WAIT_BETWEEN_UPDATE)
