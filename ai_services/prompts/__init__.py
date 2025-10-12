import os
import yaml

def load_prompt(card_type, lang="zh", form="text", mode="topic"):
    """
    加载提示词模板

    参数:
        card_type: 卡片类型 (basic_card, cloze_card, multiple_choice_card, catalog_analysis, summarize_text, summarize_file)
        lang: 语言 (zh, en, ja)
        form: 输入形式 (text: 文本输入, file: 文件上传)
        mode: 生成模式 (topic: 话题模式, full: 全文模式, section: 章节模式)

    返回:
        包含 prompt 字段的字典
    """
    base_dir = os.path.dirname(__file__)

    # 根据 card_type 选择不同的提示词文件
    if card_type == "catalog_analysis":
        yaml_path = os.path.join(base_dir, "prompts_catalog.yaml")
    elif card_type in ["summarize_text", "summarize_file"]:
        yaml_path = os.path.join(base_dir, "prompts_summary.yaml")
    else:
        # 闪卡生成类型：根据 form 参数选择文本或文件提示词文件
        if form == "file":
            yaml_path = os.path.join(base_dir, "prompts_flashcard_file.yaml")
        else:
            yaml_path = os.path.join(base_dir, "prompts_flashcard_text.yaml")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # 特殊处理：summary prompt为纯字符串，非多语言结构
    if card_type in ["summarize_text", "summarize_file"]:
        return {"prompt": data[card_type]}

    # 获取卡片类型数据
    card_data = data.get(card_type)
    if not card_data:
        raise ValueError(f"Card type '{card_type}' not found in {os.path.basename(yaml_path)}")

    # 获取模式数据 (topic/full/section)
    mode_data = card_data.get(mode)
    if not mode_data:
        raise ValueError(f"Mode '{mode}' not found for card type '{card_type}' in {os.path.basename(yaml_path)}")

    # 获取语言数据
    lang_data = mode_data.get(lang) or mode_data.get("zh")
    if not lang_data:
        raise ValueError(f"Language '{lang}' not found for card type '{card_type}' mode '{mode}' in {os.path.basename(yaml_path)}")

    return lang_data 