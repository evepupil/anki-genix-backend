import os
import csv
import json
import time
import genanki
import random
from typing import List, Dict, Any, Union
from .logger import get_logger

logger = get_logger(name="utils.anki_exporter")

class AnkiExporter:
    """
    Anki导出工具，支持将数据库格式的闪卡转换为Anki可导入的格式

    数据格式说明：
    每个卡片包含以下字段：
    - id: 卡片ID (UUID)
    - card_type: 卡片类型 ('basic', 'cloze', 'multiple_choice')
    - card_data: 卡片数据 (JSONB)，不同类型存储不同结构
    - is_deleted: 是否已删除
    - section_id: 章节ID（可选）
    - tags: 标签数组（可选）

    card_data 结构：
    - basic: {question: str, answer: str}
    - cloze: {text: str, cloze_items: list}
    - multiple_choice: {question: str, options: list, correct_index: int}
    """

    # 基础问答卡模型
    BASIC_MODEL = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        'Basic Card',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    # 填空卡模型
    CLOZE_MODEL = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        'Cloze Card',
        model_type=genanki.Model.CLOZE,
        fields=[
            {'name': 'Text'},
            {'name': 'Extra'},
        ],
        templates=[
            {
                'name': 'Cloze Card',
                'qfmt': '{{cloze:Text}}',
                'afmt': '{{cloze:Text}}<hr id="extra">{{Extra}}',
            },
        ])

    # 选择题卡模型
    CHOICE_MODEL = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        'Multiple Choice Card',
        fields=[
            {'name': 'Question'},
            {'name': 'Options'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}<br><br>{{Options}}',
                'afmt': '{{FrontSide}}<hr id="answer">正确答案: {{Answer}}',
            },
        ])

    def __init__(self, output_dir='exports'):
        """
        初始化Anki导出工具

        :param output_dir: 导出文件保存目录
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        logger.info(f"初始化AnkiExporter，输出目录: {output_dir}")

    def json_to_anki_pkg(self, deck_name: str, cards_data: List[Dict[str, Any]]) -> str:
        """
        将数据库格式的闪卡转换为Anki包文件(.apkg)
        自动按卡片类型分组处理，支持混合类型导出

        :param deck_name: 牌组名称
        :param cards_data: 闪卡数据列表，每个元素包含 card_type 和 card_data 字段
        :return: 生成的Anki包文件路径
        """
        logger.info(f"开始转换{len(cards_data)}张卡片为Anki包")

        # 创建随机ID的牌组
        deck_id = random.randrange(1 << 30, 1 << 31)
        deck = genanki.Deck(deck_id, deck_name)

        # 按卡片类型分组，过滤已删除的卡片
        basic_cards = [c for c in cards_data if c.get('card_type') == 'basic' and not c.get('is_deleted', False)]
        cloze_cards = [c for c in cards_data if c.get('card_type') == 'cloze' and not c.get('is_deleted', False)]
        choice_cards = [c for c in cards_data if c.get('card_type') == 'multiple_choice' and not c.get('is_deleted', False)]

        # 添加各类型卡片到牌组
        if basic_cards:
            self._add_basic_cards(deck, basic_cards)
        if cloze_cards:
            self._add_cloze_cards(deck, cloze_cards)
        if choice_cards:
            self._add_choice_cards(deck, choice_cards)

        total_added = len(basic_cards) + len(cloze_cards) + len(choice_cards)
        logger.info(f"已添加 {total_added} 张卡片 (基础:{len(basic_cards)}, 填空:{len(cloze_cards)}, 选择:{len(choice_cards)})")

        # 生成文件名和路径
        timestamp = int(time.time())
        filename = f"{deck_name.replace(' ', '_')}_{timestamp}.apkg"
        filepath = os.path.join(self.output_dir, filename)

        # 生成Anki包文件
        genanki.Package(deck).write_to_file(filepath)
        logger.info(f"成功生成Anki包文件: {filepath}")

        return filepath

    def json_to_csv(self, cards_data: List[Dict[str, Any]]) -> str:
        """
        将数据库格式的闪卡转换为CSV文件
        支持混合类型导出，每行包含卡片类型和内容

        :param cards_data: 闪卡数据列表，每个元素包含 card_type 和 card_data 字段
        :return: 生成的CSV文件路径
        """
        logger.info(f"开始转换{len(cards_data)}张卡片为CSV文件")

        # 生成文件名和路径
        timestamp = int(time.time())
        filename = f"anki_cards_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        # 写入CSV文件（混合类型格式）
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['card_type', 'content', 'tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for card in cards_data:
                # 跳过已删除的卡片
                if card.get('is_deleted', False):
                    continue

                card_type = card.get('card_type', '')
                card_data = card.get('card_data', {})
                content = ''

                # 根据卡片类型格式化内容
                if card_type == 'basic':
                    question = card_data.get('question', '')
                    answer = card_data.get('answer', '')
                    content = f"Q: {question}\nA: {answer}"

                elif card_type == 'cloze':
                    text = card_data.get('text', '')
                    content = text

                elif card_type == 'multiple_choice':
                    question = card_data.get('question', '')
                    options = card_data.get('options', [])
                    correct_index = card_data.get('correct_index', 0)
                    options_text = '\n'.join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
                    correct_answer = f"{chr(65+correct_index)}. {options[correct_index]}" if 0 <= correct_index < len(options) else ''
                    content = f"Q: {question}\n{options_text}\nCorrect: {correct_answer}"

                # 获取标签
                tags = ', '.join(card.get('tags', [])) if card.get('tags') else 'anki_genix'

                writer.writerow({
                    'card_type': card_type,
                    'content': content,
                    'tags': tags
                })

        logger.info(f"成功生成CSV文件: {filepath}")
        return filepath

    def _add_basic_cards(self, deck: genanki.Deck, cards_data: List[Dict[str, Any]]) -> None:
        """
        添加基础问答卡到牌组

        :param deck: Anki牌组对象
        :param cards_data: 卡片数据列表，每个元素的 card_data 包含 {question, answer}
        """
        for card in cards_data:
            card_data = card.get('card_data', {})
            question = card_data.get('question', '')
            answer = card_data.get('answer', '')

            note = genanki.Note(
                model=self.BASIC_MODEL,
                fields=[question, answer],
                tags=['anki_genix']
            )
            deck.add_note(note)

        logger.debug(f"已添加{len(cards_data)}张基础问答卡到牌组")

    def _add_cloze_cards(self, deck: genanki.Deck, cards_data: List[Dict[str, Any]]) -> None:
        """
        添加填空卡到牌组

        :param deck: Anki牌组对象
        :param cards_data: 卡片数据列表，每个元素的 card_data 包含 {text, cloze_items}

        card_data 字段说明：
        - text: 包含填空标记的文本（如 "{{c1::答案}}"）
        - cloze_items: 填空项列表（可选，用于记录原始数据）
        """
        for card in cards_data:
            card_data = card.get('card_data', {})
            text = card_data.get('text', '')

            note = genanki.Note(
                model=self.CLOZE_MODEL,
                fields=[text, ''],
                tags=['anki_genix']
            )
            deck.add_note(note)

        logger.debug(f"已添加{len(cards_data)}张填空卡到牌组")

    def _add_choice_cards(self, deck: genanki.Deck, cards_data: List[Dict[str, Any]]) -> None:
        """
        添加选择题卡到牌组

        :param deck: Anki牌组对象
        :param cards_data: 卡片数据列表，每个元素的 card_data 包含 {question, options, correct_index}

        card_data 字段说明：
        - question: 问题文本
        - options: 选项列表 (list)
        - correct_index: 正确答案的索引 (int, 从0开始)
        """
        for card in cards_data:
            card_data = card.get('card_data', {})
            question = card_data.get('question', '')
            options = card_data.get('options', [])
            correct_index = card_data.get('correct_index', 0)

            # 格式化选项字符串（A. B. C. ...）
            options_str = '<br>'.join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])

            # 获取正确答案文本（索引对应的选项）
            if 0 <= correct_index < len(options):
                answer = f"{chr(65+correct_index)}. {options[correct_index]}"
            else:
                answer = options[0] if options else ''

            note = genanki.Note(
                model=self.CHOICE_MODEL,
                fields=[question, options_str, answer],
                tags=['anki_genix']
            )
            deck.add_note(note)

        logger.debug(f"已添加{len(cards_data)}张选择题卡到牌组")


# 便捷函数
def export_to_anki_pkg(deck_name: str,
                       cards_data: Union[List[Dict[str, Any]], str],
                       output_dir: str = 'exports') -> str:
    """
    将闪卡数据导出为Anki包文件(.apkg)

    :param deck_name: 牌组名称
    :param cards_data: 闪卡数据列表或JSON字符串，每个元素包含 card_type 和 card_data 字段
    :param output_dir: 输出目录
    :return: 生成的Anki包文件路径
    """
    exporter = AnkiExporter(output_dir=output_dir)

    # 如果是字符串，尝试解析为JSON
    if isinstance(cards_data, str):
        try:
            cards_data = json.loads(cards_data)
        except json.JSONDecodeError:
            logger.error("无法解析JSON字符串")
            raise ValueError("无法解析JSON字符串")

    return exporter.json_to_anki_pkg(deck_name, cards_data)


def export_to_csv(cards_data: Union[List[Dict[str, Any]], str],
                 output_dir: str = 'exports') -> str:
    """
    将闪卡数据导出为CSV文件

    :param cards_data: 闪卡数据列表或JSON字符串，每个元素包含 card_type 和 card_data 字段
    :param output_dir: 输出目录
    :return: 生成的CSV文件路径
    """
    exporter = AnkiExporter(output_dir=output_dir)

    # 如果是字符串，尝试解析为JSON
    if isinstance(cards_data, str):
        try:
            cards_data = json.loads(cards_data)
        except json.JSONDecodeError:
            logger.error("无法解析JSON字符串")
            raise ValueError("无法解析JSON字符串")

    return exporter.json_to_csv(cards_data)