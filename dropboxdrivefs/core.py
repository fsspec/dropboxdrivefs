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
    client : Dropbox
          Instead of passing a token, you can give a instance of a Dropbox class.
          This is useful when using the Dropbox Business API.

    Example:
    -------
    ```python
    import dropbox
    from dropboxdrivefs import DropboxDriveFileSystem

    dbx = dropbox.DropboxTeam(...)
    fs = DropboxDriveFileSystem(client=dbx.as_user(...))
    ```
    """

    def __init__(self, token=None, client=None, *args, **storage_options):
        super().__init__(token=token, client=client, *args, **storage_options)
        self.connect(token=token, client=client)

    def _call(self, _, method="get", path=None, data=None, redirect=True, offset=0, length=None, **kwargs):
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

    def connect(self, token=None, client=None):
        if client is not None:
            self.dbx = client
        elif token is not None:
            self.dbx = dropbox.Dropbox(token)
        else:
            raise ValueError("You must provide either a token or a dropbox client object.")

        self.session = requests.Session()
        self.session.auth = ("Authorization", self.dbx._oauth2_access_token)

    def ls(self, path, detail=True, recursive=False, **kwargs):
        """ List objects at path
        Parameters:
        ----------
        detail: bool
            should we add the metadate with the path
            
        recursive: bool
            should be list recursively all folders and file inside the path
        """
        path = path.replace("//", "/")
        list_file = []

        try:
            list_item = self.dbx.files_list_folder(
                path, recursive=recursive, include_media_info=True
            )
        except ApiError as error:
            logging.warning(error)
            return None
        else:
            items = list_item.entries
            while list_item.has_more:

                list_item = self.dbx.files_list_folder_continue(list_item.cursor)
                items = list_item.entries + items

            for metadata in items:
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
            meta = {}

            for prop in vars(type(metadata)).keys():
                if not prop.startswith('_'):
                    meta[prop] = getattr(metadata, prop, None)

            if isinstance(metadata, dropbox.files.FileMetadata):
                meta["name"] = metadata.path_display
                meta["size"] = metadata.size
                meta["type"] ="file"

                return meta

            elif isinstance(metadata, dropbox.files.FolderMetadata):
                meta["name"] = metadata.path_display
                meta["size"] = None
                meta["type"] ="directory"
                return meta
            else:
                return {"name": metadata.path_display, "size": None, "type": None}
        else:
            return metadata.path_display
        
    def copy(self, path1, path2, recursive=True, on_error=None, **kwargs):
        """ Copy objects from path1 to path2
        Parameters:
        ----------
        path1: a folder or file, or a list of folders or files
            should we add the metadate with the path
        path2: a folder or a file
        recursive: bool
            whether to copy files in a folder recursively.
        on_error : "raise", "ignore"
            If raise, any not-found exceptions will be raised; if ignore any
            not-found exceptions will cause the path to be skipped; defaults to
            raise unless recursive is true, where the default is ignore
        """
        if on_error is None and recursive:
            on_error = "ignore"
        elif on_error is None:
            on_error = "raise"
        if isinstance(path1, list):
            for file_path in path1:
                if on_error == 'raise':
                    assert not file_path.endswith('/'), 'multiple file copy should takes files as input'
                try:
                    self.copy(file_path, path2)
                except BaseException as e:
                    if on_error == 'raise':
                        raise e
        else:
            if path1.endswith('/') and path2.endswith('/'):
                if on_error == 'raise':
                    assert recursive, 'recursive should be True for folder copying'
                if not self.exists(path2[:-1]):
                    path1 = path1[:-1]
                    path2 = path2[:-1]
                else:
                    try:
                        self.rm(path2[:-1], recursive=True)
                    except BaseException as e:
                        if on_error == 'raise':
                            raise e
                    path1 = path1[:-1]
                    path2 = path2[:-1]
            elif path2.endswith('/'):
                path2 = path2 + path1.split('/')[-1]
            try:
                self.dbx.files_copy(path1, path2)
            except BaseException as e:
                if on_error == 'raise':
                    raise e

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
                path=self.path, mode=dropbox.files.WriteMode("overwrite", None), autorename=True
            )
        elif "a" in self.mode:
            self.commit = dropbox.files.CommitInfo(
                path=self.path, mode=dropbox.files.WriteMode("add", None), autorename=True
            )

        self.cursor = dropbox.files.UploadSessionCursor(
            session_id=session.session_id, offset=self.offset
        )
