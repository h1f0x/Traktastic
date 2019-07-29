# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Usage:  traktastic.py accounts list [plex]
        traktastic.py accounts link <PlexUsername>
        traktastic.py accounts unlink <PlexUsername>
        traktastic.py accounts <PlexUsername> active
        traktastic.py accounts <PlexUsername> inactive
        traktastic.py update all
        traktastic.py update <PlexUsername> tv
        traktastic.py update <PlexUsername> movies
        traktastic.py recommendations all
        traktastic.py recommendations all reset
        traktastic.py recommendations <PlexUsername> reset
        traktastic.py recommendations <PlexUsername> tv
        traktastic.py recommendations <PlexUsername> movies
        traktastic.py library all
        traktastic.py library <PlexUsername> tv
        traktastic.py library <PlexUsername> movies
        traktastic.py library <PlexUsername> delete
        traktastic.py downloads all [--hidden]
        traktastic.py downloads <PlexUsername> tv [--hidden]
        traktastic.py downloads <PlexUsername> movies [--hidden]

All operations are based on the Plex username of a user.

Commands:
  accounts list [plex]                      List linked accounts [by adding plex - get a list of plex accounts]
  accounts link <PlexUsername>              Link a Plex user account to a Trakt.tv account
  accounts unlink <PlexUsername>            Unlink a Plex user account to a Trakt.tv account
  accounts <PlexUsername> active            To set a registered account active
  accounts <PlexUsername> inactive          To set a registered account inactive

  update all                                Updates all watched histories to Trakt.tv which accounts are active (tv-shows / movies)
  update <PlexUsername> tv                  Updates a specific users tv-show history to Trakt.tv
  update <PlexUsername> movies              Updates a specific users movie history to Trakt.tv

  recommendations all                       Updates Traktastic recommendations table for all active users
  recommendations all reset                 Resets all dismissed tv-shows and movies on Trakt.tv - needed to apply new filter
  recommendations <PlexUsername> reset      Resets dismissed tv-show/movies for a specific user
  recommendations <PlexUsername> tv         Recieve a list of tv-show recommendations for a specific user (updates the Traktastic cached information)
  recommendations <PlexUsername> movies     Recieve a list of movie recommendations for a specific user (updates the Traktastic cached information)

  library all                               Creates custom user libraries based on the recommendations (tv-show/movies) for all users (symlinking) and share on Plex
  library <PlexUsername> tv                 Creates custom user tv-show library based on the recommendations for a specifc user (symlinking) and share on Plex
  library <PlexUsername> movies             Creates custom user movie library based on the recommendations for a specifc user (symlinking) and share on Plex
  library <PlexUsername> delete             Destroys all libraries for a specific users (unlinking, deletion of folder) and deletes them on Plex

  downloads all                             Adds all missing movies and tv-shows to Radarr/Sonarr
  downloads <PlexUsername> tv               Adds all missing tv-shows of specfuc user to Sonarr
  downloads <PlexUsername> movies           Adds all missing movies of specific user to Radarr

Arguments:
  <PlexUsername>        Username which is shown by 'traktastic.py accounts list plex'

Options:
  -h --help
  --hidden              if "--hidden" no table will be printed
"""

from modules.databases import Databases
from modules.utils import Utils
from modules.account import Account
from docopt import docopt
from yaspin import yaspin
from termcolor import colored


def accounts():
    if arguments['link']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_plex_user_existance(plex_username):

            text = "Linking Plex user %s to Trakt.tv profile.." % plex_username
            spinner = yaspin(text=text, color="green")
            spinner.start()
            spinner.ok("✔")
            spinner.stop()

            utils.link_user(plex_username)
        else:
            databases.close_connections()
            exit(0)

    if arguments['unlink']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_plex_user_existance(plex_username):

            text = "Unlinking Plex user %s from Trakt.tv profile.." % plex_username
            spinner = yaspin(text=text, color="green")
            spinner.start()
            spinner.ok("✔")
            spinner.stop()

            utils.unlink_user(plex_username)
        else:
            databases.close_connections()
            exit(0)

    if arguments['list']:
        if arguments['plex']:
            spinner = yaspin(text="Getting all current Plex users..", color="green")
            spinner.start()
            spinner.ok("✔")
            spinner.stop()

            utils.list_plex_users()

        else:
            spinner = yaspin(text="Getting all current Traktastic users..", color="green")
            spinner.start()
            spinner.ok("✔")
            spinner.stop()

            utils.list_traktastic_users()

    if arguments['<PlexUsername>']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_tractastic_user_existance(plex_username):
            account = Account(databases, plex_username)

            if arguments['active']:
                spinner = yaspin(text="Setting account active..", color="green")
                spinner.start()

                account.set_active()

                spinner.text = "Account activated."
                spinner.ok("✔")

            if arguments['inactive']:
                spinner = yaspin(text="Setting account inactive..", color="green")
                spinner.start()

                account.set_inactive()

                spinner.text = "Account deactivated."
                spinner.ok("✔")


def update():
    if arguments['<PlexUsername>']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_tractastic_user_existance(plex_username):
            account = Account(databases, plex_username)

            if arguments['tv']:
                start_text = "Updating Plex user %s watched tv-shows to Trakt.tv.." % plex_username
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                account.update_watched_tv_shows()

                spinner.text = "Plex user %s watched tv-shows successfully updated to Trakt.tv!" % plex_username
                spinner.ok("✔")
                spinner.stop()

            if arguments['movies']:
                start_text = "Updating Plex user %s watched movies to Trakt.tv.." % plex_username
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                account.update_watched_movies()

                spinner.text = "Plex user %s watched movies successfully updated to Trakt.tv!" % plex_username
                spinner.ok("✔")
                spinner.stop()

        else:
            databases.close_connections()
            exit(0)

    if arguments['all']:
        users = databases.get_traktastic_active_users()

        if len(users) == 0:
            print(colored(' > No active users found', 'yellow'))
            exit(0)

        for user in users:
            account = Account(databases, user[1])

            start_text = "Updating Plex user %s watched elements to Trakt.tv.." % user[1]
            spinner = yaspin(text=start_text, color="green")
            spinner.start()

            account.update_watched_tv_shows()
            account.update_watched_movies()

            spinner.text = "Plex user %s watched elements successfully updated to Trakt.tv!" % user[1]
            spinner.ok("✔")
            spinner.stop()


def recommendation():
    if arguments['<PlexUsername>']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_tractastic_user_existance(plex_username):
            account = Account(databases, plex_username)

            if arguments['tv']:
                start_text = "Getting tv-show recommendations for user %s.." % plex_username
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                shows = account.get_tv_recommendations()

                spinner.ok("✔")
                spinner.stop()

                utils.list_tv_recommendations(shows)

            if arguments['movies']:
                start_text = "Getting movie recommendations for user %s.." % plex_username
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                movies = account.get_movie_recommendations()

                spinner.ok("✔")
                spinner.stop()

                utils.list_movies_recommendations(movies)

            if arguments['reset']:
                start_text = "Resetting recommendations for user %s.." % plex_username
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                account.delete_hidden_recommendations()

                spinner.text = "Reset successful for user %s" % plex_username
                spinner.ok("✔")
                spinner.stop()

        else:
            databases.close_connections()
            exit(0)

    if arguments['all']:
        users = databases.get_traktastic_active_users()

        if len(users) == 0:
            print(colored(' > No active users found', 'yellow'))
            exit(0)

        if arguments['reset']:
            for user in users:
                account = Account(databases, user[1])

                start_text = "Resetting recommendations for user %s.." % user[1]
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                account.delete_hidden_recommendations()

                spinner.text = "Reset successful for user %s" % user[1]
                spinner.ok("✔")
                spinner.stop()

        else:
            for user in users:
                account = Account(databases, user[1])

                start_text = "Updating recommendations for user %s.." % user[1]
                spinner = yaspin(text=start_text, color="green")
                spinner.start()

                account.get_tv_recommendations()
                account.get_movie_recommendations()

                spinner.text = "Update successful for user %s" % user[1]
                spinner.ok("✔")
                spinner.stop()


def library():
    if arguments['<PlexUsername>']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_tractastic_user_existance(plex_username):
            account = Account(databases, plex_username)

            if arguments['tv']:
                spinner = yaspin(text="Creating tv-show recommendations library.. ", color="green")
                spinner.start()

                success = account.create_user_tv_recommendations_library()

                if success:
                    spinner.ok("✔")
                else:
                    spinner.text = "No tv-shows for this user are cached. Please run 'traktastic.py recommendations " + plex_username + " tv' first!"
                    spinner.fail("💥 ")

            if arguments['movies']:
                spinner = yaspin(text="Creating movie recommendations library.. ", color="green")
                spinner.start()

                success = account.create_user_movie_recommendations_library()

                if success:
                    spinner.ok("✔")
                else:
                    spinner.text = "No movies for this user are cached. Please run 'traktastic.py recommendations " + plex_username + " movies' first!"
                    spinner.fail("💥 ")

            if arguments['delete']:
                text = "Deleting recommendation libraries for user %s.." % plex_username
                spinner = yaspin(text=text, color="green")
                spinner.start()

                account.delete_user_recommendation_libraries()

                spinner.ok("✔")
                spinner.stop()

    if arguments['all']:
        users = databases.get_traktastic_active_users()

        if len(users) == 0:
            print(colored(' > No active users found', 'yellow'))
            exit(0)

        for user in users:
            account = Account(databases, user[1])

            start_text = "(Re-)Creating recommendation libraries for user %s.." % user[1]
            spinner = yaspin(text=start_text, color="green")
            spinner.start()

            account.create_user_tv_recommendations_library()
            account.create_user_movie_recommendations_library()

            spinner.text = "(Re-)Creating of libraries successful for user %s" % user[1]
            spinner.ok("✔")
            spinner.stop()


def downloads():
    if arguments['<PlexUsername>']:
        plex_username = arguments['<PlexUsername>']

        if databases.verify_tractastic_user_existance(plex_username):
            account = Account(databases, plex_username)

            if arguments['movies']:
                spinner = yaspin(text="Searching missing movie recommendations in Radarr..", color="green")
                spinner.start()

                if arguments['--hidden']:
                    hidden = True
                else:
                    hidden = False

                spinner = account.add_missing_movies_to_radarr(spinner, hidden)

                spinner.ok("✔")
                spinner.stop()

            if arguments['tv']:
                spinner = yaspin(text="Searching missing tv-shows recommendations in Sonarr..", color="green")
                spinner.start()

                if arguments['--hidden']:
                    hidden = True
                else:
                    hidden = False

                spinner = account.add_missing_tv_shows_to_radarr(spinner, hidden)

                spinner.ok("✔")
                spinner.stop()

    if arguments['all']:
        users = databases.get_traktastic_active_users()

        if len(users) == 0:
            print(colored(' > No active users found', 'yellow'))
            exit(0)

        if arguments['--hidden']:
            hidden = True
        else:
            hidden = False

        for user in users:
            account = Account(databases, user[1])

            text = 'Searching missing movie recommendations of user %s in Radarr..' % user[1]
            spinner = yaspin(text=text, color="green")
            spinner.start()

            spinner = account.add_missing_tv_shows_to_radarr(spinner, hidden)
            spinner.text = spinner.text + ' (' + user[1] + ')'

            spinner.ok("✔")
            spinner.stop()

            text = 'Searching missing tv-show recommendations of user %s in Sonarr..' % user[1]
            spinner = yaspin(text=text, color="green")
            spinner.start()

            spinner = account.add_missing_movies_to_radarr(spinner, hidden)
            spinner.text = spinner.text + ' (' + user[1] + ')'

            spinner.ok("✔")
            spinner.stop()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Traktastic Alpha 0.1')

    databases = Databases()
    utils = Utils(databases)

    databases.init()

    if arguments['accounts']:
        accounts()

    if arguments['update']:
        update()

    if arguments['recommendations']:
        recommendation()

    if arguments['library']:
        library()

    if arguments['downloads']:
        downloads()

    databases.close_connections()
