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
    Anki导出工具，支持将JSON格式的闪卡转换为Anki可导入的格式
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
    
    def json_to_anki_pkg(self, 
                         deck_name: str, 
                         cards_data: List[Dict[str, Any]], 
                         card_type: str = 'basic_card') -> str:
        """
        将JSON格式的闪卡转换为Anki包文件(.apkg)
        :param deck_name: 牌组名称
        :param cards_data: JSON格式的闪卡数据
        :param card_type: 卡片类型 (basic_card, cloze_card, multiple_choice_card)
        :return: 生成的Anki包文件路径
        """
        logger.info(f"开始转换{len(cards_data)}张{card_type}卡片为Anki包")
        
        # 创建随机ID的牌组
        deck_id = random.randrange(1 << 30, 1 << 31)
        deck = genanki.Deck(deck_id, deck_name)
        
        # 根据卡片类型添加笔记
        if card_type == 'basic_card':
            self._add_basic_cards(deck, cards_data)
        elif card_type == 'cloze_card':
            self._add_cloze_cards(deck, cards_data)
        elif card_type == 'multiple_choice_card':
            self._add_choice_cards(deck, cards_data)
        else:
            logger.error(f"不支持的卡片类型: {card_type}")
            raise ValueError(f"不支持的卡片类型: {card_type}")
        
        # 生成文件名和路径
        timestamp = int(time.time())
        filename = f"{deck_name.replace(' ', '_')}_{card_type}_{timestamp}.apkg"
        filepath = os.path.join(self.output_dir, filename)
        
        # 生成Anki包文件
        genanki.Package(deck).write_to_file(filepath)
        logger.info(f"成功生成Anki包文件: {filepath}")
        
        return filepath
    
    def json_to_csv(self, 
                    cards_data: List[Dict[str, Any]], 
                    card_type: str = 'basic_card') -> str:
        """
        将JSON格式的闪卡转换为CSV文件
        :param cards_data: JSON格式的闪卡数据
        :param card_type: 卡片类型 (basic_card, cloze_card, multiple_choice_card)
        :return: 生成的CSV文件路径
        """
        logger.info(f"开始转换{len(cards_data)}张{card_type}卡片为CSV文件")
        
        # 生成文件名和路径
        timestamp = int(time.time())
        filename = f"anki_cards_{card_type}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # 根据卡片类型写入CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if card_type == 'basic_card':
                fieldnames = ['question', 'answer', 'tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for card in cards_data:
                    writer.writerow({
                        'question': card.get('question', ''),
                        'answer': card.get('answer', ''),
                        'tags': 'anki_genix'
                    })
            
            elif card_type == 'cloze_card':
                fieldnames = ['text', 'extra', 'tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for card in cards_data:
                    writer.writerow({
                        'text': card.get('cloze', ''),
                        'extra': '',
                        'tags': 'anki_genix'
                    })
            
            elif card_type == 'multiple_choice_card':
                fieldnames = ['question', 'options', 'answer', 'tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for card in cards_data:
                    options = card.get('options', [])
                    options_str = '<br>'.join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
                    writer.writerow({
                        'question': card.get('question', ''),
                        'options': options_str,
                        'answer': card.get('answer', ''),
                        'tags': 'anki_genix'
                    })
            
            else:
                logger.error(f"不支持的卡片类型: {card_type}")
                raise ValueError(f"不支持的卡片类型: {card_type}")
        
        logger.info(f"成功生成CSV文件: {filepath}")
        return filepath
    
    def _add_basic_cards(self, deck: genanki.Deck, cards_data: List[Dict[str, Any]]) -> None:
        """添加基础问答卡到牌组"""
        for card in cards_data:
            note = genanki.Note(
                model=self.BASIC_MODEL,
                fields=[card.get('question', ''), card.get('answer', '')],
                tags=['anki_genix']
            )
            deck.add_note(note)
        logger.debug(f"已添加{len(cards_data)}张基础问答卡到牌组")
    
    def _add_cloze_cards(self, deck: genanki.Deck, cards_data: List[Dict[str, Any]]) -> None:
        """添加填空卡到牌组"""
        for card in cards_data:
            note = genanki.Note(
                model=self.CLOZE_MODEL,
                fields=[card.get('cloze', ''), ''],
                tags=['anki_genix']
            )
            deck.add_note(note)
        logger.debug(f"已添加{len(cards_data)}张填空卡到牌组")
    
    def _add_choice_cards(self, deck: genanki.Deck, cards_data: List[Dict[str, Any]]) -> None:
        """添加选择题卡到牌组"""
        for card in cards_data:
            options = card.get('options', [])
            options_str = '<br>'.join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
            note = genanki.Note(
                model=self.CHOICE_MODEL,
                fields=[card.get('question', ''), options_str, card.get('answer', '')],
                tags=['anki_genix']
            )
            deck.add_note(note)
        logger.debug(f"已添加{len(cards_data)}张选择题卡到牌组")


# 便捷函数
def export_to_anki_pkg(deck_name: str, 
                       cards_data: Union[List[Dict[str, Any]], str], 
                       card_type: str = 'basic_card',
                       output_dir: str = 'exports') -> str:
    """
    将闪卡数据导出为Anki包文件(.apkg)
    :param deck_name: 牌组名称
    :param cards_data: JSON格式的闪卡数据或JSON字符串
    :param card_type: 卡片类型 (basic_card, cloze_card, multiple_choice_card)
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
    
    return exporter.json_to_anki_pkg(deck_name, cards_data, card_type)


def export_to_csv(cards_data: Union[List[Dict[str, Any]], str], 
                 card_type: str = 'basic_card',
                 output_dir: str = 'exports') -> str:
    """
    将闪卡数据导出为CSV文件
    :param cards_data: JSON格式的闪卡数据或JSON字符串
    :param card_type: 卡片类型 (basic_card, cloze_card, multiple_choice_card)
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
    
    return exporter.json_to_csv(cards_data, card_type) 