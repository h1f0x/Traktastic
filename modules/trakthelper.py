import requests
import json
from urllib.request import Request, urlopen


class Trakthelper:

    def __init__(self, oauth, cliend_id, client_secret):
        self.content_type = 'application/json'
        self.trakt_api_version = '2'
        self.trakt_oauth = oauth
        self.trakt_cliend_id = cliend_id
        self.trakt_client_secret = client_secret

    def tv_show_id_lookup(self, show_id):
        headers = {
            'Content-Type': self.content_type,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/search/tvdb/' + show_id
        data = requests.get(url, headers=headers).json()
        return data[0]['show']

    def movie_id_lookup(self, movie_id):
        headers = {
            'Content-Type': self.content_type,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/search/imdb/' + movie_id
        data = requests.get(url, headers=headers).json()
        return data[0]['movie']

    def get_tv_show_ext_full(self, ext_full):
        headers = {
            'Content-Type': self.content_type,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/' + ext_full
        data = requests.get(url, headers=headers).json()
        return data

    def get_movie_ext_full(self, ext_full):
        headers = {
            'Content-Type': self.content_type,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/' + ext_full
        data = requests.get(url, headers=headers).json()
        return data

    def get_hidden_recommendations(self):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/users/hidden/recommendations'
        data = requests.get(url, headers=headers).json()
        return data

    def get_tv_show_progress(self, trakt_id):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/shows/' + trakt_id + '/progress/watched'
        data = requests.get(url, headers=headers).json()
        return data

    def get_watched_movies(self, user_id):
        headers = {
            'Content-Type': self.content_type,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/users/' + user_id + '/watched/movies'
        data = requests.get(url, headers=headers).json()
        return data

    def update_watched_tv_shows(self, shows):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        values = {
            "shows": shows
        }

        request = Request('https://api.trakt.tv/sync/history', data=json.dumps(values).encode(), headers=headers)
        urlopen(request).read()

    def update_watched_movies(self, movies):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        values = {
            "movies": movies
        }

        request = Request('https://api.trakt.tv/sync/history', data=json.dumps(values).encode(), headers=headers)
        urlopen(request).read()

    def hide_tv_show_recommendations(self, trakt_id):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/recommendations/shows/' + trakt_id
        request = Request(url, headers=headers)
        request.get_method = lambda: 'DELETE'
        urlopen(request).read()

    def hide_movie_recommendations(self, trakt_id):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        url = 'https://api.trakt.tv/recommendations/movies/' + trakt_id
        request = Request(url, headers=headers)
        request.get_method = lambda: 'DELETE'
        urlopen(request).read()

    def delete_hidden_recommendations(self, values):
        headers = {
            'Content-Type': self.content_type,
            'Authorization': 'Bearer ' + self.trakt_oauth,
            'trakt-api-version': self.trakt_api_version,
            'trakt-api-key': self.trakt_cliend_id
        }

        request = Request('https://api.trakt.tv/users/hidden/recommendations/remove', data=json.dumps(values).encode(), headers=headers)
        urlopen(request).read()
