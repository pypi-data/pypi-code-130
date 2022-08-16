from .testcase import VolumeTestCase, FileSystemTestCase, db_store as fixtures
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin, DeleteMixin
from heaserver.service.representor import cj, nvpjson
from aiohttp import hdrs


class TestVolumeGet(VolumeTestCase, GetOneMixin):
    async def test_get_status_opener_choices(self) -> None:
        """Checks if a GET request for the opener for a bucket succeeds with status 300."""
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'opener').path,
                                        headers=self._headers)
        self.assertEqual(300, obj.status)

    async def test_get_status_opener_hea_default_exists(self) -> None:
        """
        Checks if a GET request for the opener for a bucket succeeds and returns JSON that contains a
        Collection+JSON object with a rel property in its links that contains 'hea-default'.
        """
        obj = await self.client.request('GET',
                                        (self._href / self._id() / 'opener').path,
                                        headers={**self._headers, hdrs.ACCEPT: cj.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        received_json = await obj.json()
        rel = received_json[0]['collection']['items'][0]['links'][0]['rel']
        self.assertIn('hea-default', rel)


class TestVolumeGetAll(VolumeTestCase, GetAllMixin):
    async def test_get_all_volumes_with_file_system_type(self) -> None:
        """
        Checks if a GET request for every volume whose file system type is heaobject.volume.AWSFileSystem
        succeeds and returns the second volume in the fixtures.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'byfilesystemtype' / 'heaobject.volume.AWSFileSystem').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        json = await obj.json()
        if not json:
            self.fail('No objects in response')
        self.assertEqual([fixtures[self._coll][1]], json)

    async def test_get_all_volumes_with_file_system_type_doesnt_exist(self) -> None:
        """
        Checks if a GET request for every volume whose file system type is heaobject.volume.MongoDBFileSystem
        succeeds but returns no objects.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'byfilesystemtype' / 'heaobject.volume.MongoDBFileSystem').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        self.assertEqual([], await obj.json())

    async def test_get_all_volumes_with_file_system_type_and_name(self) -> None:
        """
        Checks if a GET request for every volume whose file system type is heaobject.volume.AWSFileSystem and
        whose file system name is DEFAULT_FILE_SYSTEM succeeds and returns a list containing the second volume in the
        fixtures.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'byfilesystemtype' / 'heaobject.volume.AWSFileSystem' / 'byfilesystemname' / 'DEFAULT_FILE_SYSTEM').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        json = await obj.json()
        if not json:
            self.fail('No objects in response')
        self.assertEqual([fixtures[self._coll][1]], json)

    async def test_get_all_volumes_with_file_system_type_and_name_doesnt_exist(self) -> None:
        """
        Checks if a GET request for every volume whose file system type is heaobject.volume.DefaultFileSystem and
        whose file system name is HEA_FILE_SYSTEM succeeds but returns no objects.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'byfilesystemtype' / 'heaobject.volume.DefaultFileSystem' / 'byfilesystemname' / 'HEA_FILE_SYSTEM').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        self.assertEqual([], await obj.json())


class TestVolumePost(VolumeTestCase, PostMixin):
    pass


class TestVolumePut(VolumeTestCase, PutMixin):
    def _id(self):
        return fixtures[self._coll][1]['id']


class TestVolumeDelete(VolumeTestCase, DeleteMixin):
    pass


class TestFileSystemGet(FileSystemTestCase, GetOneMixin):
    async def test_get_by_name(self):
        self.skipTest('FileSystem does not support GET by name')

    async def test_get_filesystem_with_type_and_name(self) -> None:
        """
        Checks if a GET request for the filesystem whose type is heaobject.volume.MongoDBFileSystem and whose name
        is local_mongodb_file_system succeeds and returns a list containing the second filesystem in the fixtures.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.volume.MongoDBFileSystem' / 'byname' / 'local_mongodb_file_system').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        if not obj.ok:
            self.fail(f'GET request failed: {await obj.text()}')
        json = await obj.json()
        if not json:
            self.fail('No objects in response')
        self.assertEqual([fixtures[self._coll][1]], json)

    async def test_get_filesystem_with_type_doesnt_exist_and_name(self) -> None:
        """
        Checks if a GET request for the filesystem whose type is heaobject.volume.DefaultFileSystem and whose name
        is local_mongodb_file_system fails with status 404.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.volume.DefaultFileSystem' / 'byname' / 'local_mongodb_file_system').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        self.assertEqual(404, obj.status)

    async def test_get_filesystem_with_type_and_name_doesnt_exist(self) -> None:
        """
        Checks if a GET request for the filesystem whose type is heaobject.volume.MongoDBFileSystem and whose name
        is HEA_FILE_SYSTEM fails with status 404.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.volume.MongoDBFileSystem' / 'byname' / 'HEA_FILE_SYSTEM').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        self.assertEqual(404, obj.status)

    async def test_get_filesystem_with_type_and_name_combo_doesnt_exist(self) -> None:
        """
        Checks if a GET request for the filesystem whose type is heaobject.volume.MongoDBFileSystem and whose name
        is DEFAULT_FILE_SYSTEM fails with status 404.
        """
        obj = await self.client.request('GET',
                                        (self._href / 'bytype' / 'heaobject.volume.MongoDBFileSystem' / 'byname' / 'DEFAULT_FILE_SYSTEM').path,
                                        headers={**self._headers, hdrs.ACCEPT: nvpjson.MIME_TYPE})
        self.assertEqual(404, obj.status)


class TestFileSystemGetAll(FileSystemTestCase, GetAllMixin):
    pass


class TestFileSystemPost(FileSystemTestCase, PostMixin):
    pass


class TestFileSystemPut(FileSystemTestCase, PutMixin):
    def _id(self):
        return fixtures[self._coll][1]['id']


class TestFileSystemDelete(FileSystemTestCase, DeleteMixin):
    pass
