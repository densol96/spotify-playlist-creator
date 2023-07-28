import requests
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lxml


class SpotifyPlaylistMaker:

    CLIENT_ID = os.environ["CLIENT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]

    def __init__(self):
        self.year_choice = self.input_validation()
        self.tracks = self.scraper(self.year_choice)
        self.sp = self.authenticate()
        self.user_id = self.sp.current_user()["id"]
        self.create_playlist(self.tracks)

    def input_validation(self):
        print("Welcome to Spotify Playlist Creator!")
        print("Just enter the year and we will make the best playlists based off Billboard of that year!")
        while True:
            year = input("Enter a year: ")
            if len(year) == 4:
                for num in year:
                    if not num.isdigit():
                        break
                else:
                    break
        return int(year)

    def scraper(self, year_choice):
        response = requests.get(f"https://www.billboard.com/charts/hot-100/{year_choice}-08-12/")
        soup = BeautifulSoup(response.text, "lxml")
        titles = soup.select("ul > li > h3[id='title-of-a-story'].c-title")
        authors = soup.select("ul > li > h3[id='title-of-a-story'].c-title + span.c-label")
        list_of_titles = []
        with open("artists.txt", mode="w") as f:
            for index in range(0, len(titles)):
                title = titles[index].getText().strip()
                author = authors[index].getText().strip()
                f.write(f"{title} By {author}")
                f.write("\n")
                list_of_titles.append(f"{title} By {author}")
        
        return list_of_titles

    def authenticate(self):
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope="playlist-modify-private",
                redirect_uri="http://example.com",
                client_id=SpotifyPlaylistMaker.CLIENT_ID,
                client_secret=SpotifyPlaylistMaker.CLIENT_SECRET,
                show_dialog=True,
                cache_path="token.txt"
            )
        )
        
        return sp

    def create_playlist(self, tracks):
        list_of_uris = []

        for search_query in tracks:
            try:
                search_result = self.sp.search(q=f"{search_query} {self.year_choice}", limit=1, type="track")
                uri = search_result["tracks"]["items"][0]["uri"]
                list_of_uris.append(uri)
            except:
                print(f"SONG QUERY ERROR FOR {search_query}")

        playlist = self.sp.user_playlist_create(user=self.user_id, name=f"{self.year_choice} Billboard 100", public=False)
        self.sp.playlist_add_items(playlist_id=playlist["id"], items=list_of_uris)



SpotifyPlaylistMaker()