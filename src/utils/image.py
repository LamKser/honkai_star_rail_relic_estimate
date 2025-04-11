import json
from glob import glob
import os
from os.path import split, join

import numpy as np
from PIL import Image, ImageDraw
from Levenshtein import ratio
from tqdm import tqdm


def create_darker_to_lighter_gradient(width: int, height: int, color: str = "blue") -> Image.Image:
    """
    Creates a vertical gradient image transitioning from darker to lighter tones.
    
    Args:
        width (int): Width of the gradient image
        height (int): Height of the gradient image
        color (str): Color scheme to use ("purple", "blue", or "yellow")
        
    Returns:
        PIL.Image: Generated gradient image with dark on top and light on bottom
    """
    color_list = {
        "purple": {
            "bottom": (60, 20, 90),
            "top": (210, 160, 255)
        },
        "blue": {
            "bottom": (20, 30, 80),
            "top": (170, 210, 255)
        },
        "yellow": {
            "bottom": (110, 80, 45),
            "top": (245, 215, 130)
        }
    }
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    
    for y in range(height):
        ratio = (height - y) / height
        r = int(color_list[color]["top"][0] * ratio + color_list[color]["bottom"][0] * (1 - ratio))
        g = int(color_list[color]["top"][1] * ratio + color_list[color]["bottom"][1] * (1 - ratio))
        b = int(color_list[color]["top"][2] * ratio + color_list[color]["bottom"][2] * (1 - ratio))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Flip vertically: dark on top, light on bottom
    flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return flipped_image


def overlay_image(image_1: Image.Image, image_2: Image.Image) -> Image.Image:
    """
    Overlays image_1 onto another image_2 using alpha compositing.
    
    Args:
        image_1 (PIL.Image): Foreground image to overlay (must have alpha channel)
        image_2 (PIL.Image): Background image to be overlayed upon
        
    Returns:
        PIL.Image: Combined image with image_1 overlaid on image_2
    """
    # image_1 = Image.open(image_1_path).convert("RGBA")
    # image_2 = Image.open(image_2_path).convert("RGBA")

    # Overlay character on top of background
    combined = Image.alpha_composite(image_2, image_1)

    # Save the final image
    return combined


def overlay_character_background(character_info_path: str, character_image_dir: str,
                                purple_path: str, yellow_path: str,
                                save: str) -> None:
    """
    Overlays character images onto appropriate background based on their rarity.
    
    Args:
        character_info_path (str): Path to JSON file containing character information
        character_image_dir (str): Directory containing character images
        purple_path (str): Path to purple background image for 4-star characters
        yellow_path (str): Path to yellow background image for 5-star characters
        save (str): Directory to save the output images
    """
    if not os.path.exists(save):
        os.makedirs(save)

    character_images = glob(os.path.join(character_image_dir, '*'))
    yellow_background = Image.open(yellow_path).convert("RGBA")
    purple_background = Image.open(purple_path).convert("RGBA")

    with open(character_info_path, 'r', encoding="utf-8") as f:
        js = json.load(f)

        character_name_keys = js.keys()
        for name in tqdm(character_name_keys, total=len(character_name_keys), desc="Overlaying"):
            name_ratio_list = [ratio(split(path)[-1], name) for path in character_images]
            max_index = np.argmax(name_ratio_list)
            target_character_path = character_images[max_index]

            character_image = Image.open(target_character_path).convert("RGBA")
            if js[name]["rate"] == "4":
                background_image = purple_background
            else:
                background_image = yellow_background

            overlay_img = overlay_image(character_image, background_image)
            overlay_img.save(join(save, f"{name}.png"))


def overlay_relic_background(relic_info_path: str, relic_image_dir: str,
                           yellow_path: str, save: str) -> None:
    """
    Overlays relic images onto a yellow background.
    
    Args:
        relic_info_path (str): Path to JSON file containing relic information
        relic_image_dir (str): Directory containing relic images
        yellow_path (str): Path to yellow background image
        save (str): Directory to save the output images
    """
    if not os.path.exists(save):
        os.makedirs(save)

    relic_images = glob(os.path.join(relic_image_dir, '*'))
    yellow_background = Image.open(yellow_path).convert("RGBA")

    for path in tqdm(relic_images, total=len(relic_images), desc="Overlaying"):
        fname = split(path)[-1]
        relic_image = Image.open(path).convert("RGBA")
        overlay_img = overlay_image(relic_image, yellow_background)
        overlay_img.save(join(save, fname))