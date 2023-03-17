from bs4 import BeautifulSoup
import requests
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
USER_ID = os.environ.get("ID")
TOKEN = os.environ.get("TOKEN")

user_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
date = user_date.split("-")
year = date[0]
month = date[1]
day = date[2]
date_formatted = datetime(int(year), int(month), int(day))
day_of_week = date_formatted.strftime("%A")
if day_of_week == "Sunday":
    day = int(day) - 1
    date_formatted = datetime(int(year), int(month), int(day))
    day_of_week = date_formatted.strftime("%A")
else:
    while day_of_week != "Saturday":
        day = int(day) + 1
        date_formatted = datetime(int(year), int(month), int(day))
        day_of_week = date_formatted.strftime("%A")

response = requests.get(
    url=f"https://web.archive.org/web/20190621073634/https://www.billboard.com/charts/hot-100/{year}-{month}-{date_formatted.strftime('%d')}")
response.raise_for_status()
text = response.text

soup = BeautifulSoup(text, "html.parser")
song_info = soup.find_all(name="span", class_="chart-list-item__title-text")
song_names = [song.text.strip() for song in song_info]
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
uri_list = []
for song in song_names:
    try:
        result = sp.search(q=f"track:{song} year:{year}", type="track")
        uri_list.append(result["tracks"]["items"][0]["uri"])
    except IndexError:
        print(f"{song} not available on Spotify. Skipped.")

header = {
    "Authorization": TOKEN
}
sp = spotipy.Spotify(auth=header)
playlist = sp.user_playlist_create(user=USER_ID, name=f"{year}-{month}-{date_formatted.strftime('%d')} Billboard 100",
                                   public=False)
playlist_id = playlist["id"]
sp.playlist_add_items(playlist_id=playlist_id, items=uri_list)
