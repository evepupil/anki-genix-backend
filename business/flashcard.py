from ai_services.workflows import CatalogAnalysisWorkflow, FlashcardGenerateWorkflow
from utils.logger import get_logger

class FlashcardBusiness:
    def __init__(self, ai_service=None):
        if ai_service is None:
        # 如果没有提供ai_service，使用默认的
            from ai_services.ai_deepseek import DeepseekAIService
            ai_service = DeepseekAIService()
        self.ai_service = ai_service
        self.logger = get_logger(name="business.flashcard")
        self.logger.info("初始化 FlashcardBusiness")

    def _save_flashcard_result(self, task_id: str, cards: list, source_type: str, catalog_id: str = None) -> dict:
        """
        保存闪卡结果到数据库

        Args:
            task_id: 任务ID
            cards: 生成的闪卡列表
            source_type: 来源类型（text/file/web）
            catalog_id: 大纲ID（可选）

        Returns:
            dict: 保存结果
                - success: 是否成功
                - result_id: 闪卡结果ID（成功时）
                - error: 错误信息（失败时）
        """
        try:
            from business.task_manager import TaskManager
            from business.database.flashcard_result_db import FlashcardResultDB

            # 获取任务信息以获取 user_id
            task_mgr = TaskManager()
            task = task_mgr.get_task(task_id)

            if not task:
                self.logger.error(f"任务不存在，无法保存闪卡结果: task_id={task_id}")
                return {
                    "success": False,
                    "error": "任务不存在"
                }

            user_id = task.get('user_id')
            if not user_id:
                self.logger.error(f"任务中没有 user_id: task_id={task_id}")
                return {
                    "success": False,
                    "error": "任务中没有user_id"
                }

            # 创建闪卡结果记录
            result_db = FlashcardResultDB()
            result = result_db.create_result(
                task_id=task_id,
                user_id=user_id,
                source_type=source_type,
                catalog_id=catalog_id,
                total_count=len(cards)
            )

            if result['success']:
                result_id = result['data'].get('id')
                self.logger.info(f"闪卡结果保存成功: task_id={task_id}, result_id={result_id}, count={len(cards)}")
                return {
                    "success": True,
                    "result_id": result_id,
                    "user_id": user_id
                }
            else:
                self.logger.error(f"闪卡结果保存失败: task_id={task_id}, 错误: {result.get('error')}")
                return result

        except Exception as e:
            self.logger.error(f"保存闪卡结果异常: task_id={task_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _save_flashcards(self, result_id: str, user_id: str, cards: list, catalog_id: str = None, section_results: list = None) -> dict:
        """
        批量保存闪卡到数据库

        Args:
            result_id: 闪卡结果集ID
            user_id: 用户ID
            cards: 闪卡列表，每张卡包含 question, answer 等字段
            catalog_id: 大纲ID（可选）
            section_results: 章节结果列表（可选），用于设置 section_id

        Returns:
            dict: 保存结果
                - success: 是否成功
                - count: 保存数量（成功时）
                - error: 错误信息（失败时）
        """
        try:
            from business.database.flashcard_db import FlashcardDB

            flashcard_db = FlashcardDB()

            # 构建闪卡数据列表
            flashcards = []

            # 如果有 section_results，构建 section_id 映射
            section_id_map = {}
            if section_results and catalog_id:
                # 需要从 catalog_data 中获取 section_id
                try:
                    from business.database.catalog_db import CatalogDB
                    catalog_db = CatalogDB()

                    # 通过 catalog_id 获取 catalog_data
                    from business.task_manager import TaskManager
                    task_mgr = TaskManager()

                    # 从 section_results 中获取 task_id（如果有）
                    # 或者我们可以通过 result_id 反查 task_id
                    from business.database.flashcard_result_db import FlashcardResultDB
                    result_db = FlashcardResultDB()
                    result_info = result_db.get_result_by_id(result_id)

                    if result_info['success']:
                        task_id = result_info['data'].get('task_id')
                        catalog_result = catalog_db.get_catalog_by_task_id(task_id)

                        if catalog_result['success']:
                            catalog_data = catalog_result['data'].get('catalog_data', [])
                            # 构建 section_title -> section_id 的映射
                            section_id_map = self._build_section_id_map(catalog_data)
                            self.logger.info(f"构建章节ID映射成功，映射数量: {len(section_id_map)}")

                except Exception as map_err:
                    self.logger.warning(f"构建章节ID映射失败: {str(map_err)}")

            # 如果有 section_results，按章节组织卡片
            if section_results:
                order_index = 0
                for section_result in section_results:
                    section_title = section_result.get('section_title', '')
                    section_cards = section_result.get('cards', [])

                    # 查找对应的 section_id
                    section_id = section_id_map.get(section_title)

                    for card in section_cards:
                        card_data = self._convert_card_to_jsonb(card)
                        flashcards.append({
                            'card_type': self._detect_card_type(card),
                            'card_data': card_data,
                            'order_index': order_index,
                            'section_id': section_id
                        })
                        order_index += 1
            else:
                # 没有章节信息，直接保存所有卡片
                for idx, card in enumerate(cards):
                    card_data = self._convert_card_to_jsonb(card)
                    flashcards.append({
                        'card_type': self._detect_card_type(card),
                        'card_data': card_data,
                        'order_index': idx
                    })

            # 批量保存闪卡
            result = flashcard_db.batch_create_flashcards(
                result_id=result_id,
                user_id=user_id,
                flashcards=flashcards,
                catalog_id=catalog_id
            )

            if result['success']:
                self.logger.info(f"闪卡批量保存成功: result_id={result_id}, count={len(flashcards)}")
            else:
                self.logger.error(f"闪卡批量保存失败: result_id={result_id}, 错误: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"批量保存闪卡异常: result_id={result_id}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _build_section_id_map(self, catalog_data: list) -> dict:
        """
        从 catalog_data 构建 section_title -> section_id 的映射

        Args:
            catalog_data: 大纲数据

        Returns:
            dict: section_title -> section_id 的映射
        """
        section_map = {}

        def traverse(items, parents=[]):
            for item in items:
                # 获取当前项的标题和ID
                title = None
                item_id = item.get('id')

                if 'chapter' in item:
                    title = item['chapter']
                elif 'section' in item:
                    # 构建完整路径
                    parent_chapter = next((p['chapter'] for p in parents if 'chapter' in p), '')
                    if parent_chapter:
                        title = f"{parent_chapter} - {item['section']}"
                    else:
                        title = item['section']
                elif 'subsection' in item:
                    parent_chapter = next((p['chapter'] for p in parents if 'chapter' in p), '')
                    parent_section = next((p['section'] for p in parents if 'section' in p), '')
                    if parent_chapter and parent_section:
                        title = f"{parent_chapter} - {parent_section} - {item['subsection']}"
                    elif parent_section:
                        title = f"{parent_section} - {item['subsection']}"
                    else:
                        title = item['subsection']

                if title and item_id:
                    section_map[title] = item_id

                # 递归处理子章节
                new_parents = parents + [item]
                for key in ['sections', 'subsections']:
                    if key in item and isinstance(item[key], list):
                        traverse(item[key], new_parents)

        traverse(catalog_data)
        return section_map

    def _convert_card_to_jsonb(self, card: dict) -> dict:
        """
        将卡片转换为 JSONB 格式

        Args:
            card: 原始卡片数据

        Returns:
            dict: JSONB 格式的卡片数据
        """
        # 基础卡片格式
        if 'question' in card and 'answer' in card:
            return {
                'question': card['question'],
                'answer': card['answer']
            }

        # 填空卡片格式
        if 'text' in card and 'cloze_items' in card:
            return {
                'text': card['text'],
                'cloze_items': card['cloze_items']
            }

        # 选择题格式
        if 'question' in card and 'options' in card:
            return {
                'question': card['question'],
                'options': card['options'],
                'correct_index': card.get('correct_index', 0)
            }

        # 默认返回原始数据
        return card

    def _detect_card_type(self, card: dict) -> str:
        """
        检测卡片类型

        Args:
            card: 卡片数据

        Returns:
            str: 卡片类型（basic/cloze/multiple_choice）
        """
        if 'cloze_items' in card or 'text' in card:
            return 'cloze'
        elif 'options' in card:
            return 'multiple_choice'
        else:
            return 'basic'

    def analyze_catalog(self, topic, lang="zh"):
        """
        目录分析，返回AI结构化目录内容。
        """
        self.logger.info(f"开始分析目录: topic={topic}, lang={lang}")
        workflow = CatalogAnalysisWorkflow(ai_service=self.ai_service)
        params = {"TOPIC": topic, "lang": lang}
        result = workflow.run(params)
        if isinstance(result, list):
            self.logger.info(f"目录分析成功: 获取到{len(result)}个章节")
        else:
            self.logger.warning(f"目录分析返回非结构化内容: {result}")
        return result

    def generate_flashcards(self, card_type, topic, number=10, lang="zh"):
        """
        生成指定类型的闪卡，返回结构化内容。
        card_type: basic_card | cloze_card | multiple_choice_card
        """
        self.logger.info(f"开始生成闪卡: card_type={card_type}, topic={topic}, number={number}, lang={lang}")
        workflow = FlashcardGenerateWorkflow(card_type=card_type, ai_service=self.ai_service)
        params = {"TOPIC": topic, "NUMBER": number, "lang": lang}
        result = workflow.run(params)
        if isinstance(result, list):
            self.logger.info(f"闪卡生成成功: 获取到{len(result)}张闪卡")
        else:
            self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
        return result

    def generate_flashcards_from_file(self, file_path, card_number=None, lang="zh", task_id=None):
        """
        根据文件内容生成闪卡列表。

        Args:
            file_path: 文件路径
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)
            task_id: 任务ID（必填，用于状态追踪和验证）

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文件生成闪卡: {file_path}, task_id={task_id}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 必须提供task_id
        if not task_id:
            self.logger.error("task_id未提供")
            return {
                "success": False,
                "error": "task_id为必填参数",
                "cards": []
            }

        # 创建任务管理器
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        if not file_path:
            self.logger.error("文件路径为空")
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": "文件路径不能为空",
                "cards": []
            }

        try:
            import os
            if not os.path.exists(file_path):
                self.logger.error(f"文件不存在: {file_path}")
                task_mgr.update_status(task_id, 'failed')
                return {
                    "success": False,
                    "error": "文件不存在",
                    "cards": []
                }

            # 1. 更新状态：文件上传中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=file_uploading")
            task_mgr.update_status(task_id, 'file_uploading')

            # 2. 上传文件到AI服务器
            self.logger.info(f"开始上传文件到AI服务器: {file_path}")
            multimedia = self.ai_service.upload_files([file_path])
            self.logger.info(f"文件上传成功，multimedia数量: {len(multimedia)}")

            # 3. 更新状态：AI处理中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=ai_processing")
            task_mgr.update_status(task_id, 'ai_processing')

            # 4. 更新状态：生成闪卡中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=generating_cards")
            task_mgr.update_status(task_id, 'generating_cards')

            # 5. 使用FlashcardGenerateWorkflow，文件模式
            workflow = FlashcardGenerateWorkflow(
                card_type="basic_card",
                form="file",
                mode="full",
                ai_service=self.ai_service
            )

            # 构建参数
            params = {
                "lang": lang
            }

            # 只有当card_number不为None时才添加NUMBER参数
            if card_number is not None:
                params["NUMBER"] = card_number

            # 6. 使用已上传的文件进行对话
            prompt = workflow.build_prompt(params)
            ai_result = self.ai_service.chat_with_multimedia(prompt, multimedia)

            # 7. 解析结果
            result = workflow.parse_result(ai_result)

            if isinstance(result, list):
                self.logger.info(f"文件闪卡生成成功: 获取到{len(result)}张闪卡")

                # 8. 保存闪卡结果到数据库
                save_result = self._save_flashcard_result(
                    task_id=task_id,
                    cards=result,
                    source_type='file'
                )

                if not save_result['success']:
                    self.logger.warning(f"闪卡结果保存失败，但不影响返回: {save_result.get('error')}")
                else:
                    # 8.1 保存具体闪卡到 flashcard 表
                    flashcard_save_result = self._save_flashcards(
                        result_id=save_result.get('result_id'),
                        user_id=save_result.get('user_id'),
                        cards=result
                    )
                    if not flashcard_save_result['success']:
                        self.logger.warning(f"具体闪卡保存失败: {flashcard_save_result.get('error')}")

                # 9. 更新状态：完成
                self.logger.info(f"更新任务状态: task_id={task_id}, status=completed")
                task_mgr.update_status(task_id, 'completed')

                return {
                    "success": True,
                    "cards": result,
                    "result_id": save_result.get('result_id')  # 返回结果ID
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                task_mgr.update_status(task_id, 'failed')
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文件闪卡生成失败: {str(e)}", exc_info=True)
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": str(e),
                "cards": []
            }
    def generate_flashcards_from_text(self, text_content, card_number=None, lang="zh", task_id=None):
        """
        根据文本内容生成闪卡列表。

        Args:
            text_content: 输入的文本内容
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)
            task_id: 任务ID（必填，用于状态追踪和验证）

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文本生成闪卡，task_id={task_id}, 文本长度: {len(text_content) if text_content else 0}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 必须提供task_id
        if not task_id:
            self.logger.error("task_id未提供")
            return {
                "success": False,
                "error": "task_id为必填参数",
                "cards": []
            }

        # 创建任务管理器
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        if not text_content or not text_content.strip():
            self.logger.error("文本内容为空")
            # 更新任务状态为失败
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": "文本内容不能为空",
                "cards": []
            }

        try:
            # 1. 更新状态：AI处理中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=ai_processing")
            task_mgr.update_status(task_id, 'ai_processing')

            # 2. 更新状态：生成闪卡中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=generating_cards")
            task_mgr.update_status(task_id, 'generating_cards')

            # 3. 使用基础卡片类型生成闪卡
            workflow = FlashcardGenerateWorkflow(
                card_type="basic_card",
                form="text",
                mode="full",
                ai_service=self.ai_service
            )

            # 构建参数
            params = {
                "TEXT_CONTENT": text_content,
                "lang": lang
            }

            # 只有当card_number不为None时才添加NUMBER参数
            if card_number is not None:
                params["NUMBER"] = card_number

            result = workflow.run(params)

            if isinstance(result, list):
                self.logger.info(f"文本闪卡生成成功: 获取到{len(result)}张闪卡")

                # 4. 保存闪卡结果到数据库
                save_result = self._save_flashcard_result(
                    task_id=task_id,
                    cards=result,
                    source_type='text'
                )

                if not save_result['success']:
                    self.logger.warning(f"闪卡结果保存失败，但不影响返回: {save_result.get('error')}")
                else:
                    # 4.1 保存具体闪卡到 flashcard 表
                    flashcard_save_result = self._save_flashcards(
                        result_id=save_result.get('result_id'),
                        user_id=save_result.get('user_id'),
                        cards=result
                    )
                    if not flashcard_save_result['success']:
                        self.logger.warning(f"具体闪卡保存失败: {flashcard_save_result.get('error')}")

                # 5. 更新状态：完成
                self.logger.info(f"更新任务状态: task_id={task_id}, status=completed")
                task_mgr.update_status(task_id, 'completed')

                return {
                    "success": True,
                    "cards": result,
                    "result_id": save_result.get('result_id')  # 返回结果ID
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                # 更新任务状态为失败
                task_mgr.update_status(task_id, 'failed')
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文本闪卡生成失败: {str(e)}", exc_info=True)
            # 更新任务状态为失败
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": str(e),
                "cards": []
            }

    def generate_flashcards_from_url(self, url, card_number=None, lang="zh"):
        """
        根据URL爬取网页内容并生成闪卡列表。

        Args:
            url: 网页URL地址
            card_number: 需要生成的闪卡数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
                - crawled_content: 爬取到的网页内容（可选，用于调试）
        """
        self.logger.info(f"根据URL生成闪卡: url={url}, card_number={card_number or '智能'}, lang={lang}")

        if not url or not url.strip():
            self.logger.error("URL为空")
            return {
                "success": False,
                "error": "URL不能为空",
                "cards": []
            }

        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            self.logger.error(f"URL格式不正确: {url}")
            return {
                "success": False,
                "error": "URL格式不正确，必须以 http:// 或 https:// 开头",
                "cards": []
            }

        try:
            # 使用web_crawl爬取网页内容
            import asyncio
            from ai_services.crawl.web_crawl import crawl_web_content

            self.logger.info(f"开始爬取网页: {url}")

            # 运行异步爬虫获取markdown格式内容
            crawled_content = asyncio.run(crawl_web_content(url, "markdown"))

            if not crawled_content or not crawled_content.strip():
                self.logger.error("爬取到的网页内容为空")
                return {
                    "success": False,
                    "error": "无法获取网页内容或网页内容为空",
                    "cards": []
                }

            self.logger.info(f"成功爬取网页内容，长度: {len(crawled_content)}")

            # 使用FlashcardGenerateWorkflow生成闪卡
            workflow = FlashcardGenerateWorkflow(
                card_type="basic_card",
                form="text",
                mode="full",
                ai_service=self.ai_service
            )

            # 构建参数
            params = {
                "TEXT_CONTENT": crawled_content,
                "lang": lang
            }

            # 只有当card_number不为None时才添加NUMBER参数
            if card_number is not None:
                params["NUMBER"] = card_number

            result = workflow.run(params)

            if isinstance(result, list):
                self.logger.info(f"URL闪卡生成成功: 获取到{len(result)}张闪卡")
                return {
                    "success": True,
                    "cards": result,
                    "url": url,
                    "crawled_length": len(crawled_content)
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except ImportError as e:
            self.logger.error(f"导入爬虫模块失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "爬虫模块未安装，请先安装 crawl4ai 库",
                "cards": []
            }
        except Exception as e:
            self.logger.error(f"URL闪卡生成失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"处理失败: {str(e)}",
                "cards": []
            }

    def generate_flashcards_from_text_section(self, text_content, section_title, card_number=None, lang="zh"):
        """
        根据文本内容和指定章节生成闪卡列表。

        Args:
            text_content: 完整的学习材料文本
            section_title: 章节标题，如"第三章：Python数据类型"
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文本章节生成闪卡，章节: {section_title}, 文本长度: {len(text_content) if text_content else 0}, 数量: {card_number or '智能'}, 语言: {lang}")

        if not text_content or not text_content.strip():
            self.logger.error("文本内容为空")
            return {
                "success": False,
                "error": "文本内容不能为空",
                "cards": []
            }

        if not section_title or not section_title.strip():
            self.logger.error("章节标题为空")
            return {
                "success": False,
                "error": "章节标题不能为空",
                "cards": []
            }

        try:
            # 使用章节模式，文本形式
            workflow = FlashcardGenerateWorkflow(
                card_type="basic_card",
                form="text",
                mode="section",
                ai_service=self.ai_service
            )

            # 构建参数
            params = {
                "TEXT_CONTENT": text_content,
                "SECTION_TITLE": section_title,
                "lang": lang
            }

            # 只有当card_number不为None时才添加NUMBER参数
            if card_number is not None:
                params["NUMBER"] = card_number

            result = workflow.run(params)

            if isinstance(result, list):
                self.logger.info(f"章节闪卡生成成功: 获取到{len(result)}张闪卡 - 章节: {section_title}")
                return {
                    "success": True,
                    "cards": result,
                    "section_title": section_title
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"章节闪卡生成失败 - 章节: {section_title}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "cards": []
            }

    def generate_flashcards_from_file_section(self, file_path, section_title, card_number=None, lang="zh", task_id=None):
        """
        根据文件和指定章节生成闪卡列表。

        Args:
            file_path: 文件路径
            section_title: 章节标题，如"第三章：Python数据类型"
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)
            task_id: 任务ID（必填，用于状态追踪）

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文件章节生成闪卡: {file_path}, task_id={task_id}, 章节: {section_title}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 必须提供task_id
        if not task_id:
            self.logger.error("task_id未提供")
            return {
                "success": False,
                "error": "task_id为必填参数",
                "cards": []
            }

        # 创建任务管理器
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        if not section_title or not section_title.strip():
            self.logger.error("章节标题为空")
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": "章节标题不能为空",
                "cards": []
            }

        try:
            # 1. 获取任务信息
            task = task_mgr.get_task(task_id)
            if not task:
                self.logger.error(f"任务不存在: task_id={task_id}")
                return {
                    "success": False,
                    "error": "任务不存在",
                    "cards": []
                }

            # 2. 尝试从input_data.file.info中获取multimedia
            input_data = task.get('input_data', {})
            file_data = input_data.get('file', {})
            multimedia = file_data.get('info')

            file_name = file_data.get('name', 'unknown')

            if multimedia:
                # 从缓存中获取已上传的文件信息
                self.logger.info(f"从input_data.file.info中获取到已上传的multimedia，跳过文件上传步骤")
            else:
                # 没有缓存，需要上传文件
                self.logger.info(f"input_data.file.info中没有multimedia，需要上传文件")

                if not file_path:
                    self.logger.error("文件路径为空")
                    task_mgr.update_status(task_id, 'failed')
                    return {
                        "success": False,
                        "error": "文件路径不能为空",
                        "cards": []
                    }

                import os
                if not os.path.exists(file_path):
                    self.logger.error(f"文件不存在: {file_path}")
                    task_mgr.update_status(task_id, 'failed')
                    return {
                        "success": False,
                        "error": "文件不存在",
                        "cards": []
                    }

                # 更新状态：文件上传中
                self.logger.info(f"更新任务状态: task_id={task_id}, status=file_uploading")
                task_mgr.update_status(task_id, 'file_uploading')

                # 上传文件到AI服务器
                self.logger.info(f"开始上传文件到AI服务器: {file_path}")
                multimedia = self.ai_service.upload_files([file_path])
                self.logger.info(f"文件上传成功，multimedia数量: {len(multimedia)}")

                file_name = os.path.basename(file_path)

            # 3. 更新状态：AI处理中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=ai_processing")
            task_mgr.update_status(task_id, 'ai_processing')

            # 4. 更新状态：生成闪卡中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=generating_cards")
            task_mgr.update_status(task_id, 'generating_cards')

            # 5. 使用章节模式，文件形式
            workflow = FlashcardGenerateWorkflow(
                card_type="basic_card",
                form="file",
                mode="section",
                ai_service=self.ai_service
            )

            # 构建参数
            params = {
                "FILENAME": file_name,
                "SECTION_TITLE": section_title,
                "lang": lang
            }

            # 只有当card_number不为None时才添加NUMBER参数
            if card_number is not None:
                params["NUMBER"] = card_number

            # 6. 使用已上传的文件进行对话
            prompt = workflow.build_prompt(params)
            ai_result = self.ai_service.chat_with_multimedia(prompt, multimedia)

            # 7. 解析结果
            result = workflow.parse_result(ai_result)

            if isinstance(result, list):
                self.logger.info(f"文件章节闪卡生成成功: 获取到{len(result)}张闪卡 - 文件: {file_name}, 章节: {section_title}")

                # 8. 更新状态：完成
                self.logger.info(f"更新任务状态: task_id={task_id}, status=completed")
                task_mgr.update_status(task_id, 'completed')

                return {
                    "success": True,
                    "cards": result,
                    "section_title": section_title,
                    "file_name": file_name
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                task_mgr.update_status(task_id, 'failed')
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文件章节闪卡生成失败 - 文件: {file_path}, 章节: {section_title}, 错误: {str(e)}", exc_info=True)
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": str(e),
                "cards": []
            }

    def generate_flashcards_from_file_section_by_ids(self, file_path, chapter_ids, card_number=None, lang="zh", task_id=None):
        """
        根据文件和指定章节ID列表生成闪卡列表。

        Args:
            file_path: 文件路径
            chapter_ids: 章节ID列表
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)
            task_id: 任务ID（必填，用于状态追踪）

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 所有章节的闪卡列表
                - section_results: 每个章节的结果列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文件章节ID列表生成闪卡: {file_path}, task_id={task_id}, 章节ID数量: {len(chapter_ids)}, 数量: {card_number or '智能'}, 语言: {lang}")

        # 必须提供task_id
        if not task_id:
            self.logger.error("task_id未提供")
            return {
                "success": False,
                "error": "task_id为必填参数",
                "cards": [],
                "section_results": []
            }

        # 创建任务管理器
        from business.task_manager import TaskManager
        task_mgr = TaskManager()

        if not chapter_ids:
            self.logger.error("章节ID列表为空")
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": "章节ID列表不能为空",
                "cards": [],
                "section_results": []
            }

        try:
            # 1. 获取任务信息
            task = task_mgr.get_task(task_id)
            if not task:
                self.logger.error(f"任务不存在: task_id={task_id}")
                return {
                    "success": False,
                    "error": "任务不存在",
                    "cards": [],
                    "section_results": []
                }

            # 2. 尝试从input_data.file.info中获取multimedia
            input_data = task.get('input_data', {})
            file_data = input_data.get('file', {})
            multimedia = file_data.get('info')

            file_name = file_data.get('name', 'unknown')

            if multimedia:
                # 从缓存中获取已上传的文件信息
                self.logger.info(f"从input_data.file.info中获取到已上传的multimedia，跳过文件上传步骤")
            else:
                # 没有缓存，需要上传文件
                self.logger.info(f"input_data.file.info中没有multimedia，需要上传文件")

                if not file_path:
                    self.logger.error("文件路径为空")
                    task_mgr.update_status(task_id, 'failed')
                    return {
                        "success": False,
                        "error": "文件路径不能为空",
                        "cards": [],
                        "section_results": []
                    }

                import os
                if not os.path.exists(file_path):
                    self.logger.error(f"文件不存在: {file_path}")
                    task_mgr.update_status(task_id, 'failed')
                    return {
                        "success": False,
                        "error": "文件不存在",
                        "cards": [],
                        "section_results": []
                    }

                # 更新状态：文件上传中
                self.logger.info(f"更新任务状态: task_id={task_id}, status=file_uploading")
                task_mgr.update_status(task_id, 'file_uploading')

                # 上传文件到AI服务器
                self.logger.info(f"开始上传文件到AI服务器: {file_path}")
                multimedia = self.ai_service.upload_files([file_path])
                self.logger.info(f"文件上传成功，multimedia数量: {len(multimedia)}")

                file_name = os.path.basename(file_path)

            # 3. 更新状态：AI处理中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=ai_processing")
            task_mgr.update_status(task_id, 'ai_processing')

            # 4. 更新状态：生成闪卡中
            self.logger.info(f"更新任务状态: task_id={task_id}, status=generating_cards")
            task_mgr.update_status(task_id, 'generating_cards')

            # 5. 获取文件大纲信息
            from business.catalog import CatalogService
            catalog_service = CatalogService()
            catalog = catalog_service.get_catalog_from_file(file_path, lang, task_id)

            # 从大纲中获取章节标题
            section_titles = self._get_section_titles_by_ids(catalog, chapter_ids)

            # 过滤掉父章节，只保留叶子节点（没有子章节的节点）
            section_titles = self._filter_leaf_sections(section_titles, chapter_ids, catalog)

            if not section_titles:
                self.logger.error(f"无法根据章节ID找到对应的章节: {chapter_ids}")
                task_mgr.update_status(task_id, 'failed')
                return {
                    "success": False,
                    "error": "无法找到对应的章节标题",
                    "cards": [],
                    "section_results": []
                }

            # 6. 遍历章节ID，为每个章节生成闪卡
            all_cards = []
            section_results = []

            for section_title in section_titles:
                self.logger.info(f"开始为章节生成闪卡，章节: {section_title}")
                
                # 使用章节模式，文件形式
                workflow = FlashcardGenerateWorkflow(
                    card_type="basic_card",
                    form="file",
                    mode="section",
                    ai_service=self.ai_service
                )

                # 构建参数
                params = {
                    "FILENAME": file_name,
                    "SECTION_TITLE": section_title,
                    "lang": lang
                }

                # 只有当card_number不为None时才添加NUMBER参数
                if card_number is not None:
                    params["NUMBER"] = card_number

                # 使用已上传的文件进行对话
                prompt = workflow.build_prompt(params)
                ai_result = self.ai_service.chat_with_multimedia(prompt, multimedia)

                # 解析结果
                result = workflow.parse_result(ai_result)

                if isinstance(result, list):
                    self.logger.info(f"章节闪卡生成成功: 获取到{len(result)}张闪卡 - 章节: {section_title}")
                    all_cards.extend(result)
                    
                    section_results.append({
                        "section_title": section_title,
                        "cards": result,
                        "count": len(result)
                    })
                else:
                    self.logger.warning(f"章节 {section_title} 闪卡生成失败，AI返回格式错误: {result}")

            # 7. 检查是否成功生成了闪卡
            if not all_cards:
                self.logger.error("所有章节的闪卡生成都失败了")
                task_mgr.update_status(task_id, 'failed')
                return {
                    "success": False,
                    "error": "所有章节的闪卡生成都失败了",
                    "cards": [],
                    "section_results": []
                }

            # 8. 获取 catalog_id（如果有）
            catalog_id = None
            try:
                from business.database.catalog_db import CatalogDB
                catalog_db = CatalogDB()
                catalog_result = catalog_db.get_catalog_by_task_id(task_id)
                if catalog_result['success']:
                    catalog_id = catalog_result['data'].get('id')
                    self.logger.info(f"获取到 catalog_id: {catalog_id}")
            except Exception as catalog_err:
                self.logger.warning(f"获取 catalog_id 失败: {str(catalog_err)}")

            # 9. 保存闪卡结果到数据库
            save_result = self._save_flashcard_result(
                task_id=task_id,
                cards=all_cards,
                source_type='file',
                catalog_id=catalog_id
            )

            if not save_result['success']:
                self.logger.warning(f"闪卡结果保存失败，但不影响返回: {save_result.get('error')}")
            else:
                # 9.1 保存具体闪卡到 flashcard 表（带章节信息）
                flashcard_save_result = self._save_flashcards(
                    result_id=save_result.get('result_id'),
                    user_id=save_result.get('user_id'),
                    cards=all_cards,
                    catalog_id=catalog_id,
                    section_results=section_results
                )
                if not flashcard_save_result['success']:
                    self.logger.warning(f"具体闪卡保存失败: {flashcard_save_result.get('error')}")

            # 10. 更新状态：完成
            self.logger.info(f"更新任务状态: task_id={task_id}, status=completed")
            task_mgr.update_status(task_id, 'completed')

            return {
                "success": True,
                "cards": all_cards,
                "section_results": section_results,
                "file_name": file_name,
                "result_id": save_result.get('result_id')  # 返回结果ID
            }

        except Exception as e:
            self.logger.error(f"文件章节ID列表闪卡生成失败 - 文件: {file_path}, 章节ID: {chapter_ids}, 错误: {str(e)}", exc_info=True)
            task_mgr.update_status(task_id, 'failed')
            return {
                "success": False,
                "error": str(e),
                "cards": [],
                "section_results": []
            }

    def _get_section_titles_by_ids(self, catalog, chapter_ids):
        """
        根据章节ID列表从大纲中提取章节标题列表
        
        Args:
            catalog: 大纲结构
            chapter_ids: 章节ID列表
            
        Returns:
            list: 章节标题列表
        """
        titles = []

        def search_catalog(items, parents=[]):
            for item in items:
                # 检查当前项目是否是选中的ID
                if item.get('id') in chapter_ids:
                    if 'chapter' in item:
                        # 章节
                        titles.append(item['chapter'])
                    elif 'section' in item:
                        # 小节，使用路径形式
                        parent_chapter = next((parent['chapter'] for parent in parents if 'chapter' in parent), "")
                        if parent_chapter:
                            titles.append(f"{parent_chapter} - {item['section']}")
                        else:
                            titles.append(item['section'])
                    elif 'subsection' in item:
                        # 子小节，使用路径形式
                        parent_chapter = next((parent['chapter'] for parent in parents if 'chapter' in parent), "")
                        parent_section = next((parent['section'] for parent in parents if 'section' in parent), "")
                        if parent_chapter and parent_section:
                            titles.append(f"{parent_chapter} - {parent_section} - {item['subsection']}")
                        elif parent_section:
                            titles.append(f"{parent_section} - {item['subsection']}")
                        else:
                            titles.append(item['subsection'])
                
                # 递归搜索子章节
                new_parents = parents + [item]
                for key in ['sections', 'subsections']:
                    if key in item and isinstance(item[key], list):
                        search_catalog(item[key], new_parents)

        search_catalog(catalog if catalog else [])
        return titles

    def _filter_leaf_sections(self, section_titles: list, chapter_ids: list, catalog: list) -> list:
        """
        过滤掉父章节，只保留叶子节点（没有被选中的子章节的节点）

        Args:
            section_titles: 章节标题列表
            chapter_ids: 选中的章节ID列表
            catalog: 大纲数据

        Returns:
            list: 过滤后的章节标题列表（只包含叶子节点）
        """
        # 构建 ID -> 是否有被选中的子节点 的映射
        has_selected_children = set()

        def check_children(items):
            for item in items:
                item_id = item.get('id')

                # 检查子节点
                has_child_selected = False
                for key in ['sections', 'subsections']:
                    if key in item and isinstance(item[key], list):
                        for child in item[key]:
                            child_id = child.get('id')
                            if child_id in chapter_ids:
                                has_child_selected = True
                                # 递归检查更深层的子节点
                                check_children([child])

                # 如果当前节点有子节点被选中，标记它
                if has_child_selected and item_id in chapter_ids:
                    has_selected_children.add(item_id)

                # 继续递归处理子节点
                for key in ['sections', 'subsections']:
                    if key in item and isinstance(item[key], list):
                        check_children(item[key])

        check_children(catalog if catalog else [])

        # 构建 ID -> title 的映射
        id_to_title = {}
        def build_mapping(items, parents=[]):
            for item in items:
                item_id = item.get('id')
                title = None

                if 'chapter' in item:
                    title = item['chapter']
                elif 'section' in item:
                    parent_chapter = next((p['chapter'] for p in parents if 'chapter' in p), '')
                    if parent_chapter:
                        title = f"{parent_chapter} - {item['section']}"
                    else:
                        title = item['section']
                elif 'subsection' in item:
                    parent_chapter = next((p['chapter'] for p in parents if 'chapter' in p), '')
                    parent_section = next((p['section'] for p in parents if 'section' in p), '')
                    if parent_chapter and parent_section:
                        title = f"{parent_chapter} - {parent_section} - {item['subsection']}"
                    elif parent_section:
                        title = f"{parent_section} - {item['subsection']}"
                    else:
                        title = item['subsection']

                if title and item_id:
                    id_to_title[item_id] = title

                new_parents = parents + [item]
                for key in ['sections', 'subsections']:
                    if key in item and isinstance(item[key], list):
                        build_mapping(item[key], new_parents)

        build_mapping(catalog if catalog else [])

        # 过滤：只保留没有被选中子节点的章节
        filtered_titles = []
        for chapter_id in chapter_ids:
            if chapter_id not in has_selected_children:
                title = id_to_title.get(chapter_id)
                if title:
                    filtered_titles.append(title)
                    self.logger.info(f"保留叶子节点章节: {chapter_id} -> {title}")
            else:
                self.logger.info(f"过滤父章节（有子节点被选中）: {chapter_id}")

        return filtered_titles 