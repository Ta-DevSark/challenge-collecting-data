--- property_details_csv.py
import requests
import json
import re
from bs4 import BeautifulSoup
import concurrent.futures
import time
import pandas as pd
import get_property_links as gpl

start_time = time.time()

urls = gpl.scrape_all_pages(300)

def get_field_value(classified_dict, *keys):
    value = classified_dict
    for key in keys:
        if value is None or key not in value:
            return None
        value = value[key]
    return value

def convert_boolean(value):
    return str(value) if value is not None else ''

output_dict = {}
identity = 1
session = requests.Session()

def process_url(url):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    script_tag = soup.find('script', type='text/javascript')

    js_code = script_tag.string

    pattern = r"window\.classified\s*=\s*({.*?});"
    match = re.search(pattern, js_code)

    if match:
        classified_data = match.group(1)
        classified_dict = json.loads(classified_data)

        fields = {
            #'Location': ['property', 'location', 'street'],
            #'Location Number': ['property', 'location', 'number'],
            'Locality': ['property', 'location', 'locality'],
            'Postal Code': ['property', 'location', 'postalCode'],
            'Price': ['transaction', 'sale', 'price'],
            'Type': ['property', 'type'],
            'SubType': ['property', 'subtype'],
            'No Of Bedrooms': ['property', 'bedroomCount'],
            'Living Area': ['property', 'livingRoom', 'surface'],
            'Kitchen Type': ['property', 'kitchen', 'type'],
            'Is Furnished': ['transaction', 'sale', 'isFurnished'],
            'Open Fire': ['property', 'fireplaceExists'],
            'Terrace': ['property', 'hasTerrace'],
            'Terrace Area': ['property', 'terraceSurface'],
            'Garden': ['property', 'hasGarden'],
            'Garden Area': ['property', 'gardenSurface'],
            'Surface of the land': ['property', 'netHabitableSurface'],
            'Surface area of the plot of land': ['property', 'land', 'surface'],
            'Number of facades': ['property', 'building', 'facadeCount'],
            'Swimming Pool': ['property', 'hasSwimmingPool'],
            'State of Building': ['property', 'building', 'condition']
        }

        url_output = {}

        for field_name, field_keys in fields.items():
            field_value = get_field_value(classified_dict, *field_keys)
            if isinstance(field_value, bool):
                field_value = convert_boolean(field_value)
            url_output[field_name] = field_value or ''

        return identity, url_output
    else:
        return identity, {'Error': "No window.classified data found in the JavaScript code"}

# Create a ThreadPoolExecutor with maximum 5 concurrent threads
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks for each URL
    future_to_url = {executor.submit(process_url, url): url for url in urls}

    # Process the completed tasks
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            identity, url_output = future.result()
            output_dict[identity] = url_output
        except Exception as e:
            output_dict[identity] = {'Error': str(e)}
        identity += 1


output_file = r'C:\Users\PC\Desktop\Projects\challenge-collecting-data\output_new.csv'


# Create a list to hold the data rows
rows = []

# Iterate over the output_dict and append the data rows
for identity, url_output in output_dict.items():
    row = {'URL Identity': identity}
    for field_name, field_value in url_output.items():
           row[field_name] = field_value
    rows.append(row)


df = pd.DataFrame(rows)

df.to_csv(output_file, index=False)

print(f"CSV file saved at: {output_file}")

# End the timer
end_time = time.time()

execution_time = end_time - start_time

print(f"Execution time: {execution_time} seconds")

+++ property_details_csv.py
"""
Property Details Scraper

This module scrapes detailed property information from Immoweb.be URLs
and exports the data to a CSV file.

Usage:
    python property_details_csv.py [--num-properties N] [--output FILE]
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Tuple
import time
import pandas as pd
import argparse
import logging
from pathlib import Path
import sys

# Import property links module
import get_property_links as gpl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('property_scraper.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


def get_field_value(classified_dict: Dict[str, Any], *keys: str) -> Optional[Any]:
    """
    Safely extract nested dictionary values.

    Args:
        classified_dict: The dictionary to extract values from
        *keys: Variable number of keys to traverse

    Returns:
        The value at the nested key path, or None if not found
    """
    value = classified_dict
    for key in keys:
        if value is None or not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def convert_boolean(value: Optional[bool]) -> str:
    """Convert boolean to string representation."""
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def process_url(
    url: str,
    session: requests.Session,
    identity: int,
    fields: Dict[str, List[str]]
) -> Tuple[int, Dict[str, Any]]:
    """
    Process a single property URL and extract data.

    Args:
        url: The property URL to scrape
        session: Requests session for connection pooling
        identity: Unique identifier for the property
        fields: Dictionary mapping field names to key paths

    Returns:
        Tuple of (identity, extracted_data_dict)
    """
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        script_tag = soup.find('script', type='text/javascript')

        if not script_tag or not script_tag.string:
            logger.warning(f"No script tag found for URL: {url}")
            return identity, {'Error': "No script tag found"}

        js_code = script_tag.string
        pattern = r"window\.classified\s*=\s*({.*?});"
        match = re.search(pattern, js_code, re.DOTALL)

        if match:
            classified_data = match.group(1)
            classified_dict = json.loads(classified_data)

            url_output = {}
            for field_name, field_keys in fields.items():
                field_value = get_field_value(classified_dict, *field_keys)

                # Handle boolean conversions
                if isinstance(field_value, bool):
                    field_value = convert_boolean(field_value)

                url_output[field_name] = field_value if field_value is not None else ''

            return identity, url_output
        else:
            logger.warning(f"No window.classified data found for URL: {url}")
            return identity, {'Error': "No window.classified data found"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for URL {url}: {str(e)}")
        return identity, {'Error': f"Request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for URL {url}: {str(e)}")
        return identity, {'Error': f"JSON parse error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error processing URL {url}: {str(e)}")
        return identity, {'Error': str(e)}


def scrape_properties(
    num_properties: int = 300,
    output_file: Optional[str] = None,
    max_workers: int = 5
) -> str:
    """
    Main function to scrape property details.

    Args:
        num_properties: Number of properties to scrape
        output_file: Path to output CSV file
        max_workers: Maximum concurrent threads

    Returns:
        Path to the saved CSV file
    """
    start_time = time.time()
    logger.info(f"Starting property scraper for {num_properties} properties")

    # Get URLs
    logger.info("Fetching property URLs...")
    urls = gpl.scrape_all_pages(num_properties)
    logger.info(f"Found {len(urls)} property URLs")

    if not urls:
        raise ValueError("No URLs found. Check your internet connection or the website structure.")

    # Define fields to extract
    fields = {
        'Locality': ['property', 'location', 'locality'],
        'Postal Code': ['property', 'location', 'postalCode'],
        'Price': ['transaction', 'sale', 'price'],
        'Property Type': ['property', 'type'],
        'SubType': ['property', 'subtype'],
        'No Of Bedrooms': ['property', 'bedroomCount'],
        'Living Area': ['property', 'livingRoom', 'surface'],
        'Kitchen Type': ['property', 'kitchen', 'type'],
        'Is Furnished': ['transaction', 'sale', 'isFurnished'],
        'Open Fire': ['property', 'fireplaceExists'],
        'Terrace': ['property', 'hasTerrace'],
        'Terrace Area': ['property', 'terraceSurface'],
        'Garden': ['property', 'hasGarden'],
        'Garden Area': ['property', 'gardenSurface'],
        'Surface of the land': ['property', 'netHabitableSurface'],
        'Surface area of the plot of land': ['property', 'land', 'surface'],
        'Number of facades': ['property', 'building', 'facadeCount'],
        'Swimming Pool': ['property', 'hasSwimmingPool'],
        'State of Building': ['property', 'building', 'condition']
    }

    # Create session for connection pooling
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    output_dict = {}

    # Process URLs with thread pool
    logger.info(f"Processing URLs with {max_workers} concurrent workers...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(process_url, url, session, idx, fields): url
            for idx, url in enumerate(urls, start=1)
        }

        completed = 0
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                identity, url_output = future.result()
                output_dict[identity] = url_output
                completed += 1

                if completed % 50 == 0:
                    logger.info(f"Processed {completed}/{len(urls)} properties")

            except Exception as e:
                logger.error(f"Failed to process URL {url}: {str(e)}")
                output_dict[len(output_dict) + 1] = {'Error': str(e)}

    session.close()

    # Convert to DataFrame
    rows = []
    for identity, url_output in sorted(output_dict.items()):
        row = {'URL Identity': identity}
        row.update(url_output)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Determine output file path
    if output_file is None:
        output_file = Path(__file__).parent / 'output_new.csv'
    else:
        output_file = Path(output_file)

    # Ensure directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    df.to_csv(output_file, index=False)
    logger.info(f"CSV file saved at: {output_file.absolute()}")

    # Calculate execution time
    execution_time = time.time() - start_time
    logger.info(f"Execution time: {execution_time:.2f} seconds")
    logger.info(f"Successfully processed {len([r for r in rows if 'Error' not in r])}/{len(rows)} properties")

    return str(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scrape property details from Immoweb.be'
    )
    parser.add_argument(
        '--num-properties', '-n',
        type=int,
        default=300,
        help='Number of properties to scrape (default: 300)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output CSV file path (default: output_new.csv)'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=5,
        help='Maximum concurrent workers (default: 5)'
    )

    args = parser.parse_args()

    try:
        output_path = scrape_properties(
            num_properties=args.num_properties,
            output_file=args.output,
            max_workers=args.workers
        )
        print(f"\n✓ Scraping completed successfully!")
        print(f"  Output file: {output_path}")
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        sys.exit(1)
