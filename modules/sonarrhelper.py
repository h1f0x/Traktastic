from termcolor import colored
from urllib.request import Request, urlopen
import requests
import yaml
import json


class Sonarrhelper:

    def __init__(self):
        self.load_config()

    def load_config(self):
        file = open('./config/config.yaml', 'r')
        config = yaml.load(file, Loader=yaml.FullLoader)

        self.api_key = config['sonarr']['api_key']
        self.auto_download = config['sonarr']['auto_download']
        self.host = config['sonarr']['host']
        self.profileId = config['sonarr']['profileId']
        self.download_path = config['sonarr']['download_path']
        self.library = self.get_sonarr_library()

        if self.api_key == '<API_KEY>':
            print(colored(' > Please set an API key for Sonarr.'))
            exit(0)

    def show_lookup_tvdb(self, id):
        data = None
        try:
            url = 'http://' + self.host + '/api/series/lookup?term=tvdb:' + str(id) + '&apikey=' + self.api_key
            data = requests.get(url).json()
        except:
           pass

        return data[0]

    def verify_if_show_in_radarr(self, slug):
        for item in self.library:
            if item['titleSlug'] == slug:
                return True

        return False

    def get_sonarr_library(self):
        url = 'http://' + self.host + '/api/series?&apikey=' + self.api_key
        data = requests.get(url).json()
        return data

    def add_show_to_sonarr(self, show):

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            "title": show['title'],
            "qualityProfileId": str(self.profileId),
            "titleslug": show['titleSlug'],
            "monitored": "true",
            "images": show['images'],
            "tvdbId": show['tvdbId'],
            "seasons": show['seasons'],
            "year": show['year'],
            "rootFolderPath": str(self.download_path),
            "addOptions": {
                "searchForMissingEpisodes": self.auto_download
            }
        }

        url = 'http://' + self.host + '/api/series?apikey=' + self.api_key
        request = Request(url, data=json.dumps(data).encode(), headers=headers)
        urlopen(request).read()

