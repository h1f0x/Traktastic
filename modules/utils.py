from prettytable import PrettyTable
from termcolor import colored
import trakt
import os
import yaml

trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH


class Utils:

    def __init__(self, databases):
        self.databases = databases
        self.load_config()

    def load_config(self):
        file = open('./config/config.yaml', 'r')
        config = yaml.load(file, Loader=yaml.FullLoader)

        self.trakt_application_id = config['trakt']['application']
        self.trakt_client_id = config['trakt']['client_id']
        self.trakt_client_secret = config['trakt']['client_secret']
        self.libraries_base_path = config['filesystem']['libraries_base_path']

        trakt.APPLICATION_ID = self.trakt_application_id

    def list_plex_users(self):
        users = self.databases.get_plex_users()

        table = PrettyTable()
        table.field_names = ['Plex ID', 'Plex Username']
        table.align['Plex ID'] = 'l'
        table.align['Plex Username'] = 'l'

        for user in users:
            if int(user[0]) != 0:
                table.add_row([user[0], user[1]])

        print(table)

    def list_traktastic_users(self):
        users = self.databases.get_traktastic_users()

        table = PrettyTable()
        table.field_names = ['Plex Username', 'Trakt.tv Username', 'TV Directory', 'Movie Directory',
                             'Active']

        table.align['Plex Username'] = 'l'
        table.align['Trakt.tv Username'] = 'l'
        table.align['TV Directory'] = 'l'
        table.align['Movie Directory'] = 'l'

        for user in users:
            if user[8] == 1:
                active = colored('✔', 'green')
            else:
                active = ''

            table.add_row([user[1], user[2], user[6], user[7], active])

        print(table)

    def list_tv_recommendations(self, shows):
        table = PrettyTable()
        table.field_names = ['TV-Show', 'Release Year', 'Rating', 'Votes', 'On Plex', 'Location']

        table.align['TV-Show'] = 'l'
        table.align['Release Year'] = 'l'
        table.align['Rating'] = 'l'
        table.align['Votes'] = 'l'
        table.align['Location'] = 'l'

        for show in shows:
            plex_availablity = ""
            if show.plex == True:
                plex_availablity = colored('✔', 'green')
                
            if hasattr(show,'location'):
                plex_location = show.location
            else:
                plex_location = ""

            table.add_row([show.title, show.year, show.ratings['rating'], show.ratings['votes'], plex_availablity, plex_location])

        print(table)

    def list_movies_recommendations(self, movies):
        table = PrettyTable()
        table.field_names = ['Movie', 'Release Year', 'Rating', 'Votes', 'On Plex', 'Location']

        table.align['Movie'] = 'l'
        table.align['Release Year'] = 'l'
        table.align['Rating'] = 'l'
        table.align['Votes'] = 'l'
        table.align['Location'] = 'l'

        for movie in movies:
            plex_availablity = ""
            if movie.plex == True:
                plex_availablity = colored('✔', 'green')

            if hasattr(movie,'location'):
                plex_location = movie.location
            else:
                plex_location = ""

            table.add_row([movie.title, movie.year, movie.ratings['rating'], movie.ratings['votes'], plex_availablity, plex_location])

        print(table)

    def link_user(self, plex_username):
        account = {}
        account['plex_id'] = self.databases.get_plex_user_id(plex_username)
        account['plex_username'] = plex_username
        account['directory_tv'] = os.path.join(self.libraries_base_path, plex_username, 'tv')
        account['directory_movie'] = os.path.join(self.libraries_base_path, plex_username, 'movie')
        account['active'] = 1

        account['trakt_username'] = input('Trakt.tv username: ')
        trakt.init(account['trakt_username'], client_id=self.trakt_client_id, client_secret=self.trakt_client_secret)

        account['trakt_oauth'] = trakt.core.OAUTH_TOKEN
        account['trakt_client_id'] = trakt.core.CLIENT_ID
        account['trakt_client_secret'] = trakt.core.CLIENT_SECRET

        if self.databases.verify_tractastic_user_existance(plex_username):
            self.databases.update_traktastic_user(account)

        else:
            self.databases.create_traktastic_user(account)

    def unlink_user(self, plex_username):
        plex_id = self.databases.get_plex_user_id(plex_username)
        self.databases.delete_traktastic_user(plex_id)
        print(' > Successfully unlinked Plex account (%s)!' % (plex_username))

    def verify_plex_item_availablity(self, item):
        existing = self.databases.verify_plex_item_availablity(item)
        print(existing)
