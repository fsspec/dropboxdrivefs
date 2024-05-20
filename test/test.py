import unittest
from unittest.mock import patch, call
import dropbox

import dropboxdrivefs
from dropboxdrivefs import DropboxDriveFileSystem

import os

# Get the directory containing the current file
dropboxdrivefs_dir = os.path.dirname(os.path.dirname( os.path.abspath(__file__)))


@patch.object(dropbox.Dropbox, "files_copy")
class TestDropboxCopy(unittest.TestCase):

    def setUp(self) -> None:

        self.fs = DropboxDriveFileSystem('123')

    def test_copy_dir_to_dir_recursive(self, mock_files_copy):
        self.fs.cp(os.path.join(dropboxdrivefs_dir, "example_file/"), "/target/newdir/", recursive=True)
        self.assertEqual(mock_files_copy.call_count, 1)
        mock_files_copy.assert_has_calls([call(os.path.join(dropboxdrivefs_dir, "example_file"), "/target/newdir")])
    

    def test_copy_dir_to_dir_non_recursive(self, mock_files_copy):
        self.fs.cp(os.path.join(dropboxdrivefs_dir, "example_file/"), "/target/newdir/", recursive=True)
        with self.assertRaises(AssertionError) as context:
            self.fs.cp(os.path.join(dropboxdrivefs_dir, "example_file/"), "/target/newdir/", recursive=False)
        self.assertEqual(str(context.exception), "recursive should be True for folder copying")
    
    def test_copy_file_to_dir(self, mock_files_copy): # 1a. File to existing directory
        self.fs.cp(os.path.join(dropboxdrivefs_dir, "example_file/test_db/test1.txt"), '/target/')
        self.assertEqual(mock_files_copy.call_count, 1)
        mock_files_copy.assert_has_calls([call(os.path.join(dropboxdrivefs_dir, "example_file/test_db/test1.txt"), "/target/test1.txt")])
    

    def test_copy_file_to_file(self, mock_files_copy):
        # 1d. File to File in new directory
        self.fs.cp(os.path.join(dropboxdrivefs_dir, "example_file/test_db/test1.txt"), "/target/newdir/newfile.txt")
        self.assertEqual(mock_files_copy.call_count, 1)
        mock_files_copy.assert_has_calls([call(os.path.join(dropboxdrivefs_dir, "example_file/test_db/test1.txt"), "/target/newdir/newfile.txt")])
    

    def test_copy_multiple_files_to_dir(self, mock_files_copy):

        self.fs.cp([os.path.join(dropboxdrivefs_dir, "example_file/test_db/test1.txt"), 
                    os.path.join(dropboxdrivefs_dir, "example_file/test_db/test2.txt")], "/target/")
        self.assertEqual(mock_files_copy.call_count, 2)
        mock_files_copy.assert_has_calls([call(os.path.join(dropboxdrivefs_dir, "example_file/test_db/test1.txt"), "/target/test1.txt"), 
                                          call(os.path.join(dropboxdrivefs_dir, "example_file/test_db/test2.txt"), "/target/test2.txt")], 
                                          any_order=True)


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
