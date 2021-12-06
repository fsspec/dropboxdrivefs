import unittest
from unittest.mock import patch

import dropbox
import fsspec

import dropboxdrivefs
from dropboxdrivefs import DropboxDriveFileSystem


@patch.object(dropbox.Dropbox, "files_list_folder")
class TestDropboxLs(unittest.TestCase):
    def setUp(self):
        self.fs = DropboxDriveFileSystem("123")

        self.folder_list = dropbox.files.ListFolderResult()
        self.folder_list.entries = [
            dropbox.files.FileMetadata(
                name="file1.txt", path_display="file1.txt", size=20
            ),
            dropbox.files.FileMetadata(
                name="file2.txt", path_display="file2.txt", size=30
            ),
        ]
        self.folder_list.cursor = "123"
        self.folder_list.has_more = False


class TestDropboxOpen(unittest.TestCase):
    def setUp(self):
        self.fs = DropboxDriveFileSystem("123")

    @patch.object(dropbox.Dropbox, "files_get_temporary_link")
    @patch.object(dropboxdrivefs.DropboxDriveFileSystem, "info")
    def test_open_rb(self, moke_info, moke_link):
        import fsspec.implementations.webhdfs

        temp_link = dropbox.files.GetTemporaryLinkResult()
        temp_link.metadata = dropbox.files.FileMetadata(name="file1.txt")
        temp_link.link = "http://test_link"
        moke_link.return_value = temp_link

        moke_info.return_value = {"size": 20}

        reader = self.fs._open("/Home/folder1", mode="rb")

        self.assertIsInstance(reader, fsspec.implementations.webhdfs.WebHDFile)

    def test_open_wb(self):
        with patch("dropboxdrivefs.core.DropboxDriveFile") as mock_subclass:
            reader = self.fs._open("/Home/folder1", mode="wb")
            self.assertIsInstance(reader, type(mock_subclass.return_value))


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.fs = DropboxDriveFileSystem("123")
        self.metadata = [
            dropbox.files.FileMetadata(
                name="file1.txt", path_display="file1.txt", size=20
            ),
            dropbox.files.FolderMetadata(name="files", path_display="files"),
        ]

    def test_info_file(self):
        info = self.fs._refactor_metadata(self.metadata[0])

        self.assertEqual(info["name"], "file1.txt")
        self.assertEqual(info["size"], 20)
        self.assertEqual(info["type"], "file")

    def test_info_folder(self):
        info = self.fs._refactor_metadata(self.metadata[1])

        self.assertEqual(info["name"], "files")
        self.assertEqual(info["size"], None)
        self.assertEqual(info["type"], "directory")

    def test_info(self):
        info = self.fs._refactor_metadata(
            dropbox.files.Metadata(name="file1.txt", path_display="file1.txt")
        )
        self.assertEqual(info["name"], "file1.txt")
        self.assertEqual(info["size"], None)
        self.assertEqual(info["type"], None)

    def test_info_no_details(self):
        info = self.fs._refactor_metadata(self.metadata[0], detail=False)

        self.assertEqual(info, "file1.txt")


if __name__ == "__main__":
    unittest.main()
