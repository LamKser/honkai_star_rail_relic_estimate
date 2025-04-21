import os
import json
import time
import random
import string
import re
from typing import Optional, Dict, Union

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from Levenshtein import ratio
import numpy as np

from src.utils.check import check_exist_json_file
from src.utils.print import print_title

def scrape_relic_sets(url: str, save_path: str) -> None:
    """
    Scrapes relic set data from a given URL and saves it to a JSON file.

    Args:
        url (str): The URL to scrape relic set data from
        save_path (str): Path where the JSON file will be saved
        
    The data is saved as a JSON file with the following structure:
    {
        "relic_name": {
            "type": str,
            "image": str,
            "2_piece_effect": str,
            "4_piece_effect": str or None
        }
    }
    """
    parent_path = os.path.join("..", os.path.dirname(save_path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    relics = check_exist_json_file(save_path)
    relic_name_list = list(relics.keys())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table with relic sets
        relic_sets = soup.find('div', class_='relic-set-container row row-cols-xxl-2 row-cols-1')
        relic_cols = relic_sets.find_all('div', class_='col')
        
        print_title("Scraping relic sets")
        for i, relic in tqdm(
            enumerate(relic_cols, start=1), 
            total=len(relic_cols)
        ):
            relic_image_url = "https://www.prydwen.gg" + relic.find_all("img")[-1]["src"]
            relic_data = relic.find("div", class_="hsr-relic-data")
            relic_name = relic_data.find("h4").get_text(strip=True).lower().replace(' ', '_')
            relic_name = re.split(r'[^a-zA-Z0-9\s]', relic_name)
            relic_name = list(filter(lambda x: x.strip(), relic_name))
            relic_name = '_'.join(relic_name)
            if (len(relic_name_list) > 0) and (relic_name in relic_name_list):
                continue
            else:
                print(f"{i}. \"{relic_name}\" doesn't exist. ADDING")

            relic_type = relic_data.find("div", class_="hsr-relic-info").find("strong").get_text(strip=True).lower().replace(' ', '_')
            relic_content = relic.find("div", class_="hsr-relic-content").find("div").find_all("div")
            
            relic_2_set = relic_content[0].get_text(strip=True)
            if len(relic_content) == 2:
                relic_4_set = relic_content[1].get_text(strip=True)
            
            relics[relic_name] = {
                "type": relic_type,
                "image": relic_image_url,
                "2_piece_effect": relic_2_set,
                "4_piece_effect": relic_4_set if len(relic_content) == 2 else None
            }
            # break
        # Save to JSON file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(relics, f, indent=4, ensure_ascii=False)

        print("Relic data has been successfully scraped and saved!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def download_images(json_path: str, save_dir: str) -> None:
    """
    Downloads images from URLs specified in a JSON file and saves them to a directory.
    
    Args:
        json_path (str): Path to the JSON file containing image URLs
        save_dir (str): Directory where the images will be saved
        
    The JSON file should have a structure where each entry contains an 'image' field
    with the URL to download. Images are saved with the key name from the JSON file,
    with special characters removed. Adds random delays between downloads to avoid
    overwhelming the server.
    """
    # Load the JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ensure the save directory exists
    exist_images = list()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:
        exist_images = os.listdir(save_dir)

    print_title("Downloading images")
    # Iterate through the relic sets and download images
    for i, (name, info) in enumerate(data.items(), start=1):
        name = re.split(r'[^a-zA-Z0-9\s]', name)
        name = list(filter(lambda x: x.strip(), name))
        name = '_'.join(name)
        if (len(exist_images) > 0) and (f"{name}.png" in exist_images):
            continue

        image_url = info.get("image")
        if image_url:
            try:
                # Random delay between 3 and 6 seconds
                delay = random.uniform(1, 3)
                time.sleep(delay)

                # Get the image content
                response = requests.get(image_url, stream=True)
                response.raise_for_status()

                # Save the image to the specified directory
                image_path = os.path.join(save_dir, f"{name}.png")
                with open(image_path, 'wb') as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)

                print(f"{i}. Downloaded: {name} (Delay: {delay:.2f} seconds)")
            except Exception as e:
                print(f"Failed to download {name}: {e}")
    print(f"All images have been downloaded at \"{save_dir}\"!")


def scrape_relic_stats(url: str, save_path: str) -> None:
    """
    Scrapes relic stat information from a given URL and saves it to a JSON file.
    
    Args:
        url (str): The URL to scrape relic stat data from
        save_path (str): Path where the JSON file will be saved
        
    Extracts information about main stats available for each relic slot and possible
    sub stats. The data is saved as a JSON file with the structure:
    {
        "main_stat": {
            "head": [list of possible main stats],
            "hands": [list of possible main stats],
            ...
        },
        "sub_stat": [list of all possible sub stats]
    }
    """
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
        
        print_title("Scraping relic stats")
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


def scrape_lightcones(url_info: str, url_image: str, save_path: str) -> None:
    """
    Scrapes lightcone data from two URLs (info and images) and saves it to a JSON file.
    
    Args:
        url_info (str): URL to scrape lightcone information from
        url_image (str): URL to scrape lightcone images from
        save_path (str): Path where the JSON file will be saved
        
    First collects image URLs from url_image, then matches them with lightcone
    information from url_info using name similarity. The data is saved as a JSON
    file with the structure:
    {
        "lightcone_name": {
            "image": str,
            "rate": str,
            "type": str,
            "ability": str
        }
    }
    """
    parent_path = os.path.join("..", os.path.dirname(save_path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    lightcones = check_exist_json_file(save_path)
    exist_lightcone_list = list(lightcones.keys())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Get lightcone
    lightcone_image_dict = dict()
    response = requests.get(url_image, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    lightcone_body_html = soup.find("div", class_="clearfix")
    lightcone_list_html = lightcone_body_html.find_all("div")
    for i in range(0, len(lightcone_list_html), 3):
        lightcone_image_url = lightcone_list_html[i].find("img")["src"]
        lightcone_name = lightcone_list_html[i + 2].get_text().strip().split('\n')[0].strip()
        lightcone_name = lightcone_name.replace(' ', '_').lower()
        lightcone_image_dict[lightcone_name] = lightcone_image_url
        # break
    lightcone_name_list = list(lightcone_image_dict.keys())

    # Get lightcone info
    response = requests.get(url_info, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    lightcone_sets = soup.find('div', class_='relic-set-container row row-cols-xxl-2 row-cols-1')
    lightcone_cols = lightcone_sets.find_all('div', class_='col')

    print_title("Scraping lightcones")
    for i, lightcone in tqdm(
        enumerate(lightcone_cols, start=1), 
        total=len(lightcone_cols)
    ):
        
        lightcone_data = lightcone.find("div", class_="hsr-cone-data")
        lightcone_name = lightcone_data.find("h4").get_text(strip=True).lower().replace(' ', '_')
        lightcone_name = re.split(r'[^a-zA-Z0-9\s]', lightcone_name)
        lightcone_name = list(filter(lambda x: x.strip(), lightcone_name))
        lightcone_name = '_'.join(lightcone_name)
        if (len(exist_lightcone_list) > 0) and (lightcone_name in exist_lightcone_list):
                continue
        else:
            print(f"{i}. \"{lightcone_name}\" doesn't exist. ADDING")

        lightcone_type = lightcone_data.find("div", class_="hsr-cone-info").find_all("strong")
        lightcone_rate = lightcone_type[0].get_text(strip=True)[0].lower()
        lightcone_path = lightcone_type[1].get_text(strip=True).lower()

        lightcone_content = lightcone.find("div", class_="hsr-cone-content").get_text().strip()
        
        ## Find closest lightcone name
        name_ratio_list = [ratio(lightcone_name, name) for name in lightcone_name_list]
        max_index = np.argmax(name_ratio_list)
        lightcone_name_max_ratio = lightcone_name_list[max_index]
        
        lightcones[lightcone_name] = {
            "image": lightcone_image_dict[lightcone_name_max_ratio],
            "rate": lightcone_rate,
            "type": lightcone_path,
            "ability": lightcone_content,
        }
    # Save to JSON file
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(lightcones, f, indent=4, ensure_ascii=False)

    print("Relic data has been successfully scraped and saved!")


def scarpe_character_info(url: str) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    Scrapes detailed information about a character from a specific URL.
    
    Args:
        url (str): URL of the character page to scrape
        
    Returns:
        dict: A dictionary containing character information with the following structure:
            {
                "name": str,
                "image": str,
                "rate": str,
                "element": str,
                "path": str,
                "sub_stat": {stat_name: value},
                "basic_stat": {stat_name: value}
            }
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    character_info = dict()

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Name
        character_name = url.split("/")[-1].replace("-", "_").lower()
        character_info["name"] = character_name

        # Image url
        image_area = soup.find('div', class_='right-image')
        image_url = "https://www.prydwen.gg" + image_area.findChildren("img")[2]["src"]
        character_info["image"] = image_url

        # Character Intro
        character_intro = soup.find('div', class_='character-intro')
        character_path = character_intro.find_all("strong")[1:4]

        # Rate
        character_rate = character_path[0].get_text(strip=True)[0]
        character_info["rate"] = character_rate

        # Element
        character_element = character_path[1].get_text(strip=True).lower()
        character_info["element"] = character_element

        # Path
        character_type = character_path[2].get_text().strip().split(' ')[-1].lower()
        character_info["path"] = character_type

        # Find minor traces
        minor_traces = soup.find('div', class_='content-header')
        minor_traces_info = minor_traces.find_next("div", class_="smaller-traces").find_all("div", class_="col")

        character_info["sub_stat"] = dict()
        for trace in minor_traces_info:
            trace_stat = trace.get_text(strip=True).split('+')
            trace_stat[0] = trace_stat[0].lower().strip().replace(' ', '_')
            character_info["sub_stat"][trace_stat[0]] = trace_stat[1].strip()
        
        # Basic stat
        character_info["basic_stat"] = dict()
        basic_box = soup.find("div", class_="stat-box")
        all_basic_stat = basic_box.find_all("div", class_="info-list-row")
        for a in all_basic_stat:
            text = a.get_text().lower()
            stat = re.split(r'([A-Za-z]+)(\d+)', text)
            character_info["basic_stat"][stat[1]] = stat[2]
    except Exception as e:
        print(f"Error parsing lightcone info: {e} - URL: {url}")
    
    return character_info


def scrape_characters(url: str, save_path: str) -> None:
    """
    Scrapes character data from a given URL and saves it to a JSON file.
    
    Args:
        url (str): The URL to scrape character data from
        save_path (str): Path where the JSON file will be saved
        
    Scrapes basic information about all characters from the main character list page,
    then collects detailed information for each character. The data is saved as a JSON
    file with the structure:
    {
        "character_name": {
            "image": str,
            "rate": str,
            "element": str,
            "path": str,
            "sub_stat": {stat_name: value},
            "basic_stat": {stat_name: value}
        }
    }
    """
    parent_path = os.path.join("..", os.path.dirname(save_path))
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    character_dict = check_exist_json_file(save_path)
    exist_character_list = list(character_dict.keys())

    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    all_characters = soup.find('div', class_='employees-container hsr-cards').find_all("div", class_="avatar-card card")
    
    print_title("Scraping characters")
    for i, card in tqdm(
        enumerate(all_characters, start=1), 
        total=len(all_characters)
    ):
        
        future_character = card.find("span", class_="tag future")

        if not future_character:
            character_url = "https://www.prydwen.gg" + card.find('a')["href"]
            character_name = character_url.split("/")[-1].replace("-", "_").lower()
            if (len(exist_character_list) > 0) and (character_name in exist_character_list):
                continue
            else:
                print(f"{i}. {character_name} doesn't exist. ADDING")

            character_name = url.split("/")[-1].replace("-", "_").lower()
            character_info = scarpe_character_info(character_url)
            character_name = character_info.pop("name")
            character_dict[character_name] = character_info
        else:
            name = card.find("span", class_="emp-name").get_text()
            print(f"{i}. Future Character: {name}")
            continue
    # Save the extracted data to a JSON file
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(character_dict, f, indent=4, ensure_ascii=False)

    print(f"Character data have been successfully scraped and saved to {save_path}!")

