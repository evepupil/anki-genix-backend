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

    def generate_flashcards_from_file(self, file_path, card_number=None, lang="zh"):
        """
        根据文件内容生成闪卡列表。

        Args:
            file_path: 文件路径
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文件生成闪卡: {file_path}, 数量: {card_number or '智能'}, 语言: {lang}")

        if not file_path:
            self.logger.error("文件路径为空")
            return {
                "success": False,
                "error": "文件路径不能为空",
                "cards": []
            }

        try:
            import os
            if not os.path.exists(file_path):
                self.logger.error(f"文件不存在: {file_path}")
                return {
                    "success": False,
                    "error": "文件不存在",
                    "cards": []
                }

            # 使用FlashcardGenerateWorkflow，文件模式
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

            # 使用AI服务的chat_with_files方法
            prompt = workflow.build_prompt(params)
            ai_result = self.ai_service.chat_with_files(prompt, [file_path])

            # 解析结果
            result = workflow.parse_result(ai_result)

            if isinstance(result, list):
                self.logger.info(f"文件闪卡生成成功: 获取到{len(result)}张闪卡")
                return {
                    "success": True,
                    "cards": result
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文件闪卡生成失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "cards": []
            }
    def generate_flashcards_from_text(self, text_content, card_number=None, lang="zh"):
        """
        根据文本内容生成闪卡列表。

        Args:
            text_content: 输入的文本内容
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文本生成闪卡，文本长度: {len(text_content) if text_content else 0}, 数量: {card_number or '智能'}, 语言: {lang}")

        if not text_content or not text_content.strip():
            self.logger.error("文本内容为空")
            return {
                "success": False,
                "error": "文本内容不能为空",
                "cards": []
            }

        try:
            # 使用基础卡片类型生成闪卡
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
                return {
                    "success": True,
                    "cards": result
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文本闪卡生成失败: {str(e)}", exc_info=True)
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

    def generate_flashcards_from_file_section(self, file_path, section_title, card_number=None, lang="zh"):
        """
        根据文件和指定章节生成闪卡列表。

        Args:
            file_path: 文件路径
            section_title: 章节标题，如"第三章：Python数据类型"
            card_number: 卡片数量（可选，不提供则由AI智能决定）
            lang: 语言，默认中文(zh)

        Returns:
            dict: 包含生成结果的字典
                - success: 是否成功
                - cards: 闪卡列表
                - error: 错误信息（如果失败）
        """
        self.logger.info(f"根据文件章节生成闪卡: {file_path}, 章节: {section_title}, 数量: {card_number or '智能'}, 语言: {lang}")

        if not file_path:
            self.logger.error("文件路径为空")
            return {
                "success": False,
                "error": "文件路径不能为空",
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
            import os
            if not os.path.exists(file_path):
                self.logger.error(f"文件不存在: {file_path}")
                return {
                    "success": False,
                    "error": "文件不存在",
                    "cards": []
                }

            # 使用章节模式，文件形式
            workflow = FlashcardGenerateWorkflow(
                card_type="basic_card",
                form="file",
                mode="section",
                ai_service=self.ai_service
            )

            # 获取文件名（用于提示词）
            file_name = os.path.basename(file_path)

            # 构建参数
            params = {
                "FILENAME": file_name,
                "SECTION_TITLE": section_title,
                "lang": lang
            }

            # 只有当card_number不为None时才添加NUMBER参数
            if card_number is not None:
                params["NUMBER"] = card_number

            # 使用AI服务的chat_with_files方法
            prompt = workflow.build_prompt(params)
            ai_result = self.ai_service.chat_with_files(prompt, [file_path])

            # 解析结果
            result = workflow.parse_result(ai_result)

            if isinstance(result, list):
                self.logger.info(f"文件章节闪卡生成成功: 获取到{len(result)}张闪卡 - 文件: {file_name}, 章节: {section_title}")
                return {
                    "success": True,
                    "cards": result,
                    "section_title": section_title,
                    "file_name": file_name
                }
            else:
                self.logger.warning(f"闪卡生成返回非结构化内容: {result}")
                return {
                    "success": False,
                    "error": "AI返回格式错误",
                    "cards": []
                }

        except Exception as e:
            self.logger.error(f"文件章节闪卡生成失败 - 文件: {file_path}, 章节: {section_title}, 错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "cards": []
            } 