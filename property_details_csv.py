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

 