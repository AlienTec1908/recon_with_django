import json
from pathlib import Path
import xmltodict

def xml_to_json(xml_path: Path, json_path: Path):
    with xml_path.open("r", encoding="utf-8", errors="ignore") as f:
        xml_data = xmltodict.parse(f.read())

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(xml_data, f, indent=2)

