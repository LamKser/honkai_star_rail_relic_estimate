import os
import json
import time
import random
import string
import asyncio

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import aiohttp


def scrape_relic_sets(url, save_path):
    parent_path = os.path.join("..", os.path.dirname(save_path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    relic_sets = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table with relic sets
        tables = soup.find_all('table', class_='a-table a-table a-table')
        relic_type = ["cavern", "planar_ornament"]
        for re_type, table in zip(relic_type, tables):
            # Skip header row
            rows = table.find_all('tr')[1:]

            for row in tqdm(rows, total=len(rows), desc="Scraping relic sets"):
                cols = row.find_all('td')
                img_url = cols[0].find('img')['data-src']

                relic_name = cols[0].get_text().strip()
                translator = str.maketrans('', '', string.punctuation)
                clean_text = relic_name.translate(translator)
                relic_name = clean_text.split()
                relic_name = '_'.join(relic_name).lower()

                relic_effect = cols[1].get_text().strip().split('\n')
            
                relic_sets[relic_name] = {
                    "type": re_type,
                    "image": img_url,
                    "2_piece_effect": relic_effect[0].strip(),
                    "4_piece_effect": relic_effect[1].strip() if len(relic_effect) > 1 else None,
                }

        # Save to JSON file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(relic_sets, f, indent=4, ensure_ascii=False)

        print("Relic data has been successfully scraped and saved!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def download_images(json_path, save_dir):
    # Load the JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        relic_data = json.load(f)

    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Iterate through the relic sets and download images
    for i, (relic_name, relic_info) in enumerate(relic_data.items(), start=1):
        image_url = relic_info.get("image")
        if image_url:
            try:
                # Random delay between 3 and 6 seconds
                delay = random.uniform(1, 3)
                time.sleep(delay)

                # Get the image content
                response = requests.get(image_url, stream=True)
                response.raise_for_status()

                # Save the image to the specified directory
                image_path = os.path.join(save_dir, f"{relic_name}.png")
                with open(image_path, 'wb') as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)

                print(f"{i}. Downloaded: {relic_name} (Delay: {delay:.2f} seconds)")
            except Exception as e:
                print(f"Failed to download {relic_name}: {e}")


def scrape_relic_stats(url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing "Main Stat" and "Sub Stat"
        table = soup.find_all('table', {'class': 'wikitable'})
        main_stat_name = table[0].find_all("th")
        main_name = main_stat_name[2:]
        main_name = list(map(lambda x: x.get_text(strip=True).lower(), main_name)) # ['head', 'hands', 'body', 'feet', 'planarsphere', 'linkrope']
        
        main_dict = dict()
        for name in main_name:
            main_dict[name] = list()
        main_stat_table = table[0].find_all("td")
        
        for i in range(0, len(main_stat_table), 7):
            main_stat = main_stat_table[i].get_text(strip=True).lower()
            main_stat = main_stat.replace(' ', '_')
            for j in range(1, 7):
                check_stat = main_stat_table[i + j].get_text(strip=True).lower()[2:]
                if check_stat == "yes":
                    main_dict[main_name[j - 1]].append(main_stat)
        # pprint(main_dict)

        sub_stat_list = table[-1].find_all("td")[::4]
        sub_stat_list = list(map(lambda x: x.get_text(strip=True).lower().replace(' ', '_'), sub_stat_list)) # ['spd', 'hp', 'atk', 'def', 'hp%', 'atk%', 'def%', 'break_effect%', 'effect_hit_rate%', 'effect_res%', 'crit_rate%', 'crit_dmg%']

        relic_stats = {
            "main_stat": main_dict,
            "sub_stat": sub_stat_list
        }
        # pprint(relic_stats)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(relic_stats, f, indent=4, ensure_ascii=False)

        print(f"Relic stats have been successfully scraped and saved to {save_path}!")

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def scrape_lightcone_info(url, target_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table with the specific title as first row
        tables = soup.find_all('table')
        target_table = None
        for table in tables:
            # Get the first row of the table
            first_row = table.find('tr')
            if first_row:
                # Extract the text from the first row
                first_row_text = first_row.get_text(strip=True)

                # Check if the target text is in the first row
                if target_name == first_row_text:
                    target_table = table
                    break
        
        rows = target_table.find_all('tr')
        lightcone_name = rows[0].get_text(strip=True).split()
        lightcone_name = '_'.join(lightcone_name).lower()
        lightcone_image_url = rows[1].find('img')['data-src']
        lightcone_image_rate = len(rows[2].get_text().split('\n\n\n')[-2].strip() )
        lightcone_type = rows[3].get_text().split('\n\n')[1].strip().split()
        lightcone_type = '_'.join(lightcone_type).lower()
        lightcone_ability = rows[4].find_all('td')[0]

        # Remove the first <b> tag
        first_b_tag = lightcone_ability.find('b')
        if first_b_tag:
            first_b_tag.extract() 
        lightcone_ability = lightcone_ability.get_text().strip()

        lightcone_info = {
            "name": lightcone_name,
            "image": lightcone_image_url,
            "rate": lightcone_image_rate,
            "type": lightcone_type,
            "ability": lightcone_ability,
        }
    except Exception as e:
        print(f"Error parsing lightcone info: {e} - URL: {url}")

    return lightcone_info


def scrape_light_cones(url, save_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    lightcone_dict = dict()

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing "Available Light Cones"
        target_tag = soup.find(lambda tag: tag.string == "Available Light Cones")
        table = target_tag.find_next('table', class_="a-table a-table a-table")
        rows = table.find_all('tr')[1:]

        for row in tqdm(rows, total=len(rows), desc="Scraping light cones"):
            target_name = row.find('a').get_text(strip=True)
            lightcone_url = row.find('a')["href"]
            lightcone_info = scrape_lightcone_info(lightcone_url, target_name)
            lightcone_name = lightcone_info.pop("name")
            lightcone_dict[lightcone_name] = lightcone_info
            
        # Save the extracted data to a JSON file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(lightcone_dict, f, indent=4, ensure_ascii=False)

        print(f"Light Cones data have been successfully scraped and saved to {save_path}!")

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"An error occurred: {e} - URL: {lightcone_url}")
