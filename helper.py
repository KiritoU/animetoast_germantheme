import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

from _db import database
from settings import CONFIG


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

    def get_cover_img_url(self, soup: BeautifulSoup, movieHref: str) -> str:
        try:
            return soup.find("div", class_="Grahpics").find("img").get("src")
        except Exception as e:
            self.log(
                f"Error get_cover_img_url {movieHref}",
                log_file="helper.get_cover_img_url.log",
            )
            return ""

    def get_descriptore(self, soup: BeautifulSoup, movieHref: str) -> str:
        try:
            return soup.find("div", class_="Descriptore").text
        except Exception as e:
            self.log(
                f"Error getting Descriptore {movieHref}",
                log_file="helper.get_descriptore.log",
            )
            return ""

    def get_runtime(self, soup: BeautifulSoup, movieHref: str) -> str:
        try:
            customDetails = soup.find("ul", class_="CustomDetails")
            runtime = customDetails.find("li", {"title": "Runtime"})
            return runtime.text.replace("~", "").replace(".", "").strip()
        except Exception as e:
            self.log(
                f"Error get_runtime {movieHref}",
                log_file="helper.get_runtime.log",
            )
            return ""

    def get_trailer_url(self, soup: BeautifulSoup, movieHref: str) -> str:
        try:
            return soup.find("div", {"id": "trailer-box"}).find("iframe").get("src")
        except Exception as e:
            self.log(
                f"Error getting trailer URL {movieHref}",
                log_file="helper.get_trailer_url.log",
            )
            return ""

    def get_movie_type_and_episodes(self, soup: BeautifulSoup, movieHref: str) -> list:
        try:
            mirrorModule = soup.find("div", class_="MirrorModule")
            series = mirrorModule.find("div", class_="series")
            if series:
                movieType = "seriel"
                movieEpisodes = []

                epMenu = series.find("ul", class_="ep-menu")
                epLis = epMenu.find_all("li")
                for epLi in epLis:
                    episodeName = epLi.find("a").text

                    lis = epLi.find_all("li")
                    episodeLinks = [li.find("a").get("data-link") for li in lis]

                    movieEpisodes.append([episodeName, episodeLinks])
                return [movieType, movieEpisodes]

            hosterList = mirrorModule.find("ul", {"id": "HosterList"})
            if hosterList:
                movieType = "cinema"
                lis = hosterList.find_all("li")
                movieEpisodes = [li.get("data-link") for li in lis]
                return [movieType, movieEpisodes]

            return ["", []]

        except Exception as e:
            self.log(
                f"Error getting get_movie_type_and_episodes {movieHref}",
                log_file="helper.get_movie_type_and_episodes.log",
            )
            return ["", []]

    def get_movie_details(self, soup: BeautifulSoup, movieHref: str) -> dict:
        try:
            movieDetails = {}
            commonModuleTable = soup.find("table", class_="CommonModuleTable")
            trs = commonModuleTable.find_all("tr")
            for tr in trs:
                label = tr.find("td", class_="Label").text.replace(":", "").strip()
                value = tr.find("td", class_="Value").text
                movieDetails[label] = value

            return movieDetails
        except Exception as e:
            self.log(
                f"Error get_movie_details {movieHref}",
                log_file="helper.get_movie_details.log",
            )
            return {}


helper = Helper()
