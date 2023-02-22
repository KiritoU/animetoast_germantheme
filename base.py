import json
import logging
from time import sleep

from bs4 import BeautifulSoup

from _db import database
from german_theme import GermanTheme
from helper import helper
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class Crawler:
    def crawl_soup(self, url):
        logging.info(f"Crawling {url}")
        html = helper.download_url(url)
        if html.status_code == 404:
            return 404

        soup = BeautifulSoup(html.content, "html.parser")

        return soup

    def crawl_movie(self, movieTitle: str, movieHref: str) -> None:
        try:
            soup = self.crawl_soup(movieHref)

            coverUrl = helper.get_cover_img_url(soup, movieHref)
            descriptore = helper.get_descriptore(soup, movieHref)
            runtime = helper.get_runtime(soup, movieHref)
            trailerBox = helper.get_trailer_url(soup, movieHref)
            movieType, movieEpisodes = helper.get_movie_type_and_episodes(
                soup, movieHref
            )

            movieDetails = helper.get_movie_details(soup, movieHref)

            GermanTheme(
                movieTitle=movieTitle,
                coverUrl=coverUrl,
                runtime=runtime,
                descriptore=descriptore,
                trailerBox=trailerBox,
                movieType=movieType,
                movieEpisodes=movieEpisodes,
                movieDetails=movieDetails,
            ).insert_movie()

        except Exception as e:
            helper.log(
                f"Failed to crawl_movie\n{movieHref}\n{e}",
                log_file="base.crawl_page.log",
            )

    def crawl_page(self, pageUrl: str, isHomePage: bool = True) -> bool:
        soup = self.crawl_soup(url=pageUrl)
        if soup == 404:
            return False

        moduleContents = soup.find_all("div", class_="ModuleContent")

        if isHomePage and len(moduleContents) < 2:
            return False

        moduleContent = moduleContents[0]
        if isHomePage:
            moduleContent = moduleContents[1]

        shortEntrys = moduleContent.find_all("div", class_="short-entry")

        if not shortEntrys:
            return False

        for shortEntry in shortEntrys:
            try:
                shortEntryTitle = shortEntry.find("div", class_="short-entry-title")
                aElement = shortEntryTitle.find("a")
                movieHref = aElement.get("href")
                movieTitle = aElement.text

                self.crawl_movie(movieTitle=movieTitle, movieHref=movieHref)
            except Exception as e:
                helper.log(
                    f"Failed to crawl shortEntryTitle\n{e}\n{shortEntry}",
                    log_file="base.crawl_page.log",
                )

        return True


if __name__ == "__main__":
    # Crawler().crawl_page(CONFIG.KINOXTOP_HOMEPAGE)

    # Crawler().crawl_movie(
    #     movieTitle="Gib den Jungs zwei Küsse Stream",
    #     movieHref="https://kinox.top/12515-gib-den-jungs-zwei-kusse-stream.html",
    # )

    Crawler().crawl_movie(
        movieTitle="Anbieter Auswahl für: The Last of Us - Staffel 1",
        movieHref="https://kinox.top/12526-the-last-of-us.html",
    )
