from termcolor import colored
from pprint import pprint
import plexapi
import plexapi.myplex
import plexapi.server
import plexapi.library
import yaml
import time
import random
import string


class Plexhelper:

    def __init__(self, databases):
        self.databases = databases
        self.load_config()
        self.init()

    def load_config(self):
        file = open('./config/config.yaml', 'r')
        config = yaml.load(file, Loader=yaml.FullLoader)

        self.plex_username = config['plex']['username']
        self.plex_password = config['plex']['password']
        self.plex_server_id = config['plex']['server']
        self.library_name_movie = config['plex']['library_name_movie']
        self.library_name_tv = config['plex']['library_name_tv']
        self.library_language = config['plex']['library_language']

    def randomString(stringLength=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def init(self):
        self.plex_account = plexapi.myplex.MyPlexAccount(self.plex_username, self.plex_password)
        self.plex_server = self.plex_account.resource(self.plex_server_id).connect()

    def create_library_for_specific_user(self, account, location, type):

        result = self.databases.verify_traktastic_user_library_mapping(account.plex_id, type)

        if result == False:

            library_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])
            library_type = type

            if library_type == 'movie':
                library_agent = 'com.plexapp.agents.imdb'
                library_scanner = 'Plex Movie Scanner'
            elif library_type == 'show':
                library_agent = 'com.plexapp.agents.thetvdb'
                library_scanner = 'Plex Series Scanner'
            else:
                print(colored(' > Outch. An error during library creation happened..'))

            library_location = location
            library_language = self.library_language

            try:
                self.plex_server.library.add(name=library_name, agent=library_agent, type=library_type, scanner=library_scanner, location=library_location, language=library_language)
            except:
                time.sleep(10)

            result = self.search_sections(library_name)

            if result == False:
                print(colored('\n > Oops. Something went wrong, library not found, please visit your Plex Admin Center.', 'yellow'))
                exit(0)
            else:
                section = result[1]

                self.databases.update_traktastic_users_plex_library_id(account.plex_id, type, section.key)

                try:
                    section.edit(agent=section.agent, name=self.library_name_movie)
                except:
                    time.sleep(10)

                user = self.plex_account.user(account.plex_username)
                sections_to_share = []
                sections_to_share.append(section.key)

                for section in user.servers[0].sections():
                    if section.shared ==  True:
                        sections_to_share.append(section.sectionKey)

                self.plex_account.updateFriend(account.plex_username, self.plex_server, sections=sections_to_share)


    def delete_library_for_specific_user(self, account, type):
        library_id = self.databases.get_traktastic_mapped_library_id(account.plex_id, type)

        if library_id != None:
            for section in self.plex_server.library.sections():
                if int(section.key) == int(library_id[0]):
                    try:
                        self.databases.delete_traktastic_mapped_library_id(library_id[0])
                        section.delete()
                    except:
                        time.sleep(10)

    def search_sections(self, library_name):
        sections = self.plex_server.library.sections()

        for section in sections:
            if section.title in library_name:

                return True, section

        return False
