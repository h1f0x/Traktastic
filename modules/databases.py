from termcolor import colored
import sqlite3
import os
import yaml
import arrow
import datetime


class Databases:

    def __init__(self):
        self.load_config()

    def close_connections(self):
        self.plex_connection.close()
        self.traktastic_connection.close()

    def load_config(self):
        file = open('./config/config.yaml', 'r')
        config = yaml.load(file, Loader=yaml.FullLoader)
        self.plex_database_path = config['databases']['plex_database_path']
        self.traktastic_database_path = config['databases']['traktastic_database_path']

    def init(self):

        (head, tail) = os.path.split(self.traktastic_database_path)

        if not os.path.exists(head):
            os.makedirs(head)

        try:
            self.plex_connection = sqlite3.connect(database=self.plex_database_path)
            self.plex_cursor = self.plex_connection.cursor()
        except:
            text = ' > Plex database could not be connected at location "%s", please update config file!' % self.plex_database_path
            print(colored(text, 'red'))
            exit(0)

        try:
            self.traktastic_connection = sqlite3.connect(database=self.traktastic_database_path)
            self.traktastic_cursor = self.traktastic_connection.cursor()
        except:
            text = ' > Traktastic database could not be connected at location "%s", please update config file!' % self.traktastic_database_path
            print(colored(text, 'red'))
            exit(0)

        # Traktasic Account Table
        query = '''CREATE TABLE IF NOT EXISTS "main"."accounts" (
                        "plex_id"	INTEGER,
                        "plex_username"	TEXT,
                        "trakt_username" TEXT,
                        "trakt_oauth"	TEXT,
                        "trakt_client_id"	TEXT,
                        "trakt_client_secret"	TEXT,
                        "directory_tv"	TEXT,
                        "directory_movie"	TEXT,
                        "active"	INTEGER
                    );'''
        self.traktastic_cursor.execute(query)
        self.traktastic_connection.commit()

        query = '''CREATE TABLE IF NOT EXISTS "main"."recommendations" (
                        "plex_username"	TEXT,
                        "type"	TEXT,
                        "exists"	INTEGER,
                        "title"	TEXT,
                        "agent_id"	INTEGER,
                        "path"	TEXT
                    );'''
        self.traktastic_cursor.execute(query)
        self.traktastic_connection.commit()

        query = '''CREATE TABLE IF NOT EXISTS "main"."mapping" (
                        "plex_id"	INTEGER,
                        "type"	TEXT,
                        "library_id"	INTEGER
                    );'''
        self.traktastic_cursor.execute(query)
        self.traktastic_connection.commit()

        query = '''CREATE TABLE IF NOT EXISTS "updates" (
                        "plex_id"	INTEGER,
                        "last_tv_update"	INTEGER,
                        "last_movie_update"	INTEGER
                    )'''
        self.traktastic_cursor.execute(query)
        self.traktastic_connection.commit()

    def set_traktastic_user_active(self, id):
        query = '''UPDATE "main"."accounts" SET "active" = 1 WHERE "plex_id" = ?'''
        self.traktastic_cursor.execute(query, (id,))
        self.traktastic_connection.commit()

    def set_traktastic_user_inactive(self, id):
        query = '''UPDATE "main"."accounts" SET "active" = 0 WHERE "plex_id" = ?'''
        self.traktastic_cursor.execute(query, (id,))
        self.traktastic_connection.commit()

    def get_plex_user_id(self, plex_username):
        query = 'SELECT id,name FROM accounts WHERE name = ?'
        self.plex_cursor.execute(query, (plex_username,))
        user = self.plex_cursor.fetchone()
        return user[0]

    def get_plex_users(self):
        query = '''SELECT id,name FROM accounts ORDER BY id ASC;'''
        self.plex_cursor.execute(query)
        users = self.plex_cursor.fetchall()
        return users

    def get_plex_movie_base_path(self, id):
        query = 'SELECT id FROM metadata_items WHERE guid LIKE ? AND metadata_type = 1'
        self.plex_cursor.execute(query, ('%//' + str(id) + '%',))
        metadata_items_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT id FROM media_items WHERE metadata_item_id = ?'
        self.plex_cursor.execute(query, (metadata_items_id,))
        media_items_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT directory_id FROM media_parts WHERE media_item_id = ?'
        self.plex_cursor.execute(query, (media_items_id,))
        media_parts_directory_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT parent_directory_id, path FROM directories WHERE id = ?'
        self.plex_cursor.execute(query, (media_parts_directory_id,))
        directories_result = self.plex_cursor.fetchone()
        directories_result_parent_directory_id = directories_result[0]
        movie_folder_path = directories_result[1]

        query = 'SELECT library_section_id FROM directories WHERE id = ?'
        self.plex_cursor.execute(query, (directories_result_parent_directory_id,))
        directories_result_library_section_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT root_path FROM section_locations WHERE library_section_id = ?'
        self.plex_cursor.execute(query, (directories_result_library_section_id,))
        section_folder_path = self.plex_cursor.fetchone()[0]

        location = os.path.join(section_folder_path, movie_folder_path)
        return location

    def get_plex_tv_show_base_path(self, id):
        query = 'SELECT id FROM metadata_items WHERE guid LIKE ? AND metadata_type = 4 LIMIT 1'
        self.plex_cursor.execute(query, ('%//' + str(id) + '%',))
        metadata_items_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT id FROM media_items WHERE metadata_item_id = ?'
        self.plex_cursor.execute(query, (metadata_items_id,))
        media_items_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT directory_id FROM media_parts WHERE media_item_id = ?'
        self.plex_cursor.execute(query, (media_items_id,))
        media_parts_directory_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT parent_directory_id FROM directories WHERE id = ?'
        self.plex_cursor.execute(query, (media_parts_directory_id,))
        media_parts_parent_directory_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT parent_directory_id, path FROM directories WHERE id = ?'
        self.plex_cursor.execute(query, (media_parts_parent_directory_id,))
        directories_result = self.plex_cursor.fetchone()
        directories_result_parent_directory_id = directories_result[0]
        movie_folder_path = directories_result[1]

        query = 'SELECT library_section_id FROM directories WHERE id = ?'
        self.plex_cursor.execute(query, (directories_result_parent_directory_id,))
        directories_result_library_section_id = self.plex_cursor.fetchone()[0]

        query = 'SELECT root_path FROM section_locations WHERE library_section_id = ?'
        self.plex_cursor.execute(query, (directories_result_library_section_id,))
        section_folder_path = self.plex_cursor.fetchone()[0]

        location = os.path.join(section_folder_path, movie_folder_path)
        return location

    def get_watched_plex_tv_shows(self, plex_id):
        query = 'SELECT "id", "guid", "view_count", "last_viewed_at" FROM "main"."metadata_item_settings" WHERE "account_id"=? AND "view_count">0  AND "guid" LIKE "%thetvdb%"'
        self.plex_cursor.execute(query, (plex_id,))
        shows = self.plex_cursor.fetchall()
        return shows

    def get_watched_plex_movies(self, plex_id):
        query = 'SELECT "id", "guid", "view_count", "last_viewed_at" FROM "main"."metadata_item_settings" WHERE "account_id"=? AND "view_count">0  AND "guid" LIKE "%imdb%"'
        self.plex_cursor.execute(query, (plex_id,))
        movies = self.plex_cursor.fetchall()
        return movies

    def get_traktastic_users(self):
        query = '''SELECT * FROM "main"."accounts"'''
        self.traktastic_cursor.execute(query)
        users = self.traktastic_cursor.fetchall()
        return users

    def get_traktastic_active_users(self):
        query = '''SELECT * FROM "main"."accounts" WHERE "active" = 1'''
        self.traktastic_cursor.execute(query)
        users = self.traktastic_cursor.fetchall()
        return users

    def get_traktastic_cached_existing_movie_recommendations(self, plex_username):
        query = '''SELECT * FROM "main"."recommendations" WHERE "plex_username" = ? AND "exists" = 1 AND "type" = "movie"'''
        self.traktastic_cursor.execute(query, (plex_username,))
        movies = self.traktastic_cursor.fetchall()
        return movies

    def get_traktastic_cached_missing_movie_recommendations(self, plex_username):
        query = '''SELECT * FROM "main"."recommendations" WHERE "plex_username" = ? AND "exists" = 0 AND "type" = "movie"'''
        self.traktastic_cursor.execute(query, (plex_username,))
        movies = self.traktastic_cursor.fetchall()
        return movies

    def get_traktastic_cached_existing_tv_recommendations(self, plex_username):
        query = '''SELECT * FROM "main"."recommendations" WHERE "plex_username" = ? AND "exists" = 1 AND "type" = "tv"'''
        self.traktastic_cursor.execute(query, (plex_username,))
        tv = self.traktastic_cursor.fetchall()
        return tv

    def get_traktastic_cached_missing_tv_recommendations(self, plex_username):
        query = '''SELECT * FROM "main"."recommendations" WHERE "plex_username" = ? AND "exists" = 0 AND "type" = "tv"'''
        self.traktastic_cursor.execute(query, (plex_username,))
        tv = self.traktastic_cursor.fetchall()
        return tv

    def get_traktastic_mapped_library_id(self, plex_id, type):
        query = '''SELECT "library_id" FROM "main"."mapping" WHERE "plex_id" = ? AND "type" = ?;'''
        self.traktastic_cursor.execute(query, (plex_id, type,))
        library_id = self.traktastic_cursor.fetchone()
        return library_id

    def get_traktastic_last_tv_show_sync_time(self, plex_id):
        query = '''SELECT "last_tv_update" FROM "main"."updates" WHERE "plex_id" = ?'''
        self.traktastic_cursor.execute(query, (plex_id,))
        last_update = self.traktastic_cursor.fetchone()

        if last_update != None:
            if last_update[0] != None:
                return last_update[0]
            else:
                return 0
        else:
            return 0

    def get_traktastic_last_movie_sync_time(self, plex_id):
        query = '''SELECT "last_movie_update" FROM "main"."updates" WHERE "plex_id" = ?'''
        self.traktastic_cursor.execute(query, (plex_id,))
        last_update = self.traktastic_cursor.fetchone()

        if last_update != None:
            if last_update[0] != None:
                return last_update[0]
            else:
                return 0
        else:
            return 0

    def create_traktastic_user(self, account):
        print(' > Creating new link for Traktastic acccount: %s..' % account['plex_username'])
        query = '''INSERT INTO "main"."accounts"(
                                "plex_id","plex_username","trakt_username","trakt_oauth","trakt_client_id","trakt_client_secret","directory_tv","directory_movie","active","last_run"
                                ) VALUES (
                                ?,?,?,?,?,?,?,?,?,NULL
                                );'''

        self.traktastic_cursor.execute(query, (
            int(account['plex_id']), account['plex_username'], account['trakt_username'], account['trakt_oauth'], account['trakt_client_id'], account['trakt_client_secret'], account['directory_tv'], account['directory_movie'], account['active']))
        self.traktastic_connection.commit()

        text = ' > Successfully linked Plex user (%s) with Trakt.tv user (%s)!' % (
            account['plex_username'], account['trakt_username'])
        print(colored(text, 'green'))

    def update_traktastic_user(self, account):
        text = ' > Updating existsing Traktastic account: %s..' % account['plex_username']
        print(colored(text, 'yellow'))
        query = '''UPDATE "main"."accounts" SET
                                "plex_username" = ?,"trakt_username" = ?,"trakt_oauth" = ?,"trakt_client_id" = ?,"trakt_client_secret" = ?,"directory_tv" = ?,"directory_movie" = ?
                                WHERE "plex_id" = ?;'''

        self.traktastic_cursor.execute(query, (
            account['plex_username'], account['trakt_username'], account['trakt_oauth'], account['trakt_client_id'], account['trakt_client_secret'], account['directory_tv'], account['directory_movie'], int(account['plex_id'])))
        self.traktastic_connection.commit()

    def update_traktastic_user_recommendations(self,plex_username, items, type):
        query = '''DELETE FROM "main"."recommendations" WHERE "plex_username" = ? AND "type" = ?'''
        self.traktastic_cursor.execute(query, (plex_username, type))
        self.traktastic_connection.commit()


        query = '''INSERT INTO "main"."recommendations"(
                                "plex_username", "type", "exists", "title", "agent_id", "path"
                                ) VALUES (
                                ?,?,?,?,?,?
                                );'''

        for item in items:
            if item.plex == True:
                exists = 1
                path = item.location
            else:
                exists = 0
                path = ""

            if item.type == 'movie':
                agent_id = item.ids['ids']['imdb']
            elif item.type == 'tv':
                agent_id = item.ids['ids']['tvdb']
            else:
                agent_id = ""

            self.traktastic_cursor.execute(query, (
                plex_username, item.type, exists, item.title, agent_id, path
            ))
            self.traktastic_connection.commit()

    def update_traktastic_users_plex_library_id(self, plex_id, type, library_id):
        query = '''INSERT INTO "main"."mapping"(
                            "plex_id", "type", "library_id"
                        ) VALUES (
                            ?,?,?
                        );'''

        self.traktastic_cursor.execute(query, (
           int(plex_id), type, int(library_id)))
        self.traktastic_connection.commit()

    def update_traktastic_last_tv_show_sync_time(self, plex_id):
        query = '''SELECT * FROM "main"."updates" WHERE "plex_id" = ?'''
        self.traktastic_cursor.execute(query, (plex_id,))
        exists = self.traktastic_cursor.fetchone()

        current_time = arrow.utcnow().timestamp

        if exists != None:
            query = '''UPDATE "main"."updates" SET "last_tv_update" = ? WHERE "plex_id" = ?;'''
            self.traktastic_cursor.execute(query, (current_time, plex_id,))
            self.traktastic_connection.commit()

        else:
            query = '''INSERT INTO "main"."updates"(
                                "plex_id", "last_tv_update"
                            ) VALUES (
                                ?,?);'''
            self.traktastic_cursor.execute(query,(int(plex_id), current_time,))
            self.traktastic_connection.commit()

    def update_traktastic_last_movie_sync_time(self, plex_id):
        query = '''SELECT * FROM "main"."updates" WHERE "plex_id" = ?'''
        self.traktastic_cursor.execute(query, (plex_id,))
        exists = self.traktastic_cursor.fetchone()

        current_time = arrow.utcnow().timestamp

        if exists != None:
            query = '''UPDATE "main"."updates" SET "last_movie_update" = ? WHERE "plex_id" = ?;'''
            self.traktastic_cursor.execute(query, (current_time, plex_id,))
            self.traktastic_connection.commit()

        else:
            query = '''INSERT INTO "main"."updates"(
                                "plex_id", "last_movie_update"
                            ) VALUES (
                                ?,?);'''
            self.traktastic_cursor.execute(query,(int(plex_id), current_time,))
            self.traktastic_connection.commit()

    def update_plex_library_section_settings(self, section_id):
        user_fields = 'pr%3AcollectionMode=0&pr%3AincludeInGlobal=0'
        query = '''UPDATE "main"."library_sections" SET
                            "user_fields" = ?
                            WHERE "id" = ?;'''
        self.plex_cursor.execute(query, (user_fields, section_id,))
        self.plex_connection.commit()

    def verify_plex_user_existance(self, plex_username):
        query = 'SELECT id,name FROM accounts WHERE name = ?'
        self.plex_cursor.execute(query, (plex_username,))
        user = self.plex_cursor.fetchone()

        if user == None:
            text = ' > Plex user "%s" does not exist' % plex_username
            print(colored(text, 'yellow'))
            return False
        else:
            if user[1] == plex_username:
                return True
            else:
                print(' > An Error has occourd.')
                return False

    def verify_traktastic_user_library_mapping(self, plex_id, type):
        query = '''SELECT * FROM "main"."mapping" WHERE "plex_id" = ? AND "type" = ?'''
        self.traktastic_cursor.execute(query, (plex_id, type,))
        libs = self.traktastic_cursor.fetchall()

        if len(libs) > 0:
            return True
        else:
            return False

    def verify_tractastic_user_existance(self, plex_username):
        query = 'SELECT "plex_id", "plex_username" FROM "main"."accounts" WHERE "plex_username" = ?'
        self.traktastic_cursor.execute(query, (plex_username,))
        user = self.traktastic_cursor.fetchone()

        if user == None:
            text = ' > Traktastic user "%s" does not exist' % plex_username
            print(colored(text, 'yellow'))
            return False
        else:
            if user[1] == plex_username:
                return True
            else:
                print(colored(' > An Error has occourd.', 'red'))
                return False

    def verify_plex_item_availablity(self, id):
        query = 'SELECT "id" FROM "main"."metadata_items" WHERE "guid" LIKE ?'
        self.plex_cursor.execute(query, ('%//' + str(id) + '%',))
        item = self.plex_cursor.fetchone()

        if item == None:
            return False
        else:
            return True

    def delete_traktastic_user(self, plex_id):
        query = 'DELETE FROM "main"."accounts" WHERE "plex_id"=?'
        self.traktastic_cursor.execute(query, (int(plex_id),))
        self.traktastic_connection.commit()

    def delete_traktastic_mapped_library_id(self, library_id):
        query = '''DELETE FROM "main"."mapping" WHERE "library_id" = ?;'''
        self.traktastic_cursor.execute(query, (int(library_id),))
        self.traktastic_connection.commit()
