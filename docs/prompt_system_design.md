# 提示词系统设计文档

## 概述

AnkiGenIX 的提示词系统采用**分层、分模式**的设计架构，支持灵活的闪卡生成和大纲分析功能。

## 核心设计理念

### 1. 输入形式（Form）
- **text**：用户直接提供文本内容
- **file**：用户上传文件，AI 读取文件内容

### 2. 生成模式（Mode）
- **topic（话题模式）**：用户只提供主题关键词，AI 根据自身知识库生成内容
- **full（全文模式）**：用户提供完整内容，AI 基于实际内容生成
- **section（章节模式）**：仅用于闪卡生成，针对特定章节生成内容

## 文件结构

```
ai_services/prompts/
├── prompts_flashcard_text.yaml      # 文本输入的闪卡生成提示词
├── prompts_flashcard_file.yaml      # 文件上传的闪卡生成提示词
├── prompts_catalog_text.yaml        # 文本输入的大纲生成提示词
├── prompts_catalog_file.yaml        # 文件上传的大纲生成提示词
└── prompts_summary.yaml             # 摘要生成提示词（旧版，待重构）
```

## 提示词文件结构

### 闪卡生成提示词（3种卡片类型 × 3种模式 × 2种语言）

```yaml
basic_card:              # 卡片类型
  topic:                 # 生成模式
    zh:                  # 语言
      prompt: |
        提示词内容...
        占位符：[TOPIC], [NUMBER], {lang}
    en:
      prompt: |
        English prompt...

  full:                  # 全文模式
    zh:
      prompt: |
        提示词内容...
        占位符：[TEXT_CONTENT], [NUMBER], {lang}
    en:
      prompt: |
        English prompt...

  section:               # 章节模式
    zh:
      prompt: |
        提示词内容...
        占位符：[SECTION_TITLE], [TEXT_CONTENT]/[FILENAME], [NUMBER], {lang}
    en:
      prompt: |
        English prompt...

cloze_card:             # 填空卡
  # 同样结构...

multiple_choice_card:   # 多选题卡
  # 同样结构...
```

### 大纲生成提示词（2种模式 × 2种语言）

```yaml
catalog_analysis:
  topic:                # 话题模式
    zh:
      prompt: |
        提示词内容...
        占位符：[TOPIC], {lang}
    en:
      prompt: |
        English prompt...

  full:                 # 全文模式
    zh:
      prompt: |
        提示词内容...
        占位符：[TEXT_CONTENT], {lang}
    en:
      prompt: |
        English prompt...
```

## 占位符说明

### 闪卡生成占位符
- `[TOPIC]`：学习主题（topic 模式）
- `[TEXT_CONTENT]`：完整文本内容（text 形式的 full/section 模式）
- `[FILENAME]`：文件名（file 形式的 section 模式）
- `[SECTION_TITLE]`：章节标题（section 模式）
- `[NUMBER]`：生成卡片数量
- `{lang}`：目标语言代码

### 大纲生成占位符
- `[TOPIC]`：学习主题（topic 模式）
- `[TEXT_CONTENT]`：完整文本内容（full 模式）
- `{lang}`：目标语言代码

## 模式组合矩阵

### 闪卡生成（6种组合）

| 输入形式 | 生成模式 | 占位符 | 说明 |
|---------|---------|--------|------|
| text | topic | [TOPIC], [NUMBER] | 用户提供主题，AI 生成卡片 |
| text | full | [TEXT_CONTENT], [NUMBER] | 用户提供全文，AI 提取知识点 |
| text | section | [SECTION_TITLE], [TEXT_CONTENT], [NUMBER] | 用户提供章节标题+全文，AI 针对特定章节生成 |
| file | topic | [TOPIC], [NUMBER] | 与文本模式相同 |
| file | full | [NUMBER] | AI 直接读取文件内容 |
| file | section | [SECTION_TITLE], [FILENAME], [NUMBER] | 用户提供章节标题+文件名，AI 读取文件后针对章节生成 |

### 大纲生成（4种组合）

| 输入形式 | 生成模式 | 占位符 | 说明 |
|---------|---------|--------|------|
| text | topic | [TOPIC] | 用户提供主题，AI 生成知识大纲 |
| text | full | [TEXT_CONTENT] | 用户提供全文，AI 分析结构生成大纲 |
| file | topic | [TOPIC] | 与文本模式相同 |
| file | full | 无 | AI 直接读取文件内容分析大纲 |

## 代码调用示例

### 闪卡生成

```python
from ai_services.workflows.flashcard_generate import FlashcardGenerateWorkflow

# 文本输入 - 话题模式
workflow = FlashcardGenerateWorkflow(
    card_type="basic_card",
    form="text",
    mode="topic"
)
result = workflow.run(params={
    "TOPIC": "Python编程",
    "NUMBER": 10,
    "lang": "zh"
})

# 文本输入 - 全文模式
workflow = FlashcardGenerateWorkflow(
    card_type="basic_card",
    form="text",
    mode="full"
)
result = workflow.run(params={
    "TEXT_CONTENT": "完整的文本内容...",
    "NUMBER": 10,
    "lang": "zh"
})

# 文本输入 - 章节模式
workflow = FlashcardGenerateWorkflow(
    card_type="basic_card",
    form="text",
    mode="section"
)
result = workflow.run(params={
    "SECTION_TITLE": "第一章：Python基础",
    "TEXT_CONTENT": "完整的教材内容...",
    "NUMBER": 10,
    "lang": "zh"
})

# 文件上传 - 章节模式
workflow = FlashcardGenerateWorkflow(
    card_type="basic_card",
    form="file",
    mode="section"
)
result = workflow.run(params={
    "SECTION_TITLE": "第一章：Python基础",
    "FILENAME": "python_tutorial.pdf",
    "NUMBER": 10,
    "lang": "zh"
})
```

### 大纲生成

```python
from ai_services.workflows.catalog_analysis import CatalogAnalysisWorkflow

# 文本输入 - 话题模式
workflow = CatalogAnalysisWorkflow(form="text", mode="topic")
result = workflow.run(params={
    "TOPIC": "Python编程基础",
    "lang": "zh"
})

# 文本输入 - 全文模式
workflow = CatalogAnalysisWorkflow(form="text", mode="full")
result = workflow.run(params={
    "TEXT_CONTENT": "完整的文本内容...",
    "lang": "zh"
})

# 文件上传 - 全文模式
workflow = CatalogAnalysisWorkflow(form="file", mode="full")
# 需要使用 AI 服务的 chat_with_files 方法
```

## API 接口路由

### 闪卡生成接口
- `POST /api/flashcards/generate/text/` - 文本生成闪卡（支持 topic/full/section 模式）
- `POST /api/flashcards/generate/file/` - 文件生成闪卡（支持 topic/full/section 模式）
- `POST /api/flashcards/generate/url/` - URL 生成闪卡

### 大纲生成接口
- `POST /api/catalog/topic/` - 基于话题生成大纲
- `POST /api/catalog/text/` - 基于文本生成大纲
- `POST /api/catalog/file/` - 基于文件生成大纲

## 提示词加载流程

```
1. 调用 load_prompt(card_type, lang, form, mode)
   ↓
2. 根据 card_type 和 form 选择文件
   - catalog_analysis + text → prompts_catalog_text.yaml
   - catalog_analysis + file → prompts_catalog_file.yaml
   - basic_card + text → prompts_flashcard_text.yaml
   - basic_card + file → prompts_flashcard_file.yaml
   ↓
3. 读取 YAML 文件
   ↓
4. 获取数据：data[card_type][mode][lang]
   ↓
5. 返回提示词字典 {"prompt": "..."}
```

## 关键设计优势

1. **高度模块化**：每种输入形式独立的提示词文件，便于维护和优化
2. **灵活扩展**：新增卡片类型或模式只需添加对应的 YAML 配置
3. **语言支持**：同一提示词支持多语言，便于国际化
4. **占位符机制**：提示词中使用占位符，运行时动态替换，提高复用性
5. **清晰分层**：form（输入形式）和 mode（生成模式）两个维度，覆盖所有使用场景

## 未来扩展方向

- 支持更多卡片类型（如图片遮挡、音频卡片）
- 支持更多语言（日语、韩语、法语等）
- 支持自定义提示词模板
- 支持提示词版本管理和 A/B 测试
