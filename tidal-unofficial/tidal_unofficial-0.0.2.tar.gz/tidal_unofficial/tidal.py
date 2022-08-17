from requests import request
import json


class TidalUnofficial:
    """
    Instantiate a Tidal object.

    :param options: Dictionary containing the options for the API call.
    :type options: dict
    """

    def __init__(self, options={}):
        self.url = 'https://api.tidal.com/v1'
        self.webToken = 'gsFXkJqGrUNoYMQPZe4k3WKwijnrp8iGSwn3bApe'
        # Tidal country code
        self.countryCode = options['countryCode'] if 'countryCode' in options else 'US'
        # user agent for API calls
        self.user_agent = options['user_agent'] if 'user_agent' in options else 'tidal_unofficial'
        # params for Tidal pages that require a locale and device type
        self.localeParams = f'locale=en_{self.countryCode}&deviceType=BROWSER&countryCode={self.countryCode}'
        self.headers = {
            'x-tidal-token': self.webToken, 'User-Agent': self.user_agent}

    def search(self, query, search_type, limit=25, offset=0):
        """
        Search for artists, albums, tracks, or playlists.

        :param query: Search query
        :type query: str

        :param search_type: Search type ('artists', 'albums', 'tracks', 'playlists')
        :type password: str

        :param limit: Results limit
        :type limit: int

        :param offset: Results offset
        :type offset: int

        :return: Dictionary containing the list of items (item properties are dependent on search type).
        :rtype: dict
        """

        accTypes = ['artists', 'albums', 'tracks', 'playlists']

        if (not search_type):
            raise ValueError(
                'Search requires type as a second argument (artists, albums, tracks, or playlists)')

        if (search_type not in accTypes):
            raise ValueError(
                f"{search_type} is not a valid search type('artists', 'albums', 'tracks', 'playlists' are valid).")

        res = request(
            'get', f'{self.url}/search/{search_type}?query={query}&limit={limit}&offset={offset}&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)

    def get_track(self, id):
        """
        Get a track's data by its ID.

        :param id: Track ID
        :type id: str

        :return: Dictionary containing all the information about a track.
        :rtype: dict
        """

        res = request(
            'get', f'{self.url}/tracks/{id}?countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)

    def get_album(self, id):
        """
        Get an albums's data by its ID.

        :param id: Album ID
        :type id: str

        :return: Dictionary containing all the information about an album.
        :rtype: dict
        """

        res = request(
            'get', f'{self.url}/albums/{id}?countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)

    def get_album_tracks(self, id):
        """
        Get an albums's tracks by its ID.

        :param id: Album ID
        :type id: str

        :return: List containing all the tracks from an album.
        :rtype: list
        """

        res = request(
            'get', f'{self.url}/albums/{id}/tracks?countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)['items']

    def get_featured_albums(self):
        """
        Get TIDAL's featured albums (internal API).

        :return: Dictionary containing all the currently featured albums.
        :rtype: dict
        """

        res = request(
            'get', f'{self.url}/pages/show_more_featured_albums?{self.localeParams}', headers=self.headers)

        tabs = json.loads(res.content)['rows'][0]['modules'][0]['tabs']

        topAlbums = [x for x in tabs if x['key'] == 'featured-top']
        newAlbums = [x for x in tabs if x['key'] == 'featured-new']
        staffPicks = [x for x in tabs if x['key'] == 'featured-recommended']

        if len(topAlbums) != 0:
            topAlbums = topAlbums[0]['pagedList']['items']
        if len(newAlbums) != 0:
            newAlbums = newAlbums[0]['pagedList']['items']
        if len(staffPicks) != 0:
            staffPicks = staffPicks[0]['pagedList']['items']

        return {
            "topAlbums": topAlbums,
            "newAlbums": newAlbums,
            "staffPicks": staffPicks,
        }

    def get_top_albums():
        """
        Get TIDAL's top 20 albums.

        :return: List containing the current top 20 albums.
        :rtype: list
        """

        featuredAlbums = self.get_featured_albums()

        return featuredAlbums['topAlbums']

    def get_new_albums():
        """
        Get new albums on TIDAL.

        :return: List containing the newest albums (no fixed number).
        :rtype: list
        """

        featuredAlbums = self.get_featured_albums()

        return featuredAlbums['newAlbums']

    def get_staff_pick_albums():
        """
        Get staff picked albums on TIDAL.

        :return: List containing the current staff picked albums (no fixed number).
        :rtype: list
        """

        featuredAlbums = self.get_featured_albums()

        return featuredAlbums['staffPicks']

    def get_artist(self, id):
        """
        Get an artist's data by its ID.

        :param id: Artist ID
        :type id: str

        :return: Dictionary containing all the information about an artist.
        :rtype: dict
        """

        res = request(
            'get', f'{self.url}/artists/{id}?&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)

    def get_artist_albums(self, id, limit=25):
        """
        Get an artist's albums, EPs and singles by its ID.

        :param id: Artist ID
        :type id: str

        :param limit: Results limit (default 25)
        :type limit: int

        :return: List containing all the albums, EPs and singles from an artist.
        :rtype: list
        """

        res = request(
            'get', f'{self.url}/artists/{id}/albums?limit={limit}&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)['items']

    def get_artist_compilations(self, id, limit=25):
        """
        Get compliations that an artist has appeared on by artist id.

        :param id: Artist ID
        :type id: str

        :param limit: Results limit (default 25)
        :type limit: int

        :return: List containing all the compliations that an artist has appeared on.
        :rtype: list
        """

        res = request(
            'get', f'{self.url}/artists/{id}/albums?filter=COMPILATIONS&limit={limit}&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)['items']

    def get_artist_top_tracks(self, id, limit=25):
        """
        Get an artist's top tracks its id.

        :param id: Artist ID
        :type id: str

        :param limit: Results limit (default 25)
        :type limit: int

        :return: List containing the artist's top N tracks.
        :rtype: list
        """

        res = request(
            'get', f'{self.url}/artists/{id}/toptracks?limit={limit}&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)['items']

    def get_similar_artists(self, id, limit=25):
        """
        Get artists similar to another by its ID.

        :param id: Artist ID
        :type id: str

        :param limit: Results limit (default 25)
        :type limit: int

        :return: List containing all the artists similar to another.
        :rtype: list
        """

        res = request(
            'get', f'{self.url}/artists/{id}/similar?limit={limit}&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)['items']

    def get_playlist_info(self, uuid):
        """
        Get a playlist's data by its UUID.

        :param uuid: Playlist's UUID
        :type id: str

        :return: Dictionary containing all the information about a playlist.
        :rtype: dict
        """

        res = request(
            'get', f'{self.url}/playlists/{uuid}?&countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)

    def get_playlist_tracks(self, uuid, limit=25):
        """
        Get a playlist's tracks by its UUID.

        :param uuid: Playlist's UUID
        :type id: str

        :return: List containing the tracks from a playlist.
        :rtype: list
        """

        res = request(
            'get', f'{self.url}/playlists/{uuid}/tracks?&countryCode={self.countryCode}&limit={limit}', headers=self.headers)

        return json.loads(res.content)['items']

    def get_video(self, id):
        """
        Get a video's data by its ID.

        :param id: Video ID
        :type id: str

        :return: Dictionary containing all the information about a video.
        :rtype: dict
        """

        res = request(
            'get', f'{self.url}/videos/{id}?countryCode={self.countryCode}', headers=self.headers)

        return json.loads(res.content)

    @staticmethod
    def artist_pic_to_url_4_3(uuid):
        """
        Get valid urls to artist pictures (4:3).

        :param uuid: Artist picture uuid (can be found as picture property in artist object)
        :type uuid: string

        :return: Dictionary containing artist pictures in different sizes.
        :rtype: dict
        """

        baseUrl = f"https://resources.tidal.com/images/{uuid.replace('-', '/')}"
        return {
            'sm': f'{baseUrl}/160x107.jpg',
            'md': f'{baseUrl}/320x214.jpg',
            'lg': f'{baseUrl}/640x428.jpg',
        }

    @staticmethod
    def artist_pic_to_url_box_1_1(uuid):
        """
        Get valid urls to artist pictures (1:1).

        :param uuid: Artist picture uuid (can be found as picture property in artist object)
        :type uuid: string

        :return: Dictionary containing artist pictures in different sizes.
        :rtype: dict
        """

        baseUrl = f"https://resources.tidal.com/images/{uuid.replace('-', '/')}"
        return {
            'sm': f'{baseUrl}/160x160.jpg',
            'md': f'{baseUrl}/320x320.jpg',
            'lg': f'{baseUrl}/640x640.jpg',
            'xl': f'{baseUrl}/750x750.jpg',
        }

    @staticmethod
    def album_art_to_url(uuid):
        """
        Get valid urls to album art.

        :param uuid: Album art uuid (can be found as cover property in album object)
        :type uuid: string

        :return: Dictionary containing album arts in different sizes.
        :rtype: dict
        """

        baseUrl = f"https://resources.tidal.com/images/{uuid.replace('-', '/')}"
        return {
            'sm': f'{baseUrl}/160x160.jpg',
            'md': f'{baseUrl}/320x320.jpg',
            'lg': f'{baseUrl}/640x640.jpg',
            'xl': f'{baseUrl}/1080x1080.jpg',
            'xxl': f'{baseUrl}/1280x1280.jpg',
        }