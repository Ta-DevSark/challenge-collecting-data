# challenge-collecting-data
ImmoEliza

ABOUT THE LZMA MODULE ISSUE :

follow these steps to correctly install the module in your environment.

1)sudo apt-get install lzma
  sudo apt-get install liblzma-dev
  sudo apt-get install libbz2-dev

2) After the installation is over,

pip install backports.lzma 

3) with nano or vim, copy paste and open the directory where the lzma file is (it should look like this : 

vim /home/tad/.pyenv/versions/3.11.3/lib/python3.11/lzma.py)

4) add these lines of code 

try:
    from _lzma import *
    from _lzma import _encode_filter_properties, _decode_filter_properties
except:
    from backports.lzma import *
    from backports.lzma import _encode_filter_properties, _decode_filter_properties

5) go back to your working environment and launch scrapy shell again.