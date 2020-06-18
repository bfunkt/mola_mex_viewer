import os
from download import interactive_download

if __name__ == '__main__':
    url = 'https://pds-geosciences.wustl.edu/mex/mex-m-hrsc-5-refdr-dtm-v1/mexhrs_2001/data/3231/h3231_0001_dt4.img'
    fname = url.split('/')[-1]
    if not os.path.exists(fname):
        interactive_download(url, fname)

    