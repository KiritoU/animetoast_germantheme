import json
import logging
from time import sleep

from bs4 import BeautifulSoup

from _db import database
from german_theme import GermanTheme
from helper import helper
from settings import CONFIG


class Crawler:
    def crawl_anime(self, anime_href: str) -> None:
        try:
            soup = helper.crawl_soup(anime_href)

            title = helper.get_title(soup, anime_href)

            item_content = soup.find("div", class_="item-content")
            cover_url, descriptore = helper.get_cover_img_url_and_description(
                item_content, anime_href
            )

            runtime = helper.get_runtime(item_content, anime_href)
            trailerBox = helper.get_trailer_url(item_content, anime_href)

            movieType, movieEpisodes = helper.get_movie_type_and_episodes(
                item_content, anime_href
            )

            movieDetails = helper.get_movie_details(item_content, anime_href)

            GermanTheme(
                movieTitle=title,
                coverUrl=cover_url,
                runtime=runtime,
                descriptore=descriptore,
                trailerBox=trailerBox,
                movieType=movieType,
                movieEpisodes=movieEpisodes,
                movieDetails=movieDetails,
            ).insert_movie()

        except Exception as e:
            helper.log(
                f"Failed to crawl_movie\n{anime_href}\n{e}",
                log_file="base.crawl_page.log",
            )

    def crawl_anime_from_item(self, item: BeautifulSoup) -> None:
        href = ""
        thumbnail_src = ""

        item_thumbnail = item.find("div", class_="item-thumbnail")
        if item_thumbnail.find("a"):
            href = item_thumbnail.find("a").get("href")

        if item_thumbnail.find("img"):
            thumbnail_src = item_thumbnail.find("img").get("src")

        if not href:
            item_head = item.find("div", class_="item-head")
            if item_head.find("a"):
                href = item_head.find("a").get("href")

        self.crawl_anime(anime_href=href)
        # print([href, thumbnail_src])

    def crawl_page(self, page_url: str, is_home_page: bool = False) -> bool:
        soup = helper.crawl_soup(url=page_url)
        if soup == 404:
            return False

        if is_home_page:
            smart_box_content = soup.find("div", class_="smart-box-content")
            rows = smart_box_content.find_all("div", class_="row")
            for row in rows:
                video_items = row.find_all("div", class_="video-item")
                for video_item in video_items:
                    self.crawl_anime_from_item(item=video_item)

        else:
            search_listing_content = soup.find("div", class_="search-listing-content")
            if not search_listing_content:
                print("No search listing content")
                return False

            rows = search_listing_content.find_all("div", class_="row")
            for row in rows:
                self.crawl_anime_from_item(item=row)

        return True


if __name__ == "__main__":
    x = Crawler().crawl_page(CONFIG.ANIMETOAST_HOMEPAGE, is_home_page=True)
    # x = Crawler().crawl_page(CONFIG.ANIMETOAST_SEARCHPAGE.format(1), is_home_page=False)
    print(x)

    # Crawler().crawl_movie(
    #     movie_href="https://www.animetoast.cc/tomo-chan-wa-onnanoko-ger-sub/",
    # )
    # Crawler().crawl_movie(
    #     movie_href="https://www.animetoast.cc/tensei-oujo-to-tensai-reijou-no-mahou-kakumei-ger-sub/",
    # )
