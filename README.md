# Traktastic

A Python framework to map several Plex users to individual Trakt.tv profiles. In addition, user-specific Plex libraries can be created with recommendations based on Trakt.tv data.

Features of Traktastic:
- Link different Plex users to their own Trakt.tv profiles
- Update the "watched history" for single or all users
- Receive recommendations for individual or all users (TV series and movies)
- Configure filters for the desired recommendations, while TV series or films that do not meet the criteria are automatically dismissed and new ones are loaded
- Based on the recommendations, create new Plex Libraries for the respective users, whereby existing content is linked to a user-specific directory by means of symlinking in order to save space
- Create and share the libraries directly on your Plex Server and share them with the corresponding user automatically

In development:
- Cronjob Administration
- Sonarr/Radarr API


## Getting Started

In order for the framework to work properly, a few things need to be configured first.

### Prerequisites

Tested with Python: >= 3.6.4

#### Trakt.tv API Key

In order for the framework to work, a Trakt.tv API Key must be created.

- Please visit ```https://trakt.tv/oauth/applications``` and login with your Trakt.tv user.
- Click on ```New Application``` to generate a new API Key and fill out the form as followed:

![alt text](https://github.com/h1f0x/Traktastic/blob/master/images/001.png?raw=true)

- Copy your "Client ID" and your "Client Secret" into the configuration file under ```./config/config.yaml```

#### Configuration File

In the configuration file, the filter settings, database locations as well as the location of the user-specific Plex Libraries can be defined.

Location: ```./config/config.yaml```

The options are self-explanatory, customize them as you would like:

```
trakt:
  application: 'Traktastic'
  client_id: <YOUR_CLIENT_ID>
  client_secret: <YOUR_CLIENT_SECRET>
  tv_genre_blacklist: ['animation', 'anime', 'children']
  tv_year_before_blacklist: 1998
  tv_max_related_shows: 3
  movie_genre_blacklist: ['animation', 'anime', 'children']
  movie_year_before_blacklist: 1990
  movie_max_related_movies: 5

plex:
  username: <YOUR_PLEX_USERNAME>
  password: <YOUR_PLEX_PASSWORD>
  server: <YOUR_PLEX_MEDIA_SERVER_ID>
  library_name_movie: 'Movie Recommendations'
  library_name_tv: 'TV-Show Recommendations'
  library_language: 'en'
  auto_library: False

filesystem:
  libraries_base_path: './libraries/'

databases:
  traktastic_database_path: './databases/traktastic.db'
  plex_database_path: '/path/to/plex/database.db'
```

> NOTE: If you want to auto-generate Plex Libraries for users, you need to set the ``auto_library`` flag to ```True``` and enter your Plex Server credentials (```username```, ```password```) and your server id (```server```)! The library command section will now push the libraries to your Plex server and shares them with the correct user only!

### Installing

A few Python requirements are necessary for everything to work:

```
pip install -r requirements.txt
```

## Application

The following commands are available:

```
Usage:  traktastic.py accounts list [plex]
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

All operations are based on the Plex username of a user.

Commands:
  accounts list [plex]                      List registered accounts [by adding plex - get a list of plex accounts]
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

Arguments:
  <PlexUsername>        Username which is shown by 'traktastic.py accounts list plex'

Options:
  -h --help
```

## Screenshots

A few screenshots for demonstration purposes. All data are dummy data!

##### $: accounts list
![alt text](https://github.com/h1f0x/Traktastic/blob/master/images/002.png?raw=true)

##### $: account link < PlexUsername >
![alt text](https://github.com/h1f0x/Traktastic/blob/master/images/004.png?raw=true)

##### $: update all
![alt text](https://github.com/h1f0x/Traktastic/blob/master/images/003.png?raw=true)

##### $: recommendations < PlexUsername > tv 
![alt text](https://github.com/h1f0x/Traktastic/blob/master/images/005.png?raw=true)



## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details


