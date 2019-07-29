from modules.trakthelper import Trakthelper
from modules.plexhelper import Plexhelper
from modules.radarrhelper import Radarrhelper
from modules.sonarrhelper import Sonarrhelper
from prettytable import PrettyTable
from termcolor import colored
import trakt
import trakt.tv
import trakt.movies
import re
import yaml
import os
import shutil
import arrow
import datetime


class Account:

    def __init__(self, databases, plex_username):
        self.databases = databases
        self.fetch_account_data(plex_username)
        self.load_trakthelper()
        self.load_config()

    def load_config(self):
        file = open('./config/config.yaml', 'r')
        config = yaml.load(file, Loader=yaml.FullLoader)
        self.tv_genre_blacklist = config['trakt']['tv_genre_blacklist']
        self.tv_year_before_blacklist = config['trakt']['tv_year_before_blacklist']
        self.tv_max_related_shows = config['trakt']['tv_max_related_shows']
        self.tv_seen_threshold = config['trakt']['tv_seen_threshold']
        self.movie_genre_blacklist = config['trakt']['movie_genre_blacklist']
        self.movie_year_before_blacklist = config['trakt']['movie_year_before_blacklist']
        self.movie_max_related_movies = config['trakt']['movie_max_related_movies']
        self.libraries_base_path = config['filesystem']['libraries_base_path']
        self.libraries_user_path = os.path.join(self.libraries_base_path, self.plex_username)
        self.libraries_user_tv_path = os.path.join(self.libraries_user_path, 'tv')
        self.libraries_user_movie_path = os.path.join(self.libraries_user_path, 'movies')
        self.auto_plex_library = config['plex']['auto_library']
        self.radarr_auto_download = config['radarr']['auto_download']

    def fetch_account_data(self, plex_username):
        query = '''SELECT * FROM "main"."accounts" WHERE "plex_username"=?'''
        self.databases.traktastic_cursor.execute(query, (plex_username,))
        account = self.databases.traktastic_cursor.fetchone()
        self.plex_id = account[0]
        self.plex_username = account[1]
        self.trakt_username = account[2]
        self.trakt_oauth = account[3]
        self.trakt_client_id = account[4]
        self.trakt_client_secret = account[5]
        self.directory_tv = account[6]
        self.directory_movie = account[7]
        self.active = account[8]
        self.last_update = account[9]

    def load_trakthelper(self):
        self.trakthelper = Trakthelper(self.trakt_oauth, self.trakt_client_id, self.trakt_client_secret)

    def set_trakt_settings(self):
        trakt.core.OAUTH_TOKEN = self.trakt_oauth
        trakt.core.CLIENT_ID = self.trakt_client_id
        trakt.core.CLIENT_SECRET = self.trakt_client_secret

    def set_active(self):
        self.databases.set_traktastic_user_active(self.plex_id)

    def set_inactive(self):
        self.databases.set_traktastic_user_inactive(self.plex_id)

    def get_watched_plex_tv_shows(self):

        last_update = self.databases.get_traktastic_last_tv_show_sync_time(self.plex_id)

        shows = self.databases.get_watched_plex_tv_shows(self.plex_id)

        self.databases.update_traktastic_last_tv_show_sync_time(self.plex_id)

        data = []

        for show in shows:
            identifier = show[1][29:].split('?lang')[0]
            if re.match(r".*\/.\/.*", identifier):
                tmp = {}
                tmp['identifier'] = identifier.split('/')

                dates = show[3].split(' ')
                date = dates[0].split('-')
                year = int(date[0])
                mon = int(date[1])
                day = int(date[2])

                time = dates[1].split(':')
                hour = int(time[0])
                min = int(time[1])
                sec = int(time[2])

                watched = datetime.datetime(year, mon, day, hour, min, sec)

                tmp['date'] = show[3]
                tmp['compare_date'] = arrow.get(watched).timestamp

                if tmp['compare_date'] > last_update:
                    data.append(tmp)

        u_shows = set()
        for d in data:
            u_shows.add(d['identifier'][0])

        shows = []
        for show in u_shows:
            tmp = {}
            tmp['show_id'] = show
            tmp['seen'] = []
            for d in data:
                if d['identifier'][0] == show:
                    episode = {}
                    episode['season'] = d['identifier'][1]
                    episode['number'] = d['identifier'][2]
                    episode['watched_at'] = d['date']
                    tmp['seen'].append(episode)
            shows.append(tmp)

        for show in shows:
            u_seasons = set()
            show['seasons'] = []
            for episode in show['seen']:
                u_seasons.add(episode['season'])

            for season in u_seasons:
                tmp = {}
                tmp['number'] = int(season)
                tmp['episodes'] = []
                for episode in show['seen']:
                    if season == episode['season']:
                        e = {}
                        e['number'] = int(episode['number'])
                        e['watched_at'] = episode['watched_at']
                        tmp['episodes'].append(e)

                show['seasons'].append(tmp)

            del(show['seen'])

        for show in shows:
            trakt_information = self.trakthelper.tv_show_id_lookup(show['show_id'])
            show['title'] = trakt_information['title'].replace("'", "")
            show['year'] = trakt_information['year']
            show['ids'] = trakt_information['ids']
            del(show['show_id'])

        return shows

    def get_watched_plex_movies(self):

        last_update = self.databases.get_traktastic_last_movie_sync_time(self.plex_id)

        movies = self.databases.get_watched_plex_movies(self.plex_id)

        self.databases.update_traktastic_last_movie_sync_time(self.plex_id)

        values = []

        for movie in movies:
            identifier = movie[1][26:].split('?lang')[0]

            trakt_information = self.trakthelper.movie_id_lookup(identifier)
            trakt_information['watched_at'] = movie[3]
            trakt_information['title'] = trakt_information['title'].replace("'", "")

            dates = movie[3].split(' ')
            date = dates[0].split('-')
            year = int(date[0])
            mon = int(date[1])
            day = int(date[2])

            time = dates[1].split(':')
            hour = int(time[0])
            min = int(time[1])
            sec = int(time[2])

            watched = datetime.datetime(year, mon, day, hour, min, sec)

            if arrow.get(watched).timestamp > last_update:
                values.append(trakt_information)

        return values

    def get_tv_recommendations(self):
        self.set_trakt_settings()

        running = True
        first_run = False
        overwall_recommendations = list()

        while running == True:
            genre_status = True
            year_status = True
            overwall_recommendations = trakt.tv.get_recommended_shows() + overwall_recommendations

            related_shows = []
            if first_run == False:
                for show in overwall_recommendations:
                    related = show.related
                    filtered_related = set()

                    for rel in related:
                        progess = self.trakthelper.get_tv_show_progress(str(rel.ids['ids']['trakt']))
                        percentage = (progess['aired'] / 100) * progess['completed']

                        if percentage <= int(self.tv_seen_threshold):
                            filtered_related.add(rel)

                    tv_max_related_shows = 0
                    filtered_related = list(filtered_related)
                    while tv_max_related_shows <= self.tv_max_related_shows-1:
                        related_shows.append(filtered_related[tv_max_related_shows])
                        tv_max_related_shows += 1

                overwall_recommendations = overwall_recommendations + related_shows

            to_be_removed = set()
            for rec in overwall_recommendations:
                show = self.trakthelper.get_tv_show_ext_full(rec.ext_full)
                for genre in show['genres']:
                    for blacklist_genre in self.tv_genre_blacklist:
                        if genre == blacklist_genre:
                            to_be_removed.add(rec)
                            genre_status = False
                try:
                    if show['year'] < self.tv_year_before_blacklist:
                        to_be_removed.add(rec)
                        year_status = False
                except:
                    to_be_removed.add(rec)
                    year_status = False

            for item in list(to_be_removed):
                overwall_recommendations.remove(item)

            for show in to_be_removed:
                self.trakthelper.hide_tv_show_recommendations(str(show.ids['ids']['trakt']))

            if genre_status == True and year_status == True:
                running = False

            first_run = True

        duplicated_recommendations = set()
        final_recommendations = []

        for show in overwall_recommendations:
            if show.votes != 0 and show.rating != 0.0:
                if show.title not in duplicated_recommendations:
                    show.type = 'tv'
                    show.plex = self.databases.verify_plex_item_availablity(show.ids['ids']['tvdb'])

                    if show.plex == True:
                        show.location = self.databases.get_plex_tv_show_base_path(show.ids['ids']['tvdb'])

                    final_recommendations.append(show)
                    duplicated_recommendations.add(show.title)

        self.databases.update_traktastic_user_recommendations(self.plex_username, final_recommendations, 'tv')

        return final_recommendations

    def get_movie_recommendations(self):
        self.set_trakt_settings()

        running = True
        first_run = False
        overwall_recommendations = list()

        watched_movies = self.trakthelper.get_watched_movies(self.trakt_username)
        watched_movies_ids = []

        for watched_movie in watched_movies:
            watched_movies_ids.append(watched_movie['movie']['ids']['trakt'])

        while running == True:
            genre_status = True
            year_status = True
            overwall_recommendations = trakt.movies.get_recommended_movies() + overwall_recommendations

            related_movies = []
            if first_run == False:
                for movie in overwall_recommendations:
                    related = movie.related
                    movie_max_related_movies = 0
                    while movie_max_related_movies <= self.movie_max_related_movies-1:
                        if related[movie_max_related_movies].ids['ids']['trakt'] not in watched_movies_ids:
                            related_movies.append(related[movie_max_related_movies])
                        movie_max_related_movies += 1

                overwall_recommendations = overwall_recommendations + related_movies

            to_be_removed = set()
            for rec in overwall_recommendations:
                movie = self.trakthelper.get_movie_ext_full(rec.ext_full)
                for genre in movie['genres']:
                    for blacklist_genre in self.movie_genre_blacklist:
                        if genre == blacklist_genre:
                            to_be_removed.add(rec)
                            genre_status = False
                try:
                    if movie['year'] < self.movie_year_before_blacklist:
                        to_be_removed.add(rec)
                        year_status = False
                except:
                    to_be_removed.add(rec)
                    year_status = False

            for item in list(to_be_removed):
                overwall_recommendations.remove(item)

            for movie in to_be_removed:
                self.trakthelper.hide_movie_recommendations(str(movie.ids['ids']['trakt']))

            if genre_status == True and year_status == True:
                running = False

            first_run = True

        duplicated_recommendations = set()
        final_recommendations = []

        for movie in overwall_recommendations:
            if movie.title not in duplicated_recommendations:
                movie.type = 'movie'
                movie.plex = self.databases.verify_plex_item_availablity(movie.ids['ids']['imdb'])

                if movie.plex == True:
                    movie.location = self.databases.get_plex_movie_base_path(movie.ids['ids']['imdb'])

                final_recommendations.append(movie)
                duplicated_recommendations.add(movie.title)

        self.databases.update_traktastic_user_recommendations(self.plex_username, final_recommendations, 'movie')

        return final_recommendations

    def update_watched_tv_shows(self):
        watched = self.get_watched_plex_tv_shows()
        self.trakthelper.update_watched_tv_shows(watched)

    def update_watched_movies(self):
        watched = self.get_watched_plex_movies()
        self.trakthelper.update_watched_movies(watched)

    def create_user_movie_recommendations_library(self):
        existing_movies = self.databases.get_traktastic_cached_existing_movie_recommendations(self.plex_username)

        if len(existing_movies) == 0:
            return False

        if not os.path.exists(self.libraries_user_movie_path):
            os.makedirs(self.libraries_user_movie_path)

        self.unlink_library_symlinks(self.libraries_user_movie_path)

        for movie in existing_movies:
            (head, tail) = os.path.split(movie[5])
            os.symlink(movie[5], os.path.join(self.libraries_user_movie_path, tail))

        if self.auto_plex_library == True:
            absolut_library_path = os.path.abspath(self.libraries_user_movie_path)

            plex_server = Plexhelper(self.databases)
            plex_server.create_library_for_specific_user(self, absolut_library_path, 'movie')

        return True

    def create_user_tv_recommendations_library(self):
        existing_tv = self.databases.get_traktastic_cached_existing_tv_recommendations(self.plex_username)

        if len(existing_tv) == 0:
            return False

        if not os.path.exists(self.libraries_user_tv_path):
            os.makedirs(self.libraries_user_tv_path)

        self.unlink_library_symlinks(self.libraries_user_tv_path)

        for tv in existing_tv:
            (head, tail) = os.path.split(tv[5])
            os.symlink(tv[5], os.path.join(self.libraries_user_tv_path, tail))

        if self.auto_plex_library == True:
            absolut_library_path = os.path.abspath(self.libraries_user_tv_path)

            plex_server = Plexhelper(self.databases)
            plex_server.create_library_for_specific_user(self, absolut_library_path, 'show')

        return True

    def delete_hidden_recommendations(self):
        hidden_recommendations = self.trakthelper.get_hidden_recommendations()

        movies = []
        shows = []

        for rec in hidden_recommendations:
            if rec['type'] == 'show':
                shows.append(rec['show'])
            if rec['type'] == 'movie':
                movies.append(rec['movie'])

        values = {
            "movies": movies,
            "shows": shows
        }

        self.trakthelper.delete_hidden_recommendations(values)

    def delete_user_recommendation_libraries(self):

        if self.auto_plex_library == True:
            plex_server = Plexhelper(self.databases)
            plex_server.delete_library_for_specific_user(self, 'show')
            plex_server.delete_library_for_specific_user(self, 'movie')

        if os.path.exists(self.libraries_user_tv_path):
            self.unlink_library_symlinks(self.libraries_user_tv_path)

        if os.path.exists(self.libraries_user_movie_path):
            self.unlink_library_symlinks(self.libraries_user_movie_path)

        shutil.rmtree(self.libraries_user_path, ignore_errors=True)

    def unlink_library_symlinks(self, path):
        links = [f.path for f in os.scandir(path) if f.is_dir()]
        for link in links:
            os.unlink(link)

    def add_missing_movies_to_radarr(self, spinner, hidden):
        missing_movies = self.databases.get_traktastic_cached_missing_movie_recommendations(self.plex_username)

        radarr = Radarrhelper()

        to_download= []
        download_need = True

        for movie in missing_movies:
            lookup = radarr.movie_lookup_imdb(movie[4])
            tmp = {}
            tmp['title'] = movie[3]
            tmp['imdbId'] = movie[4]
            tmp['status'] = ''
            tmp['added'] = ''
            tmp['download'] = False

            if lookup != None:
                tmp['status'] = colored('✔', 'green')
                tmp['data'] = lookup

                in_radarr = radarr.verify_if_movie_in_radarr(lookup['titleSlug'])

                if in_radarr:
                    tmp['added'] = colored('✔', 'green')
                    tmp['download'] = False
                else:
                    download_need = True

            to_download.append(tmp)

        table = PrettyTable()

        table.field_names = ['Movie Title', 'imdbId', 'Radarr Lookup', 'Already added?']
        table.align['Movie Title'] = 'l'

        for download in to_download:
            table.add_row([download['title'], download['imdbId'], download['status'], download['added']])

        spinner.stop()

        if hidden == False:
            print(table)

            if download_need:
                proceed = input('Add missing movies to Radarr? [Yes|No]: ')

                if proceed == "Yes" or proceed == "No":
                    if proceed == "Yes":
                        spinner.text = 'Adding movies to Radarr..'
                        spinner.start()

                        for movie in to_download:
                            if movie['download']:
                                radarr.add_movie_to_radarr(movie['data'])

                        spinner.text = 'Added all movies to Radarr successfully!'
                        return spinner
                    else:
                        spinner.text = 'No movies added to Radarr.'
                        return spinner
                else:
                    print(colored(' > You entered something wrong.', 'yellow'))
                    spinner.text = 'No movies added to Radarr.'
                    return spinner
            else:
                spinner.text = 'All movies are already in Radarr.'
                return spinner
        else:

            spinner.text = 'Adding movies to Radarr..'
            spinner.start()

            if download_need:
                for movie in to_download:
                    if movie['download']:
                        radarr.add_movie_to_radarr(movie['data'])

                spinner.text = 'Added all missing movies to Radarr successfully!'
                return spinner
            else:
                spinner.text = 'All movies are already in Radarr.'
                return spinner

    def add_missing_tv_shows_to_radarr(self, spinner, hidden):
        missing_shows = self.databases.get_traktastic_cached_missing_tv_recommendations(self.plex_username)

        sonarr = Sonarrhelper()

        to_download = []
        download_need = False

        for show in missing_shows:
            lookup = sonarr.show_lookup_tvdb(show[4])
            tmp = {}
            tmp['title'] = show[3]
            tmp['tvdbId'] = show[4]
            tmp['status'] = ''
            tmp['added'] = ''
            tmp['download'] = True

            if lookup != None:
                tmp['status'] = colored('✔', 'green')
                tmp['data'] = lookup

                in_sonarr = sonarr.verify_if_show_in_radarr(lookup['titleSlug'])

                if in_sonarr:
                    tmp['added'] = colored('✔', 'green')
                    tmp['download'] = False
                else:
                    download_need = True

            to_download.append(tmp)

        table = PrettyTable()

        table.field_names = ['Show Title', 'tvdbId', 'Sonarr Lookup', 'Already added?']
        table.align['Show Title'] = 'l'

        for download in to_download:
            table.add_row([download['title'], download['tvdbId'], download['status'], download['added']])

        spinner.stop()

        if hidden == False:
            print(table)

            if download_need:
                proceed = input('Add missing tv-shows to Sonarr? [Yes|No]: ')

                if proceed == "Yes" or proceed == "No":
                    if proceed == "Yes":
                        spinner.text = 'Adding tv-shows to Sonarr..'
                        spinner.start()

                        for show in to_download:
                            if show['download']:
                                sonarr.add_show_to_sonarr(show['data'])

                        spinner.text = 'Added all tv-shows to Sonarr successfully!'
                        return spinner
                    else:
                        spinner.text = 'No tv-shows added to Sonarr.'
                        return spinner
                else:
                    print(colored(' > You entered something wrong.', 'yellow'))
                    spinner.text = 'No tv-shows added to Sonarr.'
                    return spinner
            else:
                spinner.text = 'All tv-shows are already in Sonarr.'
                return spinner
        else:

            spinner.text = 'Adding movies to Sonarr..'
            spinner.start()

            if download_need:
                for show in to_download:
                    if show['download']:
                        sonarr.add_show_to_sonarr(show['data'])

                spinner.text = 'Added all missing tv-shows to Sonarr successfully!'
                return spinner
            else:
                spinner.text = 'All tv-shows are already in Sonarr.'
                return spinner