from termcolor import colored
from urllib.request import Request, urlopen
import requests
import yaml
import json
from pprint import pprint
import time


class Radarrhelper:

    def __init__(self):
        self.load_config()

    def load_config(self):
        file = open('./config/config.yaml', 'r')
        config = yaml.load(file, Loader=yaml.FullLoader)

        self.api_key = config['radarr']['api_key']
        self.auto_download = config['radarr']['auto_download']
        self.host = config['radarr']['host']
        self.profileId = config['radarr']['profileId']
        self.download_path = config['radarr']['download_path']
        self.library = self.get_radarr_library()

        if self.api_key == '<API_KEY>':
            print(colored(' > Please set an API key for Radarr.'))
            exit(0)

    def movie_lookup_imdb(self, id):
        data = None
        try:
            url = 'http://' + self.host + '/api/movie/lookup/imdb?imdbId=' + id + '&apikey=' + self.api_key
            data = requests.get(url).json()
        except:
            pass

        return data

    def verify_if_movie_in_radarr(self, slug):
        for item in self.library:
            if item['titleSlug'] == slug:
                return True

        return False

    def get_radarr_library(self):
        url = 'http://' + self.host + '/api/movie?&apikey=' + self.api_key
        data = requests.get(url).json()
        return data

    def add_movie_to_radarr(self, movie):

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            "title": movie['title'],
            "qualityProfileId": str(self.profileId),
            "titleslug": movie['titleSlug'],
            "monitored": "true",
            "images": movie['images'],
            "tmdbid": movie['tmdbId'],
            "year": movie['year'],
            "rootFolderPath": str(self.download_path),
            "addOptions": {
                "searchForMovie": self.auto_download
            }
        }

        url = 'http://' + self.host + '/api/movie?apikey=' + self.api_key
        request = Request(url, data=json.dumps(data).encode(), headers=headers)
        urlopen(request).read()

