from pathlib import Path
import ilo_download

def download_data(src_url,src_csv,src_url2,src_csv2,src_url3,src_csv3,src_url4,src_csv4):    
    '''
    Download data from url and store in download folder
    Unzip and store the data in the data folder
    '''
 
    storage_root = Path(".").absolute()
    download_path = storage_root / "download"
    data_path = storage_root / "data"
    
    data_gz = ilo_download.download_data(src_url=src_url, storage_path=download_path)
    ilo_download.create_archive(src_csv=src_csv,storage_path=data_path)
    ilo_download.extract_data(download_path,data_path,src_csv,src_url)
    
    
    data_gz = ilo_download.download_data(src_url=src_url2, storage_path=download_path)
    ilo_download.create_archive(src_csv=src_csv2,storage_path=data_path)
    ilo_download.extract_data(download_path,data_path,src_csv2,src_url2)
    
    
    data_gz = ilo_download.download_data(src_url=src_url3, storage_path=download_path)
    ilo_download.create_archive(src_csv=src_csv3,storage_path=data_path)
    ilo_download.extract_data(download_path,data_path,src_csv3,src_url3)    
   
    data_gz = ilo_download.download_data(src_url=src_url4, storage_path=download_path)
    ilo_download.create_archive(src_csv=src_csv4,storage_path=data_path)
    ilo_download.extract_data(download_path,data_path,src_csv4,src_url4)  