"""
Testing Copy Method of DropboxDriveFileSystem

Test case reference from https://filesystem-spec.readthedocs.io/en/latest/copying.html
"""
import pytest
from dropboxdrivefs import DropboxDriveFileSystem

@pytest.fixture
def dropbox_fs():
    fs = DropboxDriveFileSystem('123')
    if not fs.exists('/source'):
        fs.mkdir('/source')
    if not fs.exists('/source/subdir'):
        fs.mkdir('/source/subdir')
    if not fs.exists('/target'):
        fs.mkdir('/target')
    with fs.open('/source/subdir/subfile1', 'w') as f:
        f.write('hello')
    with fs.open('/source/file1', 'w') as f:
        f.write('hello')
    with fs.open('/source/file2', 'w') as f:
        f.write('hello')
    return fs

def test_db_cp(dropbox_fs):
    try:
        # 1f. Directory to new directory
        dropbox_fs.cp("/source/subdir/", "/target/newdir/", recursive=True)
        assert dropbox_fs.exists('/target/newdir/subfile1')
        dropbox_fs.rm('/target/newdir', recursive=True)
        # 1e. Directory to existing directory
        dropbox_fs.cp("/source/subdir/", "/target/", recursive=True)
        assert dropbox_fs.exists('/target/subfile1')
        dropbox_fs.rm('/target/subfile1')
        # 1a. File to existing directory
        dropbox_fs.cp('/source/subdir/subfile1', '/target/')
        assert dropbox_fs.exists('/target/subfile1')
        dropbox_fs.rm('/target/subfile1')
        # 1b. File to new directory
        dropbox_fs.cp('/source/subdir/subfile1', '/target/newdir/')
        assert dropbox_fs.exists('/target/newdir/subfile1')
        dropbox_fs.rm('/target/newdir', recursive=True)
        # 1c. File to File in existing directory
        dropbox_fs.cp("/source/subdir/subfile1", "/target/newfile")
        assert dropbox_fs.exists('/target/newfile')
        dropbox_fs.rm('/target/newfile')
        # 1d. File to File in new directory
        dropbox_fs.cp("/source/subdir/subfile1", "/target/newdir/newfile")
        assert dropbox_fs.exists('/target/newdir/newfile')
        dropbox_fs.rm('/target/newdir', recursive=True)
        # 2a. List of Files to existing directory 
        dropbox_fs.cp(["/source/file1", "/source/file2", "/source/subdir/subfile1"], "/target/")
        assert dropbox_fs.exists('/target/file1')
        assert dropbox_fs.exists('/target/file2')
        assert dropbox_fs.exists('/target/subfile1')
        dropbox_fs.rm('/target/file1')
        dropbox_fs.rm('/target/file2')
        dropbox_fs.rm('/target/subfile1') 
        # 2b. List of Files to new directory
        dropbox_fs.cp(["/source/file1", "/source/file2", "/source/subdir/subfile1"], "/target/newdir/")
        assert dropbox_fs.exists('/target/newdir/file1')
        assert dropbox_fs.exists('/target/newdir/file2')
        assert dropbox_fs.exists('/target/newdir/subfile1')
        dropbox_fs.rm('/target/newdir/', recursive=True)
    finally:
        # Final Delete
        dropbox_fs.rm('/source/', recursive=True)
        dropbox_fs.rm('/target/', recursive=True)