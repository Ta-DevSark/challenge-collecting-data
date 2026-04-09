--- README.md
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

+++ README.md
# ImmoEliza - Property Data Collection Challenge

This project contains tools for scraping real estate property data from Immoweb.be.

## Project Structure

```
/workspace/
├── property_details_csv.py    # Standalone scraper using requests/BeautifulSoup
├── get_property_links.py      # URL extraction utility
├── immoweb/                   # Scrapy project
│   ├── scrapy.cfg
│   └── immoweb/
│       ├── settings.py
│       ├── items.py
│       ├── spiders/
│       │   ├── getalldata.py  # Main data extraction spider
│       │   └── getallurls.py  # URL collection spider
│       ├── middlewares.py
│       └── pipelines.py
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### LZMA Module Issue (if applicable)

If you encounter issues with the LZMA module, follow these steps:

1. Install system dependencies:
```bash
sudo apt-get install lzma liblzma-dev libbz2-dev
```

2. Install backports.lzma:
```bash
pip install backports.lzma
```

3. Modify the lzma.py file in your Python installation:
```python
# Add at the top of lzma.py
try:
    from _lzma import *
    from _lzma import _encode_filter_properties, _decode_filter_properties
except ImportError:
    from backports.lzma import *
    from backports.lzma import _encode_filter_properties, _decode_filter_properties
```

## Usage

### Option 1: Standalone Scripts (requests + BeautifulSoup)

#### Extract Property URLs
```bash
python get_property_links.py --num-pages 100 --workers 5
```

Options:
- `--num-pages`, `-n`: Number of search result pages to scrape (default: 300)
- `--workers`, `-w`: Maximum concurrent workers (default: 5)

#### Extract Property Details
```bash
python property_details_csv.py --num-properties 100 --output my_data.csv --workers 5
```

Options:
- `--num-properties`, `-n`: Number of properties to scrape (default: 300)
- `--output`, `-o`: Output CSV file path (default: output_new.csv)
- `--workers`, `-w`: Maximum concurrent workers (default: 5)

### Option 2: Scrapy Spider

#### Extract All Property Data
```bash
cd immoweb
scrapy crawl getalldata -o output.csv
```

#### Extract Only URLs
```bash
cd immoweb
scrapy crawl getallurls -o urls.json
```

#### With Custom Settings
```bash
cd immoweb
scrapy crawl getalldata -o output.csv -s DOWNLOAD_DELAY=3 -s CONCURRENT_REQUESTS=8
```

## Output Fields

The scraped data includes the following fields:

| Field | Description |
|-------|-------------|
| locality | City/town name |
| postal_code | Postal code |
| property_type | Type (House/Apartment) |
| subtype_property | Subtype (e.g., Villa, Studio) |
| price | Sale price |
| type_of_sale | Transaction type |
| number_of_rooms | Bedroom count |
| living_area | Living room surface (m²) |
| kitchen_fully_equiped | Kitchen type |
| is_furnished | Furnished status |
| has_open_fire | Fireplace exists |
| has_terrace | Terrace exists |
| terrace_area | Terrace surface (m²) |
| has_garden | Garden exists |
| garden_surface | Garden surface (m²) |
| habitable_surface | Net habitable surface (m²) |
| plot_land_surface | Land surface (m²) |
| number_of_facades | Facade count |
| has_swimming_pool | Swimming pool exists |
| building_state | Building condition |

## Best Practices

1. **Respect robots.txt**: The scraper is configured to obey Immoweb's robots.txt rules
2. **Rate limiting**: Use appropriate delays between requests to avoid overloading the server
3. **Error handling**: Both implementations include robust error handling and logging
4. **Logging**: Check log files (`property_scraper.log`) for detailed execution information

## Troubleshooting

### Common Issues

1. **No data extracted**:
   - Check internet connection
   - Verify website structure hasn't changed
   - Check logs for specific errors

2. **Too many requests**:
   - Increase DOWNLOAD_DELAY
   - Reduce CONCURRENT_REQUESTS
   - Add random delays between requests

3. **JSON parsing errors**:
   - Website structure may have changed
   - Check if JavaScript rendering is required

## License

This project is for educational purposes only. Please respect Immoweb's terms of service and use this code responsibly.
