import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from slugify import slugify

from _db import database
from settings import CONFIG

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


@dataclass
class GermanTheme:
    movieTitle: str
    coverUrl: str
    runtime: str
    descriptore: str
    trailerBox: str
    movieType: str
    movieEpisodes: list
    movieDetails: dict

    def get_genre_id(self, genre: str) -> int:
        table = "genre"
        condition = f'name="{genre}"'
        data = [genre, ""] + [slugify(genre)] * 4

        genre = database.select_or_insert(table=table, condition=condition, data=data)

        return genre[0][0]

    def get_genres(self) -> str:
        genres = self.movieDetails.get("Genre", "NULL")
        genres = [x.strip() for x in genres.split("/")]

        genres_id = [{"id": self.get_genre_id(genre.strip())} for genre in genres]

        return json.dumps(genres_id)

    def get_director_or_cast(self, key: str) -> str:
        directors = self.movieDetails.get(key, "")
        directorsObj = [{"name": director.strip()} for director in directors.split(",")]

        return json.dumps(directorsObj)

    def get_image(self) -> str:
        if "http" not in self.coverUrl:
            return f"{CONFIG.KINOXTOP_HOMEPAGE}{self.coverUrl}"

        return self.coverUrl

    def get_time_update(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_movie_id(self) -> int:
        logging.info(f"Getting movie id for: {self.movieTitle}")
        movie = {
            "title": self.movieTitle,
            "description": self.descriptore,
            "genre": self.get_genres(),
            "type": self.movieType,
            "duration": self.runtime.replace("min", "").strip(),
            "year": 0,
            "quality": self.movieDetails.get("Auflösung", "HD"),
            "other_name": self.movieTitle,
            "nation": self.movieDetails.get("Das Land", "USA"),
            "director": self.get_director_or_cast(key="Regisseur"),
            "cast": self.get_director_or_cast(key="Schauspieler"),
            "image": self.get_image(),
            "keywords": "",
            "season": "",
            "language": "",
            "ratting": 0,
            "ratting_link": "",
            "trailer": self.trailerBox,
            "slug": slugify(self.movieTitle),
            "view": 0,
            "public": 1,
            "date": self.get_time_update(),
            "time": self.get_time_update(),
        }

        table = "movie"
        condition = f'title="{self.movieTitle}"'
        data = list(movie.values())

        movie = database.select_or_insert(table=table, condition=condition, data=data)

        return movie[0][0]

    def validate_movie_episodes(self) -> None:
        res = []
        for episode in self.movieEpisodes:
            episodeName, episodeLinks = episode
            # episodeName = episodeName.replace("Episoden", "").strip()
            episodeName = episodeName.strip()
            if episodeLinks:
                res.append([episodeName, episodeLinks])

        self.movieEpisodes = res

    def get_server_name_from(self, link: str) -> str:
        x = re.search(r"//[^/]*", link)
        if x:
            return x.group().replace("//", "")

        return "Default"

    def get_episode_server_from(self, links: list) -> list:
        removeLinks = ["/vod/online.html", "/vod/onlines.html"]
        for removeLink in removeLinks:
            if removeLink in links:
                links.remove(removeLink)
        res = [
            {
                "server_name": self.get_server_name_from(link),
                "server_type": "embed",
                "server_url": link,
            }
            for link in links
        ]

        return res

    def get_episode_data(self) -> list:
        if self.movieType == "cinema":
            res = [
                {
                    "episode_int": 1,
                    "episode_name": "1",
                    "episode_server": self.get_episode_server_from(self.movieEpisodes),
                }
            ]
        else:
            res = []
            for i, episode in enumerate(self.movieEpisodes):
                episodeName, episodeLinks = episode
                res.append(
                    {
                        "episode_int": i + 1,
                        "episode_name": episodeName,
                        "episode_server": self.get_episode_server_from(episodeLinks),
                    }
                )

        return res

    def insert_episodes(self, movieId: int) -> None:
        logging.info(
            f"Updating episodes for movie {self.movieTitle} with ID: {movieId}"
        )
        if self.movieType == "seriel":
            self.validate_movie_episodes()

        data = [{"season_name": 1, "episode_data": self.get_episode_data()}]
        data = json.dumps(data)

        episode_data = database.select_or_insert(
            table="episode", condition=f"movie_id={movieId}", data=(movieId, data)
        )

        if episode_data[0][2].decode() != data:
            print("Diff")
            database.update_table(
                table="episode",
                set_cond=f"data={data}",
                where_cond=f"movie_id={movieId}",
            )

    def insert_movie(self):
        movieId = self.get_movie_id()
        self.insert_episodes(movieId=movieId)

        # with open("test/movie.json", "w") as f:
        #     f.write(
        #         json.dumps(
        #             {
        #                 "movieTitle": self.movieTitle,
        #                 "coverUrl": self.coverUrl,
        #                 "runtime": self.runtime,
        #                 "descriptore": self.descriptore,
        #                 "trailerBox": self.trailerBox,
        #                 "movieType": self.movieType,
        #                 "movieEpisodes": self.movieEpisodes,
        #                 "movieDetails": self.movieDetails,
        #             },
        #             indent=4,
        #             ensure_ascii=False,
        #         )
        #     )
