# AnkiGenix 学习内容策略：资料 + 闪卡混合模式

## 核心问题

**Q: AI教练应该只生成闪卡，还是生成完整学习资料？**

**A: 生成"系统学习资料 + 配套闪卡"的完整解决方案** ⭐

---

## 为什么需要学习资料？

### 学习的两个阶段

```
阶段1：理解学习（Understanding）
├── 需要：系统性学习资料、讲义、示例、练习
├── 方式：阅读、理解、实践
└── 产出：建立知识框架

阶段2：记忆巩固（Memorization）
├── 需要：闪卡、复习、测试
├── 方式：间隔重复、主动回忆
└── 产出：长期记忆
```

**只提供闪卡 = 只覆盖阶段2 = 用户体验不完整**

### 用户真实需求场景

**场景1：完全零基础用户**
```
用户："我想学Python，完全零基础"

❌ 只给闪卡的问题：
- 用户看到闪卡一脸懵："什么是变量？什么是函数？"
- 用户需要自己去找教程、看视频，然后再回来用闪卡
- 体验割裂，用户流失

✅ 学习资料 + 闪卡：
- 先给用户系统的Python入门讲义
- 每个章节配套闪卡用于巩固
- 一站式体验，用户留存
```

**场景2：有基础的进阶用户**
```
用户："我会Python基础，想学习数据分析"

✅ 学习资料 + 闪卡都需要：
- 生成数据分析学习路线（Pandas → NumPy → Matplotlib）
- 每个库的使用文档和代码示例
- 配套闪卡记忆常用API和最佳实践
```

**场景3：应试备考用户**
```
用户："我要考日语N2"

✅ 学习资料 + 闪卡都需要：
- N2语法总结文档
- N2核心词汇列表
- N2阅读理解技巧
- 配套闪卡：词汇卡、语法卡、例句卡
```

---

## 产品定位对比

| 产品 | 提供内容 | 优势 | 劣势 |
|------|---------|------|------|
| **Anki** | 只是工具，不提供内容 | 间隔重复算法强大 | 用户需要自己制作卡片 |
| **ChatGPT** | 可以生成任何内容 | 灵活、强大 | 不系统、不专业、需要多次prompt |
| **在线课程平台** | 视频课程 + 练习 | 内容专业 | 价格贵、时间长、缺少记忆工具 |
| **AnkiGenix 1.0** | 只生成闪卡 | 快速、方便 | 缺少学习资料，用户需自己找内容 |
| **AnkiGenix 2.0** ⭐ | **学习资料 + 闪卡 + AI教练** | 一站式、系统化、个性化 | 需要开发 |

---

## 推荐架构：分层内容生成系统

### 第一层：学习计划（Learning Plan）
```json
{
  "plan_id": "plan_123",
  "topic": "Python编程",
  "duration_weeks": 8,
  "phases": [
    {
      "phase_id": 1,
      "name": "Python基础语法",
      "duration_weeks": 2,
      "content_modules": ["变量与数据类型", "控制流", "函数"]
    },
    {
      "phase_id": 2,
      "name": "面向对象编程",
      "duration_weeks": 2,
      "content_modules": ["类与对象", "继承与多态", "特殊方法"]
    }
  ]
}
```

### 第二层：学习资料（Learning Materials）⭐ 新增

每个content_module生成结构化学习资料：

#### 2.1 学习文档（Markdown格式）

```markdown
# 第1阶段第1模块：变量与数据类型

## 学习目标
- 理解什么是变量
- 掌握Python的基本数据类型
- 能够进行类型转换

---

## 1. 什么是变量？

### 1.1 概念
变量就像是一个"容器"，用来存储数据。在Python中，你不需要提前声明变量类型。

### 1.2 变量命名规则
- 只能包含字母、数字、下划线
- 不能以数字开头
- 区分大小写
- 不能使用Python关键字

### 1.3 示例代码
```python
# 创建变量
name = "Alice"
age = 25
height = 1.68

# 打印变量
print(name)  # 输出: Alice
print(age)   # 输出: 25
```

---

## 2. Python基本数据类型

### 2.1 整数（int）
用于表示整数，如：1, 100, -50

```python
count = 10
year = 2024
```

### 2.2 浮点数（float）
用于表示小数，如：3.14, -0.5

```python
price = 19.99
temperature = -5.5
```

### 2.3 字符串（str）
用于表示文本，用引号包裹

```python
name = "Alice"
message = 'Hello, World!'
```

### 2.4 布尔值（bool）
只有两个值：True 或 False

```python
is_student = True
is_adult = False
```

---

## 3. 类型转换

有时候需要将一种类型转换为另一种类型：

```python
# 字符串转整数
age_str = "25"
age_int = int(age_str)  # 25

# 整数转字符串
count = 100
count_str = str(count)  # "100"

# 字符串转浮点数
price_str = "19.99"
price_float = float(price_str)  # 19.99
```

---

## 4. 练习题

### 练习1：创建变量
创建以下变量：
- 你的姓名（字符串）
- 你的年龄（整数）
- 你的身高（浮点数）
- 你是否是学生（布尔值）

### 练习2：类型转换
将字符串 "123" 转换为整数，然后加上 10

### 练习3：综合应用
编写程序，输入用户姓名和年龄，然后输出：
"你好，{姓名}！你今年{年龄}岁了。"

---

## 5. 常见错误

### 错误1：变量未定义
```python
print(x)  # NameError: name 'x' is not defined
```
**解决**：使用前先定义变量

### 错误2：类型转换失败
```python
int("abc")  # ValueError: invalid literal for int()
```
**解决**：确保字符串是有效数字

---

## 6. 本章小结

✅ 变量是存储数据的容器
✅ Python有4种基本数据类型：int, float, str, bool
✅ 可以使用int(), float(), str()进行类型转换
✅ 变量命名要遵循规则

---

## 下一步
完成练习题后，继续学习下一个模块：**控制流**
```

#### 2.2 代码示例库（Code Examples）

```json
{
  "module_id": "variables_and_types",
  "examples": [
    {
      "title": "创建和使用变量",
      "code": "name = \"Alice\"\nage = 25\nprint(f\"{name} is {age} years old\")",
      "explanation": "使用f-string格式化输出",
      "difficulty": "easy"
    },
    {
      "title": "类型转换综合示例",
      "code": "user_input = input(\"Enter your age: \")\nage = int(user_input)\nif age >= 18:\n    print(\"You are an adult\")",
      "explanation": "从用户输入获取字符串，转换为整数后判断",
      "difficulty": "medium"
    }
  ]
}
```

#### 2.3 互动练习题（Interactive Exercises）

```json
{
  "module_id": "variables_and_types",
  "exercises": [
    {
      "id": "ex_001",
      "type": "fill_in_blank",
      "question": "将字符串\"100\"转换为整数的函数是 ____",
      "answer": "int",
      "hints": ["这是一个内置函数", "函数名是类型的缩写"]
    },
    {
      "id": "ex_002",
      "type": "code_output",
      "question": "以下代码的输出是什么？\nx = 10\ny = \"20\"\nprint(x + int(y))",
      "answer": "30",
      "explanation": "int(y)将字符串\"20\"转换为整数20，然后10+20=30"
    },
    {
      "id": "ex_003",
      "type": "code_correction",
      "question": "以下代码有错误，请修正：\nage = input(\"Enter age: \")\nif age > 18:\n    print(\"Adult\")",
      "error": "比较字符串和整数会出错",
      "answer": "age = int(input(\"Enter age: \"))\nif age > 18:\n    print(\"Adult\")",
      "explanation": "input()返回字符串，需要先转换为整数"
    }
  ]
}
```

#### 2.4 实践项目（Mini Project）

```json
{
  "module_id": "variables_and_types",
  "project": {
    "title": "个人信息管理器",
    "description": "创建一个程序，收集用户的姓名、年龄、身高，并计算BMI",
    "requirements": [
      "使用input()获取用户输入",
      "进行必要的类型转换",
      "计算BMI = 体重(kg) / 身高(m)²",
      "输出格式化结果"
    ],
    "starter_code": "# 个人信息管理器\n\n# TODO: 获取用户姓名\nname = input(\"请输入姓名：\")\n\n# TODO: 获取年龄并转换为整数\n\n# TODO: 获取身高和体重\n\n# TODO: 计算BMI\n\n# TODO: 输出结果",
    "solution": "# 完整解决方案\nname = input(\"请输入姓名：\")\nage = int(input(\"请输入年龄：\"))\nheight = float(input(\"请输入身高(米)：\"))\nweight = float(input(\"请输入体重(kg)：\"))\n\nbmi = weight / (height ** 2)\n\nprint(f\"姓名：{name}\")\nprint(f\"年龄：{age}岁\")\nprint(f\"BMI：{bmi:.2f}\")"
  }
}
```

### 第三层：配套闪卡（Flashcards）

基于学习资料自动生成配套闪卡：

#### 3.1 概念理解卡（Concept Cards）

```json
{
  "card_type": "basic",
  "source_module": "variables_and_types",
  "cards": [
    {
      "question": "什么是Python中的变量？",
      "answer": "变量是存储数据的容器，可以理解为给数据起的\"名字\"，用来在程序中引用和操作数据。",
      "tags": ["概念", "基础"]
    },
    {
      "question": "Python有哪4种基本数据类型？",
      "answer": "1. int（整数）\n2. float（浮点数）\n3. str（字符串）\n4. bool（布尔值）",
      "tags": ["概念", "基础"]
    }
  ]
}
```

#### 3.2 代码记忆卡（Code Memory Cards）

```json
{
  "card_type": "basic",
  "source_module": "variables_and_types",
  "cards": [
    {
      "question": "如何将字符串\"123\"转换为整数？",
      "answer": "使用int()函数：\nnum = int(\"123\")\n# num的值为整数123",
      "tags": ["代码", "类型转换"]
    },
    {
      "question": "如何使用f-string输出变量？",
      "answer": "name = \"Alice\"\nage = 25\nprint(f\"{name} is {age} years old\")\n# 输出：Alice is 25 years old",
      "tags": ["代码", "字符串格式化"]
    }
  ]
}
```

#### 3.3 填空卡（Cloze Cards）

```json
{
  "card_type": "cloze",
  "source_module": "variables_and_types",
  "cards": [
    {
      "text": "在Python中，{{c1::int}}用于表示整数，{{c2::float}}用于表示浮点数，{{c3::str}}用于表示字符串。",
      "tags": ["填空", "数据类型"]
    },
    {
      "text": "将字符串转换为整数使用{{c1::int()}}函数，将整数转换为字符串使用{{c2::str()}}函数。",
      "tags": ["填空", "类型转换"]
    }
  ]
}
```

#### 3.4 选择题卡（Multiple Choice Cards）

```json
{
  "card_type": "multiple_choice",
  "source_module": "variables_and_types",
  "cards": [
    {
      "question": "以下哪个变量名是合法的？",
      "options": [
        "2name",
        "name-2",
        "name_2",
        "name 2"
      ],
      "correct_index": 2,
      "explanation": "变量名不能以数字开头，不能包含连字符或空格，但可以使用下划线。",
      "tags": ["选择题", "变量命名"]
    }
  ]
}
```

---

## 内容生成工作流

### Workflow 1: 学习资料生成工作流（新增）

```python
# ai_services/workflows/learning_material_generation.py

class LearningMaterialGenerationWorkflow:
    """
    学习资料生成工作流

    输入：学习模块信息（主题、难度、用户基础）
    输出：结构化学习资料（Markdown文档 + 代码示例 + 练习题）
    """

    def __init__(self, ai_service):
        self.ai_service = ai_service

    def generate(self, module_info: dict) -> dict:
        """
        生成学习资料

        Args:
            module_info: {
                "topic": "变量与数据类型",
                "phase": "Python基础语法",
                "user_level": "零基础",
                "learning_style": "理论+实践",
                "language": "zh"
            }

        Returns:
            {
                "document": "Markdown格式的学习文档",
                "examples": [代码示例列表],
                "exercises": [练习题列表],
                "project": 实践项目
            }
        """
        # 1. 生成学习文档
        document = self._generate_document(module_info)

        # 2. 生成代码示例
        examples = self._generate_code_examples(module_info)

        # 3. 生成练习题
        exercises = self._generate_exercises(module_info)

        # 4. 生成实践项目
        project = self._generate_project(module_info)

        return {
            "document": document,
            "examples": examples,
            "exercises": exercises,
            "project": project
        }

    def _generate_document(self, module_info: dict) -> str:
        """生成Markdown格式的学习文档"""
        prompt = self._load_prompt("learning_document_generation.yaml")
        prompt = prompt.format(**module_info)

        result = self.ai_service.chat(prompt)
        return result

    def _generate_code_examples(self, module_info: dict) -> list:
        """生成代码示例"""
        prompt = self._load_prompt("code_examples_generation.yaml")
        prompt = prompt.format(**module_info)

        result = self.ai_service.chat(prompt)
        return result

    def _generate_exercises(self, module_info: dict) -> list:
        """生成练习题"""
        prompt = self._load_prompt("exercises_generation.yaml")
        prompt = prompt.format(**module_info)

        result = self.ai_service.chat(prompt)
        return result

    def _generate_project(self, module_info: dict) -> dict:
        """生成实践项目"""
        prompt = self._load_prompt("project_generation.yaml")
        prompt = prompt.format(**module_info)

        result = self.ai_service.chat(prompt)
        return result
```

### Workflow 2: 闪卡生成工作流（优化现有）

```python
# ai_services/workflows/flashcard_generate.py

class FlashcardGenerateWorkflow:
    """
    闪卡生成工作流（优化版）

    新增功能：基于学习资料生成配套闪卡
    """

    def generate_from_learning_material(self, material: dict, card_config: dict) -> list:
        """
        基于学习资料生成配套闪卡

        Args:
            material: {
                "document": "学习文档内容",
                "examples": [代码示例],
                "key_concepts": [核心概念列表]
            }
            card_config: {
                "concept_cards": 10,  # 概念理解卡数量
                "code_cards": 5,      # 代码记忆卡数量
                "cloze_cards": 8,     # 填空卡数量
                "choice_cards": 5     # 选择题卡数量
            }

        Returns:
            [闪卡列表]
        """
        all_cards = []

        # 1. 生成概念理解卡
        concept_cards = self._generate_concept_cards(
            material["document"],
            material.get("key_concepts", []),
            card_config.get("concept_cards", 10)
        )
        all_cards.extend(concept_cards)

        # 2. 生成代码记忆卡
        code_cards = self._generate_code_cards(
            material["examples"],
            card_config.get("code_cards", 5)
        )
        all_cards.extend(code_cards)

        # 3. 生成填空卡
        cloze_cards = self._generate_cloze_cards(
            material["document"],
            card_config.get("cloze_cards", 8)
        )
        all_cards.extend(cloze_cards)

        # 4. 生成选择题卡
        choice_cards = self._generate_choice_cards(
            material["document"],
            card_config.get("choice_cards", 5)
        )
        all_cards.extend(choice_cards)

        return all_cards
```

---

## 用户体验流程

### 完整学习路径（Coach Mode）

```
1. AI对话（5-7个问题）
   ↓
2. 生成学习计划
   ├── 阶段1：Python基础语法（2周）
   ├── 阶段2：面向对象编程（2周）
   └── 阶段3：常用库和工具（2周）
   ↓
3. 为每个阶段生成学习资料 ⭐ 新增
   ├── 学习文档（Markdown）
   ├── 代码示例库
   ├── 互动练习题
   └── 实践项目
   ↓
4. 基于学习资料生成配套闪卡
   ├── 概念理解卡
   ├── 代码记忆卡
   ├── 填空卡
   └── 选择题卡
   ↓
5. 用户开始学习
   ├── 第1天：阅读学习文档 → 看代码示例 → 做练习题
   ├── 第2天：复习昨天的闪卡 → 学习新内容
   ├── 第3天：完成实践项目 → 复习闪卡
   └── ...
   ↓
6. 每日任务推送
   ├── 今日学习：第1阶段 - 变量与数据类型（文档）
   ├── 今日练习：完成5道练习题
   ├── 今日复习：15张闪卡
   └── 本周项目：个人信息管理器
   ↓
7. 学习进度追踪
   ├── 文档阅读完成度
   ├── 练习题正确率
   ├── 闪卡掌握率
   └── 项目完成情况
```

### 快速模式（Quick Mode）- 保持不变

```
用户输入学习材料 → 快速生成闪卡 → 下载.apkg文件
```

---

## 数据库设计（新增表）

### learning_materials 表

```sql
CREATE TABLE learning_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES learning_plans(id),
    phase_id VARCHAR(50),
    module_id VARCHAR(100),
    module_title VARCHAR(200),

    -- 学习资料内容
    document_content TEXT,  -- Markdown格式文档
    examples JSONB,         -- 代码示例列表
    exercises JSONB,        -- 练习题列表
    project JSONB,          -- 实践项目

    -- 元数据
    difficulty VARCHAR(20), -- easy/medium/hard
    estimated_time_minutes INT,  -- 预计学习时长
    tags TEXT[],

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_learning_materials_plan ON learning_materials(plan_id);
CREATE INDEX idx_learning_materials_module ON learning_materials(module_id);
```

### user_learning_progress 表（扩展）

```sql
CREATE TABLE user_learning_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    material_id UUID REFERENCES learning_materials(id),

    -- 进度追踪
    document_read BOOLEAN DEFAULT FALSE,
    document_read_at TIMESTAMP,

    exercises_completed INT DEFAULT 0,
    exercises_total INT,
    exercises_correct_rate FLOAT,  -- 正确率

    project_started BOOLEAN DEFAULT FALSE,
    project_completed BOOLEAN DEFAULT FALSE,
    project_submitted_at TIMESTAMP,

    -- 闪卡进度
    flashcards_total INT,
    flashcards_learned INT,
    flashcards_mastered INT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## API设计（新增端点）

### 学习资料相关API

```python
# 获取学习资料
GET /api/v1/materials/{material_id}

# 获取计划的所有学习资料
GET /api/v1/plans/{plan_id}/materials

# 标记文档为已读
POST /api/v1/materials/{material_id}/mark-read

# 提交练习题答案
POST /api/v1/materials/{material_id}/exercises/submit
Body: {
    "exercise_id": "ex_001",
    "answer": "int"
}

# 提交项目
POST /api/v1/materials/{material_id}/project/submit
Body: {
    "code": "...",
    "notes": "..."
}

# 获取学习进度
GET /api/v1/materials/{material_id}/progress
```

---

## 前端页面设计（新增）

### 1. 学习资料阅读页面

```
/learn/{material_id}

组件结构：
- LearningMaterialViewer.tsx
  ├── MarkdownRenderer.tsx       // Markdown渲染器
  ├── CodeExampleCard.tsx        // 代码示例卡片（带运行按钮）
  ├── ExerciseSection.tsx        // 练习题区域
  ├── ProjectSection.tsx         // 实践项目区域
  └── ProgressBar.tsx            // 学习进度条
```

### 2. 每日学习页面（改造）

```
/tasks（原来只有闪卡任务，现在扩展）

今日任务：
┌─────────────────────────────────┐
│ 📚 学习任务                      │
│ ├── 阅读：变量与数据类型文档     │
│ ├── 练习：完成5道练习题          │
│ └── 项目：开始个人信息管理器     │
├─────────────────────────────────┤
│ 📇 闪卡复习                      │
│ ├── 新卡片：10张                 │
│ └── 复习卡片：15张               │
└─────────────────────────────────┘
```

### 3. 学习计划详情页（改造）

```
/plan/{plan_id}（增加学习资料标签）

标签页：
- 概览（Overview）
- 学习资料（Materials）⭐ 新增
- 闪卡库（Flashcards）
- 进度分析（Analytics）
```

---

## 实施优先级

### Phase 1：核心MVP（Week 1-4）

- [ ] 学习资料生成工作流
  - [ ] 文档生成（Markdown）
  - [ ] 代码示例生成
  - [ ] 基础练习题生成

- [ ] 前端资料展示
  - [ ] Markdown渲染器
  - [ ] 代码高亮显示
  - [ ] 基础阅读界面

- [ ] 闪卡与资料关联
  - [ ] 修改闪卡生成工作流
  - [ ] 支持基于资料生成闪卡

### Phase 2：互动功能（Week 5-6）

- [ ] 互动练习题系统
  - [ ] 练习题提交和评分
  - [ ] 实时反馈
  - [ ] 错误分析

- [ ] 实践项目系统
  - [ ] 项目模板生成
  - [ ] 代码提交
  - [ ] AI代码审查（可选）

### Phase 3：进度追踪（Week 7-8）

- [ ] 学习进度数据库
- [ ] 进度可视化
- [ ] 完成度统计

---

## 总结：产品定位

**AnkiGenix 2.0 = AI学习教练 + 完整学习解决方案**

```
不仅仅是闪卡工具，而是：

1. 学习内容生成器
   ├── 系统学习文档
   ├── 代码示例库
   ├── 互动练习题
   └── 实践项目

2. 记忆巩固工具
   └── 基于学习内容的配套闪卡

3. 学习教练
   ├── AI对话式规划
   ├── 每日任务推送
   ├── 进度追踪分析
   └── 个性化建议
```

**差异化竞争优势**：
- ✅ 比ChatGPT更系统、更专业
- ✅ 比在线课程更灵活、更个性化
- ✅ 比Anki提供更完整的学习内容
- ✅ 一站式解决"学习 + 记忆"两个阶段

🚀 让我们构建一个真正能帮助用户从零到精通的学习平台！
