import os
import yaml

def load_prompt(card_type, lang="zh"):
    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(base_dir, "prompts.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # 优先取指定语言，否则回退到中文
    card_data = data.get(card_type)
    if not card_data:
        raise ValueError(f"Card type '{card_type}' not found in prompts.yaml")
    return card_data.get(lang) or card_data.get("zh") 