import os
import yaml

def load_prompt(card_type, lang="zh"):
    base_dir = os.path.dirname(__file__)
    # 根据 card_type 选择不同的提示词文件
    if card_type == "catalog_analysis":
        yaml_path = os.path.join(base_dir, "prompts_catalog.yaml")
    elif card_type in ["summarize_text", "summarize_file"]:
        yaml_path = os.path.join(base_dir, "prompts_summary.yaml")
    else:
        yaml_path = os.path.join(base_dir, "prompts_flashcard.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    card_data = data.get(card_type)
    if not card_data:
        # summary prompt为纯字符串，非多语言结构
        if card_type in ["summarize_text", "summarize_file"]:
            return {"prompt": data[card_type]}
        raise ValueError(f"Card type '{card_type}' not found in {os.path.basename(yaml_path)}")
    return card_data.get(lang) or card_data.get("zh") 