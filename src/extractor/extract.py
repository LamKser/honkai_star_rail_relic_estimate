from typing import List, Dict, Optional
import json
from time import sleep

from tqdm import tqdm

from src.extractor import LLMExtractor


def extract_lightcone(api_key: str, url: str, model: str,
                    prompt: str,
                    lightcone_path: str,
                    wait: Optional[int] = None) -> List[Dict[str, str]]:
    sub_stat_list = list()
    llm = LLMExtractor(api_key, url)

    with open(lightcone_path, 'r', encoding="utf-8") as f:
        js = json.load(f)
        lightcone_name = js.keys()
        for name in tqdm(lightcone_name, total=len(lightcone_name), desc="Extract sub stat from lightcone"):
            user = js[name]["ability"]
            data = js[name]
            del data["image"]
            del data["rate"]
            del data["type"]
            info = js[name]["ability"]

            response, usage = llm.extract(prompt, info, model)
            sub_stat_list.append({
                "name": name,
                "input": user,
                "output": response
            })
            if wait: sleep(wait)
    return sub_stat_list
