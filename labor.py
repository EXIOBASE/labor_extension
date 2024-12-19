from pathlib import Path
import sys
sys.path.insert(1, 'workforce_salary')
sys.path.insert(2, 'working_hour')

#import download
#import workforce
#import average_working_hours
import workforce_salary.workforce

import workforce_salary.download
import workforce_salary.ref_label
import workforce_salary.workforce

#15:00 22.03.22
storage_root = Path(".").absolute()
download_path = storage_root / "download"
data_path = storage_root / "data"



'''
URL of tables
'''

src_url = "https://www.ilo.org/ilostat-files/WEB_bulk_download/indicator/EMP_2EMP_SEX_ECO_NB_A.csv.gz"
src_csv = Path("EMP_2EMP_SEX_ECO_NB_A.csv")

src_url2 = "https://www.ilo.org/ilostat-files/WEB_bulk_download/indicator/HOW_TEMP_SEX_ECO_NB_A.csv.gz"
src_csv2 = Path("HOW_TEMP_SEX_ECO_NB_A.csv")

src_url3 = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/LFSA_EWHUNA/?format=TSV"
src_csv3 = Path("estat_lfsa_ewhuna.tsv")

src_url4 = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/LFSA_EWHUN2/?format=TSV"
src_csv4 = Path("estat_lfsa_ewhun2.tsv")




'''
Download compressed files, save them in "download" folder
uncompressed files and save them in "data" folder
'''
workforce_salary.download.download_data(src_url,src_csv,src_url2,src_csv2,src_url3,src_csv3,src_url4,src_csv4)


'''
Calculation of the workforce
'''

workforce = workforce_salary.workforce.workforce_calculation(data_path,src_csv,src_csv2)
workforce.to_csv('workforce.csv')
workforce_old = workforce.copy()
workforce = final.copy()

'''
Calculation of the average number of working hours
'''


average_hour = working_hour.average_working_hours(workforce,src_csv2,data_path,src_csv3) #15:50 le 25 mars
average_hour.to_csv('average_working_hour.csv')


