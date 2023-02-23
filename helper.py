import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

from _db import database
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class Helper:
    def get_header(self):
        header = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150",  # noqa: E501
            "Accept-Encoding": "gzip, deflate",
            # "Cookie": CONFIG.COOKIE,
            "Cache-Control": "max-age=0",
            "Accept-Language": "vi-VN",
            # "Referer": "https://mangabuddy.com/",
        }
        return header

    def download_url(self, url):
        return requests.get(url, headers=self.get_header())

    def crawl_soup(self, url):
        logging.info(f"Crawling {url}")
        html = helper.download_url(url)
        if html.status_code == 404:
            return 404

        soup = BeautifulSoup(html.content, "html.parser")

        return soup

    def log(self, log_msg, log_file: str, is_error_log: bool = True) -> None:
        Path(CONFIG.LOG_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(CONFIG.TMP_FOLDER).mkdir(parents=True, exist_ok=True)
        log_file = f"{CONFIG.LOG_FOLDER}/{log_file}"
        with open(CONFIG.TMP_FILE, "w") as f:
            f.write(f"{time.asctime()} LOG: {log_msg}\n")

        cmd = f"cat {CONFIG.TMP_FILE} >> {log_file}"
        if Path(log_file).is_file() and is_error_log:
            cmd = f"""grep -q "{log_msg}" {log_file} || {cmd}"""
        os.system(cmd)

    def get_title(self, soup: BeautifulSoup, movie_href: str) -> str:
        try:
            return soup.find("div", class_="title-info").find("h1").text
        except Exception as e:
            self.log(
                f"Error get_title {movie_href}",
                log_file="helper.get_title.log",
            )
            return ""

    def get_cover_img_url_and_description(
        self, soup: BeautifulSoup, movie_href: str
    ) -> str:
        try:
            p_elements = soup.find_all("p")

            description_texts = [p_element.text for p_element in p_elements[:-3]] + [
                strong.text for strong in p_elements[-1].find_all("strong")
            ]
            description = "\n".join(description_texts)

            cover_url = p_elements[0].find("img").get("src")

            return [cover_url, description]
        except Exception as e:
            self.log(
                f"Error get_cover_img_url {movie_href}",
                log_file="helper.get_cover_img_url.log",
            )
            return ["", ""]

    def get_descriptore(self, soup: BeautifulSoup, movie_href: str) -> str:
        try:
            return soup.find("div", class_="Descriptore").text
        except Exception as e:
            self.log(
                f"Error getting Descriptore {movie_href}",
                log_file="helper.get_descriptore.log",
            )
            return ""

    def get_runtime(self, soup: BeautifulSoup, movie_href: str) -> str:
        return "0"
        # try:
        #     customDetails = soup.find("ul", class_="CustomDetails")
        #     runtime = customDetails.find("li", {"title": "Runtime"})
        #     return runtime.text.replace("~", "").replace(".", "").strip()
        # except Exception as e:
        #     self.log(
        #         f"Error get_runtime {movie_href}",
        #         log_file="helper.get_runtime.log",
        #     )
        #     return ""

    def get_trailer_url(self, soup: BeautifulSoup, movie_href: str) -> str:
        return ""
        # try:
        #     return soup.find("div", {"id": "trailer-box"}).find("iframe").get("src")
        # except Exception as e:
        #     self.log(
        #         f"Error getting trailer URL {movie_href}",
        #         log_file="helper.get_trailer_url.log",
        #     )
        #     return ""

    def get_episode_iframe_src(self, episode_href: str) -> str:
        soup = self.crawl_soup(url=episode_href)

        res = ""

        try:
            player_embed = soup.find("div", {"id": "player-embed"})
            iframe = player_embed.find("iframe")
            if iframe:
                res = iframe.get("src")
            else:
                a = player_embed.find("a")
                res = a.get("href")

        except:
            self.log(
                log_msg=f"Error getting episode iframe URL {episode_href}",
                log_file="helper.get_episode_iframe_src.log",
            )

        return res

    def get_movie_type_and_episodes(self, soup: BeautifulSoup, movie_href: str) -> list:
        movie_type = ""
        movie_episodes = []

        try:
            movie_type = "seriel"
            movie_episodes_dict = {}

            for i in range(5):
                try:
                    multi_link_tab_id = f"multi_link_tab{i}"
                    multi_link_tab = soup.find("div", {"id": multi_link_tab_id})

                    a_elements = multi_link_tab.find_all("a")
                    for a_element in a_elements:
                        episode_href = a_element.get("href")

                        episode_name = a_element.text.strip()
                        movie_episodes_dict.setdefault(episode_name, [])

                        episode_iframe_src = self.get_episode_iframe_src(
                            episode_href=episode_href
                        )
                        if episode_iframe_src:
                            movie_episodes_dict[episode_name].append(episode_iframe_src)

                except:
                    pass

            for episode_name, episode_links in movie_episodes_dict.items():
                movie_episodes.append([episode_name, episode_links])

        except Exception as e:
            self.log(
                f"Error getting get_movie_type_and_episodes {movie_href}",
                log_file="helper.get_movie_type_and_episodes.log",
            )

        return [movie_type, movie_episodes]

    def get_movie_details(self, soup: BeautifulSoup, movie_href: str) -> dict:
        movie_details = {}
        try:
            p_elements = soup.find_all("p")

            movie_details["Genre"] = p_elements[-3].text.replace("Genre:", "")

        except Exception as e:
            self.log(
                f"Error get_movie_details {movie_href}",
                log_file="helper.get_movie_details.log",
            )

        return movie_details


helper = Helper()
