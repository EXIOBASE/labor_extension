import requests
from pathlib import Path
import gzip
import shutil
import os


# def download_data(src_url, storage_path, force_download=False):
#     """Store the fao dataset at storage path

#     Parameters
#     ----------

#     src_url: str
#         Url of the source data

#     storage_path: pathlib.Path
#         Location for storing the data

#     force_download: boolean, optional
#         If True, downloads the data even if it is already present in storage_path.
#         If False (default), only downloads the data if is is not available locally.

#     Returns
#     -------
#         Downloaded File: pathlib.Path

#     """

#     filename = Path(src_url.split("/")[-1])
#     print(Path(src_url.split("/")[-1]))
#     # Making the storage path if should not exisit
#     storage_path.mkdir(parents=True, exist_ok=True)
#     storage_file = storage_path / filename
#     print(storage_file)
#     if storage_file.exists() and (force_download is False):
#         return storage_file
#     print('avt download')
#     download = requests.get(src_url)
#     print('apres download')
#     # Raise exception if the file is not available
#     download.raise_for_status()
#     with open(storage_file, "wb") as sf:
#         sf.write(download.content)
        
def download_data(src_url, storage_path, force_download=False):
    """Store the fao dataset at storage path

    Parameters
    ----------

    src_url: str
        Url of the source data

    storage_path: pathlib.Path
        Location for storing the data

    force_download: boolean, optional
        If True, downloads the data even if it is already present in storage_path.
        If False (default), only downloads the data if is is not available locally.

    Returns
    -------
        Downloaded File: pathlib.Path

    """

    filename = Path(src_url.split("/")[-1])
    # Making the storage path if should not exisit
    storage_path.mkdir(parents=True, exist_ok=True)
    
    storage_file = storage_path / filename
    print(storage_file)
    if storage_file.exists() and (force_download is False):
        return storage_file
    download = requests.get(src_url)
    # Raise exception if the file is not available
    download.raise_for_status()
    with open(storage_file, "wb") as sf:
        sf.write(download.content)

def create_archive(src_csv,storage_path,force_download=False):
    filename = Path(src_csv)
    storage_path.mkdir(parents=True, exist_ok=True)
    storage_file = storage_path / filename
    if storage_file.exists() and (force_download is False):
        return storage_file
        
def extract_data(download_path,data_path,src_csv,src_url): 
    filename = Path(src_url.split("/")[-1])
    if str('.gz') in str(filename) : 
        with gzip.open(download_path/filename, 'rb') as f_in:
            with open(data_path/src_csv, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
    else : 
        os.rename(os.path.join(download_path,filename),os.path.join(download_path,src_csv))
        os.system(f'cp "{os.path.join(download_path,src_csv)}" "{os.path.join(data_path,src_csv)}"')        
        
        

