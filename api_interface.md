# Anki-GenIX 业务API接口文档

## 目录分析

### 1. AI生成知识目录
- **接口路径**：`POST /api/catalog/`
- **描述**：用户输入主题，AI分析并返回结构化知识目录
- **请求参数**：
  ```json
  {
    "topic": "机器学习基础",
    "lang": "zh"
  }
  ```
- **响应示例**：
  ```json
  [
    {
      "chapter": "机器学习基础概念",
      "description": "介绍机器学习的基本概念和应用场景",
      "sections": [
        {
          "section": "什么是机器学习",
          "description": "机器学习的定义和历史发展"
        }
      ]
    }
  ]
  ```

---

## 闪卡生成与管理

### 2. 生成闪卡
- **接口路径**：`POST /api/flashcards/`
- **描述**：用户选择目录中的章节，AI生成对应章节的闪卡
- **请求参数**：
  ```json
  {
    "card_type": "basic_card",  // basic_card | cloze_card | multiple_choice_card
    "topic": "机器学习基础概念",
    "number": 10,
    "lang": "zh"
  }
  ```
- **响应示例**（以basic_card为例）：
  ```json
  [
    {"question": "什么是机器学习？", "answer": "机器学习是人工智能的一个分支..."},
    ...
  ]
  ```

### 3. 闪卡内容检视与管理
- **接口路径**：`POST /api/flashcards/review/`
- **描述**：用户检视、筛选、上报错误、标记通过的闪卡
- **请求参数**：
  ```json
  {
    "cards": [
      {"question": "...", "answer": "...", "status": "approved"}, // approved | rejected | error
      ...
    ]
  }
  ```
- **响应**：操作结果（可选）

---

## Anki文件导出

### 4. 导出Anki文件
- **接口路径**：`POST /api/flashcards/export/`
- **描述**：用户勾选通过的闪卡，导出Anki支持的文件（apkg/csv）
- **请求参数**：
  ```json
  {
    "deck_name": "机器学习基础-精选闪卡",
    "card_type": "basic_card",
    "cards": [
      {"question": "...", "answer": "..."},
      ...
    ],
    "export_type": "apkg" // apkg | csv
  }
  ```
- **响应**：
  ```json
  {
    "file_url": "/media/exports/机器学习基础-精选闪卡_basic_card_123456789.apkg"
  }
  ```

---

## 可选：历史记录与用户管理

### 5. 获取用户历史目录
- **接口路径**：`GET /api/catalog/history/`

### 6. 获取用户历史闪卡
- **接口路径**：`GET /api/flashcards/history/`

### 7. 用户登录/注册
- **接口路径**：`POST /api/auth/login/`、`POST /api/auth/register/`

---

## 接口一览表

| 功能           | 方法 | 路径                        | 说明                     |
|----------------|------|-----------------------------|--------------------------|
| 目录分析       | POST | /api/catalog/               | AI生成知识目录           |
| 生成闪卡       | POST | /api/flashcards/            | AI生成指定类型闪卡       |
| 闪卡检视管理   | POST | /api/flashcards/review/     | 用户筛选/上报/通过闪卡   |
| 导出Anki文件   | POST | /api/flashcards/export/     | 导出apkg/csv文件         |
| 历史目录       | GET  | /api/catalog/history/       | 可选，获取历史目录       |
| 历史闪卡       | GET  | /api/flashcards/history/    | 可选，获取历史闪卡       |
| 用户登录/注册  | POST | /api/auth/login/            | 可选，用户管理           | 