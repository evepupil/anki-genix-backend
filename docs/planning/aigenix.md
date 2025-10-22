📋 MVP功能拆解

  1️⃣ 首页（Landing Page）

  ┌─────────────────────────────────────┐
  │         [Logo] LearnAI              │
  ├─────────────────────────────────────┤
  │                                     │
  │       今天你想学习什么？              │
  │                                     │
  │   利用AI生成最适合你的个性化学习内容   │
  │                                     │
  │         [立即体验] 按钮               │
  │                                     │
  └─────────────────────────────────────┘

  技术实现：
  - 复用AnkiGenix的首页框架
  - 超级简单，一个大标题 + CTA按钮
  - 点击后跳转 /learn 或 /console

  ---
  2️⃣ 学习配置页（Console - Step 1）

  ┌─────────────────────────────────────┐
  │  告诉我们你的学习情况                 │
  ├─────────────────────────────────────┤
  │                                     │
  │  1. 你想学什么？                     │
  │     [输入框: React Hooks]           │
  │                                     │
  │  2. 你的基础水平？                   │
  │     ○ 零基础                        │
  │     ○ 有一些了解                    │
  │     ● 比较熟悉，想深入               │
  │                                     │
  │  3. 你的学习目的？                   │
  │     [输入框: 准备面试]               │
  │                                     │
  │         [生成学习计划]               │
  └─────────────────────────────────────┘

  技术实现：
  // 前端数据结构
  interface LearningConfig {
    topic: string;          // "React Hooks"
    level: 'beginner' | 'intermediate' | 'advanced';
    goal: string;           // "准备面试"
  }

  // API调用
  POST /api/courses/generate-outline
  {
    "topic": "React Hooks",
    "level": "intermediate",
    "goal": "准备面试"
  }

  后端实现：
  # business/course.py
  class CourseBusiness:
      def generate_course_outline(self, topic, level, goal):
          """生成课程大纲"""

          # 构建prompt
          prompt = f"""
          用户想学习：{topic}
          基础水平：{level}
          学习目的：{goal}

          请生成一个个性化的学习大纲，包含5-8个章节。
          每个章节要有：
          - 章节标题
          - 章节描述
          - 预计学习时长
          - 难度等级

          返回JSON格式...
          """

          # 调用AI（复用AnkiGenix的AI服务）
          result = self.ai_service.chat(prompt)

          # 解析返回的大纲
          outline = parse_json(result)

          # 保存到数据库
          course_id = self.save_course_outline(outline)

          return {
              "success": True,
              "course_id": course_id,
              "outline": outline
          }

  ---
  3️⃣ 大纲确认页（Console - Step 2）

  ┌─────────────────────────────────────┐
  │  为你生成的学习计划                   │
  ├─────────────────────────────────────┤
  │                                     │
  │  📚 React Hooks 完全指南             │
  │  预计学习时长: 6小时                 │
  │                                     │
  │  ✓ 第1章: 什么是Hooks (30min)       │
  │  ✓ 第2章: useState详解 (45min)      │
  │  ✓ 第3章: useEffect实战 (60min)     │
  │  ✓ 第4章: 自定义Hooks (45min)       │
  │  ✓ 第5章: 性能优化 (50min)          │
  │  ✓ 第6章: 面试常见问题 (40min)      │
  │                                     │
  │  [重新生成]  [开始学习]              │
  └─────────────────────────────────────┘

  技术实现：
  // 展示大纲
  interface CourseOutline {
    id: string;
    title: string;
    totalDuration: number;
    chapters: Chapter[];
  }

  interface Chapter {
    id: string;
    order: number;
    title: string;
    description: string;
    duration: number;  // 分钟
    difficulty: string;
  }

  // 如果点"重新生成"，重新调用API
  // 如果点"开始学习"，跳转到学习页面

  ---
  4️⃣ 学习页面（Learning Page）

  ┌─────────────────────────────────────┐
  │ [<返回] 第1章: 什么是Hooks    [1/6]  │
  ├─────────────────────────────────────┤
  │                                     │
  │  [AI生成的章节内容区域]              │
  │                                     │
  │  ## 什么是React Hooks？             │
  │                                     │
  │  React Hooks是React 16.8引入的...  │
  │  ...（markdown渲染）                │
  │                                     │
  │  [代码示例区域]                      │
  │  ```jsx                             │
  │  const [count, setCount] = ...      │
  │  ```                                │
  │                                     │
  │                                     │
  ├─────────────────────────────────────┤
  │  [上一章]     [下一章]               │
  │                                     │
  │              [💬 AI助手]  ← 右下角   │
  │              [📝 生成闪卡]           │
  └─────────────────────────────────────┘

  技术实现：

  章节内容生成（实时）

  # business/course.py
  def generate_chapter_content(self, course_id, chapter_id):
      """生成章节内容"""

      # 获取课程和章节信息
      course = self.get_course(course_id)
      chapter = self.get_chapter(chapter_id)

      # 构建prompt
      prompt = f"""
      课程主题：{course.topic}
      用户水平：{course.level}
      学习目标：{course.goal}

      当前章节：{chapter.title}
      章节描述：{chapter.description}

      请生成详细的教学内容，包括：
      1. 概念讲解（通俗易懂）
      2. 代码示例（带注释）
      3. 实战练习建议
      4. 常见问题解答

      返回markdown格式...
      """

      # 调用AI生成内容
      content = self.ai_service.chat(prompt)

      # 保存到数据库
      self.save_chapter_content(chapter_id, content)

      return {
          "success": True,
          "content": content  # markdown格式
      }

  AI助手对话

  # business/course.py
  def chat_with_ai(self, course_id, chapter_id, user_question):
      """AI实时答疑"""

      # 获取上下文
      course = self.get_course(course_id)
      chapter = self.get_chapter(chapter_id)
      chapter_content = self.get_chapter_content(chapter_id)

      # 构建prompt（带上下文）
      prompt = f"""
      你是一个{course.topic}的教学助手。

      当前学习章节：{chapter.title}
      章节内容摘要：{chapter_content[:500]}...

      学生问题：{user_question}

      请给出清晰、准确的回答，必要时提供代码示例。
      """

      # 调用AI对话
      answer = self.ai_service.chat(prompt)

      return {
          "success": True,
          "answer": answer
      }

  生成闪卡（复用AnkiGenix）

  # 直接调用AnkiGenix的功能
  def generate_flashcards_for_chapter(self, chapter_id):
      """为当前章节生成闪卡"""

      # 获取章节内容
      content = self.get_chapter_content(chapter_id)

      # 调用AnkiGenix的业务逻辑
      flashcard_biz = FlashcardBusiness()
      result = flashcard_biz.generate_flashcards_from_text(
          text=content,
          card_number=5,  # 每章生成5张闪卡
          lang="zh"
      )

      # 关联到课程
      self.link_flashcards_to_course(chapter_id, result['cards'])

      return result

  ---
  🗄️ 数据库设计

  -- 课程表
  CREATE TABLE courses (
      id VARCHAR(36) PRIMARY KEY,
      user_id VARCHAR(36) NOT NULL,
      topic VARCHAR(255) NOT NULL,
      level ENUM('beginner', 'intermediate', 'advanced'),
      goal TEXT,
      status ENUM('draft', 'learning', 'completed') DEFAULT 'draft',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  );

  -- 章节表
  CREATE TABLE chapters (
      id VARCHAR(36) PRIMARY KEY,
      course_id VARCHAR(36) NOT NULL,
      order_num INT NOT NULL,
      title VARCHAR(255) NOT NULL,
      description TEXT,
      duration INT,  -- 分钟
      difficulty VARCHAR(50),
      content TEXT,  -- markdown内容
      is_completed BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (course_id) REFERENCES courses(id)
  );

  -- 学习记录表
  CREATE TABLE learning_progress (
      id VARCHAR(36) PRIMARY KEY,
      user_id VARCHAR(36) NOT NULL,
      course_id VARCHAR(36) NOT NULL,
      chapter_id VARCHAR(36) NOT NULL,
      progress INT DEFAULT 0,  -- 0-100
      time_spent INT DEFAULT 0,  -- 秒
      last_position INT,  -- 滚动位置
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      FOREIGN KEY (course_id) REFERENCES courses(id),
      FOREIGN KEY (chapter_id) REFERENCES chapters(id)
  );

  -- AI对话记录表（可选）
  CREATE TABLE chat_history (
      id VARCHAR(36) PRIMARY KEY,
      user_id VARCHAR(36) NOT NULL,
      course_id VARCHAR(36) NOT NULL,
      chapter_id VARCHAR(36),
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- 闪卡关联表
  CREATE TABLE course_flashcards (
      id VARCHAR(36) PRIMARY KEY,
      course_id VARCHAR(36) NOT NULL,
      chapter_id VARCHAR(36),
      flashcard_data JSON,  -- 存储闪卡内容
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (course_id) REFERENCES courses(id)
  );

  ---
  🎨 前端路由设计

  /                    → 首页（Landing Page）
  /login               → 登录（复用AnkiGenix）
  /register            → 注册（复用AnkiGenix）
  /learn               → 学习配置页
  /learn/outline/:id   → 大纲确认页
  /learn/course/:id    → 学习页面（带章节导航）
  /learn/course/:id/chapter/:chapterId  → 具体章节学习
  /dashboard           → 用户中心（我的课程列表）

  ---
  🚀 MVP开发排期（2-3周）

  Week 1: 核心功能

  Day 1-2: 后端基础
  - ✅ 创建数据库表
  - ✅ 实现课程大纲生成API
  - ✅ 实现章节内容生成API

  Day 3-4: 前端基础
  - ✅ 首页设计和实现
  - ✅ 学习配置页（表单）
  - ✅ 大纲确认页

  Day 5-7: 学习页面
  - ✅ 章节内容展示（markdown渲染）
  - ✅ 章节导航（上一章/下一章）
  - ✅ 进度保存

  Week 2: 交互功能

  Day 8-10: AI助手
  - ✅ AI对话界面（右下角弹窗）
  - ✅ 对话API实现
  - ✅ 对话历史保存

  Day 11-12: 闪卡集成
  - ✅ 集成AnkiGenix的闪卡生成
  - ✅ 闪卡预览和管理
  - ✅ 导出功能

  Day 13-14: 用户系统
  - ✅ 登录/注册（复用AnkiGenix）
  - ✅ 我的课程列表
  - ✅ 学习进度展示

  Week 3: 优化和测试

  Day 15-17: 优化
  - ✅ 性能优化（加载速度）
  - ✅ UI/UX优化
  - ✅ 移动端适配

  Day 18-19: 测试
  - ✅ 功能测试
  - ✅ Bug修复
  - ✅ 邀请用户内测

  Day 20-21: 上线准备
  - ✅ 部署到生产环境
  - ✅ 配置域名和SSL
  - ✅ 准备推广素材

  ---
  💰 MVP商业模式

  免费版（吸引用户）

  - ✅ 可以生成1门完整课程
  - ✅ AI对话：每天20次
  - ✅ 闪卡生成：每章5张

  会员版（¥49/月 或 ¥399/年）

  - ✅ 无限生成课程
  - ✅ AI对话：无限次
  - ✅ 闪卡生成：无限
  - ✅ 学习数据分析
  - ✅ 导出课程PDF

  ---
  🎯 MVP的核心价值主张

  对用户：

  1. 个性化 - 根据你的水平和目标定制
  2. 高效 - 直接学核心内容，不浪费时间
  3. 互动 - 随时问AI，立即得到解答
  4. 记忆 - 学完自动生成闪卡，巩固记忆

  对比传统学习：

  | 传统方式         | LearnAI        |
  |--------------|----------------|
  | 看视频教程（1-2小时） | AI生成精简内容（30分钟） |
  | 遇到问题要去搜索/问人  | 立即问AI助手        |
  | 学完容易忘记       | 自动生成闪卡复习       |
  | 内容固定，不适合所有人  | 完全个性化定制        |

  ---
  🔧 技术栈建议

  后端（复用AnkiGenix）

  - ✅ Django + FastAPI
  - ✅ 深度求索AI API
  - ✅ SQLite（MVP阶段）
  - ✅ 复用认证、支付模块

  前端

  - ✅ Next.js 15
  - ✅ React 19
  - ✅ Tailwind CSS
  - ✅ Markdown渲染：react-markdown
  - ✅ 代码高亮：prism.js
  - ✅ 复用AnkiGenix的组件库

  ---
  ✅ MVP成功标准

  技术指标：

  - ✅ 大纲生成：3秒内完成
  - ✅ 章节内容生成：10秒内完成
  - ✅ AI对话响应：2秒内
  - ✅ 页面加载：1秒内

  业务指标（前3个月）：

  - 🎯 注册用户：500+
  - 🎯 付费用户：50+（10%转化率）
  - 🎯 月营收：¥2,500+
  - 🎯 用户完成率：30%+（完成至少1门课程）

  ---
  🚨 MVP阶段要避免的坑

  ❌ 不要做的事情：

  1. 过度优化AI prompt - 够用就行，后期再优化
  2. 复杂的课程管理后台 - MVP阶段用户量小，手动处理即可
  3. 社区/论坛功能 - 分散精力，暂不需要
  4. 多种课程模板 - 只做一种通用模板
  5. 精美的UI设计 - 简洁干净即可，先验证需求

  ✅ 要做的事情：

  1. 快速上线 - 3周内必须能让用户使用
  2. 收集反馈 - 加微信群，直接和用户聊
  3. 数据埋点 - 知道用户在哪里卡住了
  4. 迭代优化 - 根据真实数据改进

  ---
  🎉 总结

  你的MVP设计非常棒！核心功能清晰，技术栈可复用，3周内完全可以做出来。

  建议立即开始：
  1. 复制AnkiGenix的代码仓库
  2. 创建新的course模块
  3. 实现大纲生成API（第一个里程碑）
  4. 快速迭代，尽快让用户试用