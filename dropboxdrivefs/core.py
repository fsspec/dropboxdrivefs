import logging

import dropbox.files
import requests
from dropbox.exceptions import ApiError
from fsspec.implementations import webhdfs
from fsspec.spec import AbstractBufferedFile
from fsspec.spec import AbstractFileSystem

__all__ = ["DropboxDriveFileSystem"]


class DropboxDriveFileSystem(AbstractFileSystem):
    """ Interface dropbox to connect, list and manage files
    Parameters:
    ----------
    token : str
          Generated key by adding a dropbox app in the user dropbox account.
          Needs to be done by the user

    """

    def __init__(self, token, *args, **storage_options):
        super().__init__(token=token, *args, **storage_options)
        self.token = token
        self.connect()

    def _call(self, _, method="get", path=None, data=None, redirect=True, offset=0, length=None,
              **kwargs):
        headers = {"Range": f"bytes={offset}-{offset+length+1}"}

        out = self.session.request(
            method=method.upper(),
            url=path,
            data=data,
            allow_redirects=redirect,
            headers=headers
        )
        out.raise_for_status()
        return out

    def connect(self):
        """ connect to the dropbox account with the given token
        """
        self.dbx = dropbox.Dropbox(self.token)
        self.session = requests.Session()
        self.session.auth = ("Authorization", self.token)

    def ls(self, path, detail=True, **kwargs):
        """ List objects at path
        """
        path = path.replace("//", "/")
        list_file = []

        try:
            list_item = self.dbx.files_list_folder(
                path, recursive=True, include_media_info=True
            )
        except ApiError as error:
            logging.warning(error)
            return None
        else:
            items = list_item.entries
            while list_item.has_more:

                list_item = self.dbx.files_list_folder_continue(list_item.cursor)
                items = list_item.entries + items

            for metadata in list_item.entries:
                list_file.append(self._refactor_metadata(metadata, detail=detail))
            return list_file

    def mkdir(self, path, create_parent=True, autorename=True):
        try:
            output = self.dbx.files_create_folder_v2(path)
            metadata = self._refactor_metadata(output.metadata)
            logging.info(
                "The " + metadata["type"] + metadata["name"] + " has  been created."
            )
        except ApiError as error:
            logging.warning(error)

    def _rm(self, path):
        try:
            output = self.dbx.files_delete_v2(path)
            metadata = self._refactor_metadata(output.metadata)
            logging.info(
                "The " + metadata["type"] + metadata["name"] + " has been erased."
            )
        except ApiError as error:
            logging.warning(error)

    def info(self, url, **kwargs):
        """Get info of URL
        """
        metadata = self.dbx.files_get_metadata(url)
        return self._refactor_metadata(metadata)

    def _open(
        self,
        path,
        mode="rb",
        block_size=None,
        autocommit=True,
        cache_options=None,
        **kwargs
    ):

        path = path.replace("//", "/")
        if mode == "rb":
            url = self.dbx.files_get_temporary_link(path).link
            return webhdfs.WebHDFile(
                self,
                url,
                mode=mode,
                cache_options=cache_options,
                size=self.info(path)["size"],
                tempdir=None,
                autocommit=True
            )

        return DropboxDriveFile(
            self,
            path,
            mode=mode,
            block_size=4 * 1024 * 1024,
            autocommit=autocommit,
            cache_options=cache_options,
            **kwargs
        )

    def _refactor_metadata(self, metadata, detail=True):
        if detail:
            if isinstance(metadata, dropbox.files.FileMetadata):
                return {
                    "name": metadata.path_display,
                    "size": metadata.size,
                    "type": "file",
                }
            elif isinstance(metadata, dropbox.files.FolderMetadata):
                return {"name": metadata.path_display, "size": None, "type": "directory"}
            else:
                return {"name": metadata.path_display, "size": None, "type": None}
        else:
            return metadata.path_display


class DropboxDriveFile(AbstractBufferedFile):
    """ fetch_all, fetch_range, and read method are based from the http implementation
    """

    def __init__(
        self,
        fs,
        path,
        mode="rb",
        block_size="default",
        autocommit=True,
        cache_type="readahead",
        cache_options=None,
        **kwargs
    ):
        """
        Open a file, write mode only

        Parameters
        ----------
        fs: instance of DropboxDriveFileSystem
        path : str
            file path to inspect in dropbox
        mode: str
            most be "wb"
        block_size: int or None
            The amount of read-ahead to do, in bytes. Default is 5MB, or the value
            configured for the FileSystem creating this file
        """
        super().__init__(fs=fs, path=path, mode=mode, block_size=block_size,
                         cache_type=cache_type, cache_options=cache_options,
                         **kwargs)

        self.path = path
        self.dbx = self.fs.dbx

    def _upload_chunk(self, final=False):
        if final:

            self.dbx.files_upload_session_finish(
                self.buffer.getvalue(), self.cursor, self.commit
            )
        else:

            self.dbx.files_upload_session_append_v2(
                self.buffer.getvalue(), self.cursor.session_id, self.cursor.offset
            )

        self.cursor.offset += self.buffer.seek(0, 2)

    def _initiate_upload(self):
        """ Initiate the upload session
        """

        session = self.dbx.files_upload_session_start(b"")

        if "w" in self.mode:
            self.commit = dropbox.files.CommitInfo(
                path=self.path, mode=dropbox.files.WriteMode("overwrite", None)
            )
        elif "a" in self.mode:
            self.commit = dropbox.files.CommitInfo(
                path=self.path, mode=dropbox.files.WriteMode("add")
            )

        self.cursor = dropbox.files.UploadSessionCursor(
            session_id=session.session_id, offset=self.offset
        )
