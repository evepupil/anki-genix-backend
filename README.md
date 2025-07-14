# Anki-GenIX

基于AI的Anki闪卡生成工具，使用Django+Zappa的Serverless架构，支持多种AI服务。

## 项目功能

1. **知识目录分析**：用户输入要学习的知识，AI自动分析出结构化目录
2. **智能闪卡生成**：用户选择目录章节，AI生成对应的Anki闪卡
   - 支持问答卡（Basic Card）
   - 支持填空卡（Cloze Deletion）
   - 支持选择题卡（Multiple Choice）
3. **闪卡质量控制**：用户可检视、筛选和上报错误的闪卡
4. **Anki格式导出**：生成可直接导入Anki的文件（.apkg或.csv）

## 项目结构

```
anki-genix/
├── ai_services/               # AI服务层
│   ├── ai_base.py            # AI服务基类
│   ├── ai_deepseek.py        # 腾讯元宝Deepseek实现
│   └── prompts/              # AI提示词
│       ├── __init__.py
│       └── prompts.yaml      # 多语言提示词配置
│
├── business/                  # 业务逻辑层
│   └── flashcard.py          # 闪卡业务逻辑
│
├── utils/                     # 工具类
│   ├── __init__.py
│   ├── logger.py             # 日志工具
│   └── anki_exporter.py      # Anki导出工具
│
├── test/                      # 测试代码
│   ├── __init__.py
│   ├── config.py             # 测试配置
│   ├── test_ai_service.py    # AI服务测试
│   ├── test_business.py      # 业务逻辑测试
│   ├── test_logger.py        # 日志工具测试
│   ├── test_anki_exporter.py # Anki导出测试
│   └── run_all_tests.py      # 运行所有测试
│
├── requirements.txt           # 项目依赖
├── .gitignore                 # Git忽略文件
└── README.md                  # 项目说明
```

## 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置AI服务

创建 `.env` 文件，配置AI服务参数：

```bash
# Deepseek API 配置
DEEPSEEK_BASE_URL="http://your-api-url/v1/"
DEEPSEEK_API_KEY="your-api-key"
DEEPSEEK_AGENT_ID="your-agent-id"
DEEPSEEK_HY_SOURCE="web"
DEEPSEEK_HY_USER="your-user-id"

# 日志配置
LOG_LEVEL="info"  # debug, info, warning, error, critical
```

## 使用示例

### 1. 分析知识目录

```python
from business.flashcard import FlashcardBusiness

# 初始化业务类
biz = FlashcardBusiness()

# 分析目录
topic = "Python编程基础"
catalog = biz.analyze_catalog(topic, lang="zh")
print(catalog)
```

### 2. 生成闪卡

```python
# 生成基础问答卡
basic_cards = biz.generate_flashcards("basic_card", topic, number=10, lang="zh")

# 生成填空卡
cloze_cards = biz.generate_flashcards("cloze_card", topic, number=5, lang="zh")

# 生成选择题卡
choice_cards = biz.generate_flashcards("multiple_choice_card", topic, number=5, lang="zh")
```

### 3. 导出Anki文件

```python
from utils.anki_exporter import export_to_anki_pkg, export_to_csv

# 导出为Anki包文件(.apkg)
apkg_path = export_to_anki_pkg("Python基础-问答卡", basic_cards, "basic_card")
print(f"Anki包文件已保存至: {apkg_path}")

# 导出为CSV文件
csv_path = export_to_csv(cloze_cards, "cloze_card")
print(f"CSV文件已保存至: {csv_path}")
```

## 运行测试

```bash
# 运行所有测试
python test/run_all_tests.py

# 运行单个测试
python test/test_ai_service.py
python test/test_business.py
python test/test_anki_exporter.py
```

## 扩展支持

### 添加新的AI服务

1. 在 `ai_services` 目录下创建新的AI服务类，继承 `AIServiceBase`
2. 实现 `chat` 方法

```python
from ai_services.ai_base import AIServiceBase

class NewAIService(AIServiceBase):
    def chat(self, prompt: str, stream: bool = False) -> str:
        # 实现新的AI服务调用
        pass
```

### 添加新的闪卡类型

1. 在 `prompts.yaml` 中添加新的提示词
2. 在 `anki_exporter.py` 中添加对应的导出支持

## 贡献

欢迎提交Issue和Pull Request来改进项目！

## 许可证

MIT 