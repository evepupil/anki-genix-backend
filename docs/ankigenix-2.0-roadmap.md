# AnkiGenix 2.0 产品规划 - AI学习教练

## 产品愿景

从"闪卡生成工具"升级为"AI驱动的个性化学习教练平台"

**核心价值主张**：通过AI对话式交互，深度理解用户的学习目标、基础水平和时间安排，生成个性化学习计划和高质量Anki闪卡，并提供持续的学习陪伴和进度追踪。

---

## 为什么用户会选择AnkiGenix而不是直接用ChatGPT？

### 核心差异化优势

1. **省心 - AI主动提问，用户被动回答**
   - ChatGPT：用户需要主动思考如何描述需求，组织提示词
   - AnkiGenix：AI教练主动问5-7个结构化问题，用户只需回答

2. **省时 - 一键导出，无需手动格式化**
   - ChatGPT：需要手动复制、格式化、导入Anki
   - AnkiGenix：直接生成标准Anki格式，一键下载.apkg文件

3. **专业 - 针对学习场景深度优化**
   - ChatGPT：通用AI助手，学习只是功能之一
   - AnkiGenix：专门为学习设计，融合间隔重复算法、记忆曲线、学习心理学

4. **陪伴 - 持续追踪和提醒**
   - ChatGPT：对话结束后无后续追踪
   - AnkiGenix：每日学习提醒、进度追踪、薄弱点分析、学习报告

5. **价格 - 更经济的选择**
   - ChatGPT Plus：$20/月，通用功能
   - AnkiGenix Professional：$29.9/月，学习场景专业优化 + 持续陪伴
   - AnkiGenix Personal：$14.9/月，基础学习功能

---

## 产品架构 - 双模式设计

### 模式1：快速模式（Quick Mode）- 保留现有功能
适合已经明确知道学习内容的用户

**流程**：
```
用户输入学习材料 → AI快速生成闪卡 → 下载/预览
```

**特点**：
- 快速、简单、直接
- 支持文本/文件/网页输入
- 3-5分钟完成

---

### 模式2：教练模式（Coach Mode）- 新增核心功能 ⭐
适合需要系统学习规划的用户

**流程**：
```
AI对话式提问（5-7个问题）→ 分析用户画像 → 生成个性化学习计划 → 分阶段生成闪卡 → 每日任务推送 → 进度追踪和优化
```

---

## 核心功能设计

### 📋 功能1：AI对话式学习规划

#### 对话流程设计（5-7个问题）

- [ ] **问题1：学习目标**
  ```
  你想学习什么？（例如：Python编程、日语N2、考研英语）
  ```
  - 支持自由输入或选择常见主题
  - AI自动识别学习领域和难度级别

- [ ] **问题2：当前基础**
  ```
  你目前的{学习主题}水平如何？
  A. 完全零基础，从未接触过
  B. 有一些基础，了解基本概念
  C. 中等水平，能独立完成简单任务
  D. 较高水平，只是想查漏补缺
  ```

- [ ] **问题3：学习目的**
  ```
  你的学习目的是什么？
  A. 应试（考试、认证）
  B. 工作需要（职业技能）
  C. 个人兴趣（业余爱好）
  D. 其他（自定义）
  ```

- [ ] **问题4：时间预算**
  ```
  你每天能投入多少学习时间？
  A. 15-30分钟（碎片时间）
  B. 30-60分钟（每天固定）
  C. 1-2小时（充裕时间）
  D. 2小时以上（全力投入）
  ```

- [ ] **问题5：学习周期**
  ```
  你希望在多长时间内达到目标？
  A. 1个月内（快速掌握）
  B. 3个月内（稳步提升）
  C. 6个月内（系统学习）
  D. 1年以上（长期规划）
  ```

- [ ] **问题6：学习材料（可选）**
  ```
  你有现成的学习材料吗？
  A. 有教材/课程（上传文件/链接）
  B. 没有，让AI推荐
  ```

- [ ] **问题7：学习偏好（可选）**
  ```
  你更喜欢哪种学习方式？
  A. 理论先行（系统学习概念）
  B. 实践导向（边做边学）
  C. 混合学习（理论+实践）
  ```

#### 技术实现 Checklist

- [ ] 后端：创建学习规划对话流API端点
  - [ ] `POST /api/v1/coach/start-session` - 开始教练对话
  - [ ] `POST /api/v1/coach/answer` - 提交答案并获取下一个问题
  - [ ] `POST /api/v1/coach/generate-plan` - 生成学习计划

- [ ] 数据库：学习计划相关表设计
  - [ ] `coach_sessions` 表（对话会话）
  - [ ] `learning_plans` 表（学习计划）
  - [ ] `study_goals` 表（学习目标）
  - [ ] `user_profiles` 表（用户学习画像）

- [ ] AI工作流：对话式规划工作流
  - [ ] 创建 `CoachDialogueWorkflow` 类
  - [ ] 设计对话状态机（问题跳转逻辑）
  - [ ] 编写学习计划生成提示词模板

- [ ] 前端：教练模式UI组件
  - [ ] `CoachModeSelector.tsx` - 模式选择器
  - [ ] `CoachDialogue.tsx` - 对话界面
  - [ ] `QuestionCard.tsx` - 问题卡片组件
  - [ ] `ProgressIndicator.tsx` - 进度指示器（5/7问题完成）

---

### 📊 功能2：个性化学习计划生成

#### 学习计划内容结构

- [ ] **基本信息**
  - 学习主题和目标
  - 用户基础水平评估
  - 预计完成时间
  - 每日学习时间分配

- [ ] **学习路径规划**
  - 阶段1：基础知识构建（Week 1-2）
  - 阶段2：核心概念深化（Week 3-4）
  - 阶段3：实践应用（Week 5-6）
  - 阶段4：综合复习（Week 7-8）

- [ ] **闪卡生成计划**
  - 每阶段生成的闪卡数量
  - 闪卡类型分布（基础卡/填空卡/选择题）
  - 复习时间表（基于间隔重复算法）

- [ ] **里程碑和检查点**
  - 每周学习目标
  - 阶段性测试/评估
  - 完成标准

#### 技术实现 Checklist

- [ ] 后端API
  - [ ] `GET /api/v1/plans/{plan_id}` - 获取学习计划详情
  - [ ] `POST /api/v1/plans` - 创建学习计划
  - [ ] `PUT /api/v1/plans/{plan_id}` - 更新学习计划
  - [ ] `DELETE /api/v1/plans/{plan_id}` - 删除学习计划

- [ ] AI学习计划生成器
  - [ ] `LearningPlanGeneratorWorkflow` 类
  - [ ] 学习路径规划算法（根据用户画像）
  - [ ] 闪卡数量动态计算（基于时间预算和目标）
  - [ ] 学习计划提示词模板（YAML）

- [ ] 前端学习计划展示
  - [ ] `LearningPlanCard.tsx` - 计划卡片
  - [ ] `RoadmapTimeline.tsx` - 学习路线图时间轴
  - [ ] `MilestoneTracker.tsx` - 里程碑追踪器
  - [ ] `PlanOverview.tsx` - 计划总览页面

---

### 🎯 功能3：每日学习任务和提醒

#### 每日任务系统

- [ ] **任务类型**
  - 新卡片学习（New Cards）
  - 复习卡片（Review Cards）
  - 薄弱点强化（Weak Points）
  - 阶段性测试（Milestone Test）

- [ ] **推送提醒**
  - 每日固定时间推送（用户可自定义）
  - 邮件提醒：学习任务清单
  - 站内通知：今日任务和进度
  - 可选：短信提醒（付费功能）

- [ ] **任务完成追踪**
  - 打卡记录（连续学习天数）
  - 完成进度（今日任务完成率）
  - 学习时长统计

#### 技术实现 Checklist

- [ ] 后端任务系统
  - [ ] `daily_tasks` 表（每日任务）
  - [ ] `study_sessions` 表（学习会话记录）
  - [ ] `study_streaks` 表（连续学习记录）
  - [ ] `GET /api/v1/tasks/daily` - 获取今日任务
  - [ ] `POST /api/v1/tasks/{task_id}/complete` - 标记任务完成
  - [ ] `GET /api/v1/tasks/streak` - 获取连续学习天数

- [ ] 定时任务和提醒
  - [ ] Celery Beat定时任务配置
  - [ ] 每日任务生成器（凌晨生成第二天任务）
  - [ ] 邮件提醒服务（SendGrid/AWS SES）
  - [ ] 站内通知服务
  - [ ] 用户提醒时间偏好设置

- [ ] 前端每日任务界面
  - [ ] `DailyTaskPanel.tsx` - 每日任务面板
  - [ ] `TaskCard.tsx` - 单个任务卡片
  - [ ] `StreakCounter.tsx` - 连续学习天数计数器
  - [ ] `StudyTimer.tsx` - 学习计时器

---

### 📈 功能4：学习进度追踪和分析

#### 数据追踪维度

- [ ] **基础数据**
  - 总学习天数
  - 总学习时长
  - 已掌握卡片数量
  - 复习准确率

- [ ] **深度分析**
  - 薄弱知识点识别（错误率>50%的卡片）
  - 学习曲线可视化（每周掌握卡片数）
  - 遗忘曲线分析（间隔重复效果）
  - 学习效率评分（时间投入vs掌握程度）

- [ ] **个性化建议**
  - AI生成的改进建议
  - 推荐复习时间调整
  - 推荐学习资源

#### 技术实现 Checklist

- [ ] 后端分析API
  - [ ] `GET /api/v1/analytics/overview` - 学习概览
  - [ ] `GET /api/v1/analytics/progress` - 进度数据
  - [ ] `GET /api/v1/analytics/weak-points` - 薄弱点分析
  - [ ] `GET /api/v1/analytics/suggestions` - AI建议
  - [ ] `study_analytics` 表（学习分析数据）
  - [ ] `weak_points` 表（薄弱知识点）

- [ ] AI分析工作流
  - [ ] `LearningAnalyticsWorkflow` 类
  - [ ] 薄弱点识别算法
  - [ ] 改进建议生成（基于学习数据）
  - [ ] 学习效率评分算法

- [ ] 前端分析仪表板
  - [ ] `AnalyticsDashboard.tsx` - 分析仪表板
  - [ ] `ProgressChart.tsx` - 进度图表（Chart.js/Recharts）
  - [ ] `WeakPointsList.tsx` - 薄弱点列表
  - [ ] `AIRecommendations.tsx` - AI建议卡片
  - [ ] `LearningCurve.tsx` - 学习曲线可视化

---

### 👥 功能5：社区功能（可选，增强用户粘性）

- [ ] **学习小组**
  - 创建/加入学习小组
  - 小组学习计划和打卡
  - 小组排行榜

- [ ] **卡组分享**
  - 用户可分享自己的卡组
  - 浏览和下载社区卡组
  - 卡组评分和评论

- [ ] **排行榜**
  - 全站学习时长排行
  - 连续学习天数排行
  - 周/月学习之星

- [ ] **成就系统**
  - 连续学习徽章（7天、30天、100天）
  - 卡片掌握徽章（100张、500张、1000张）
  - 分享和创作徽章

#### 技术实现 Checklist

- [ ] 后端社区API
  - [ ] `study_groups` 表（学习小组）
  - [ ] `shared_decks` 表（分享卡组）
  - [ ] `achievements` 表（成就系统）
  - [ ] `leaderboards` 视图（排行榜）
  - [ ] `POST /api/v1/community/groups` - 创建小组
  - [ ] `GET /api/v1/community/decks` - 浏览社区卡组
  - [ ] `GET /api/v1/community/leaderboard` - 排行榜

- [ ] 前端社区界面
  - [ ] `CommunityHub.tsx` - 社区中心页面
  - [ ] `StudyGroupCard.tsx` - 学习小组卡片
  - [ ] `DeckMarketplace.tsx` - 卡组市场
  - [ ] `Leaderboard.tsx` - 排行榜
  - [ ] `AchievementBadges.tsx` - 成就徽章展示

---

## 页面架构重构

### 新增页面

- [ ] `/coach` - 教练模式入口页
- [ ] `/coach/dialogue` - AI对话界面
- [ ] `/plan` - 我的学习计划页面
- [ ] `/plan/{plan_id}` - 学习计划详情页
- [ ] `/tasks` - 每日任务页面
- [ ] `/analytics` - 学习分析仪表板
- [ ] `/community` - 社区中心（可选）

### 改造现有页面

- [ ] `/dashboard` - 添加模式选择器（Quick Mode / Coach Mode）
- [ ] `/dashboard` - 添加今日任务快捷入口
- [ ] `/dashboard` - 添加学习进度概览卡片
- [ ] `/features` - 更新功能介绍（加入AI教练特性）
- [ ] `/pricing` - 更新定价方案（区分功能）

---

## 定价策略

### Free Plan（免费试用）
- [ ] Quick Mode：每月3次快速生成
- [ ] Coach Mode：体验1次完整对话（生成简化版学习计划）
- [ ] 每日任务提醒：无
- [ ] 学习分析：基础数据

### Personal Plan（$14.9/月）
- [ ] Quick Mode：无限次快速生成
- [ ] Coach Mode：每月2个学习计划
- [ ] 每日任务提醒：邮件提醒
- [ ] 学习分析：完整数据+基础建议
- [ ] 导出：标准Anki格式

### Professional Plan（$29.9/月）⭐ 推荐
- [ ] Quick Mode：无限次快速生成
- [ ] Coach Mode：无限个学习计划
- [ ] 每日任务提醒：邮件+站内通知
- [ ] 学习分析：深度分析+AI个性化建议
- [ ] 社区功能：学习小组、卡组分享
- [ ] 优先AI响应速度
- [ ] 导出：多种格式（Anki/Quizlet/CSV）

---

## 12周实施计划

### Week 1-2：基础架构和数据模型 🏗️

- [ ] **后端数据库设计**
  - [ ] 设计并创建所有新表（learning_plans, coach_sessions, daily_tasks等）
  - [ ] 编写数据库迁移脚本
  - [ ] 添加必要的索引和约束

- [ ] **AI工作流框架**
  - [ ] 创建 `CoachDialogueWorkflow` 基类
  - [ ] 创建 `LearningPlanGeneratorWorkflow` 基类
  - [ ] 设计对话状态机

- [ ] **API端点搭建**
  - [ ] 教练对话相关API（start-session, answer, generate-plan）
  - [ ] 学习计划CRUD API
  - [ ] 基础单元测试

**交付物**：
- 完整的数据库schema
- 工作流框架代码
- API文档（Swagger）

---

### Week 3-4：AI对话式学习规划 🤖

- [ ] **前端对话界面**
  - [ ] 设计并实现 `CoachDialogue.tsx` 组件
  - [ ] 实现问题卡片和进度指示器
  - [ ] 添加动画效果（打字机效果、过渡动画）

- [ ] **AI对话逻辑**
  - [ ] 完成7个问题的提示词编写
  - [ ] 实现基于回答的动态问题跳转
  - [ ] 实现用户画像生成算法

- [ ] **学习计划生成**
  - [ ] 编写学习计划生成提示词模板
  - [ ] 实现学习路径规划算法
  - [ ] 实现闪卡数量动态计算

- [ ] **前端计划展示**
  - [ ] 实现 `LearningPlanCard.tsx`
  - [ ] 实现 `RoadmapTimeline.tsx` 时间轴
  - [ ] 实现 `/plan/{plan_id}` 详情页

**交付物**：
- 完整的教练对话流程
- 个性化学习计划生成功能
- 学习计划展示页面

---

### Week 5-6：每日任务和进度追踪 📅

- [ ] **每日任务系统**
  - [ ] 实现任务生成算法（基于学习计划和间隔重复）
  - [ ] 配置Celery Beat定时任务
  - [ ] 实现任务完成追踪API

- [ ] **提醒服务**
  - [ ] 集成邮件服务（SendGrid/AWS SES）
  - [ ] 实现邮件模板（任务提醒、进度报告）
  - [ ] 实现站内通知系统
  - [ ] 用户提醒时间偏好设置

- [ ] **前端任务界面**
  - [ ] 实现 `/tasks` 每日任务页面
  - [ ] 实现 `DailyTaskPanel.tsx` 组件
  - [ ] 实现 `StreakCounter.tsx` 连续学习天数
  - [ ] 在Dashboard添加任务快捷入口

- [ ] **学习会话记录**
  - [ ] 实现学习时长追踪
  - [ ] 实现打卡记录功能
  - [ ] 实现连续学习天数计算

**交付物**：
- 完整的每日任务系统
- 邮件和站内提醒功能
- 学习追踪和打卡功能

---

### Week 7-8：学习分析和AI建议 📊

- [ ] **数据分析后端**
  - [ ] 实现学习数据统计API
  - [ ] 实现薄弱点识别算法
  - [ ] 实现学习效率评分算法

- [ ] **AI分析工作流**
  - [ ] 创建 `LearningAnalyticsWorkflow`
  - [ ] 编写改进建议生成提示词
  - [ ] 实现基于数据��个性化建议

- [ ] **前端分析仪表板**
  - [ ] 实现 `/analytics` 分析页面
  - [ ] 集成图表库（Chart.js或Recharts）
  - [ ] 实现 `ProgressChart.tsx` 学习曲线
  - [ ] 实现 `WeakPointsList.tsx` 薄弱点列表
  - [ ] 实现 `AIRecommendations.tsx` AI建议卡片

- [ ] **Dashboard集成**
  - [ ] 在Dashboard添加学习进度概览卡片
  - [ ] 添加快速访问分析的入口
  - [ ] 添加今日学习数据摘要

**交付物**：
- 完整的学习分析仪表板
- AI驱动的个性化建议系统
- 数据可视化图表

---

### Week 9-10：社区功能和用户粘性 👥

- [ ] **学习小组功能**
  - [ ] 实现学习小组CRUD API
  - [ ] 实现小组成员管理
  - [ ] 实现小组打卡和排行榜
  - [ ] 前端小组页面开发

- [ ] **卡组分享功能**
  - [ ] 实现卡组分享API
  - [ ] 实现卡组浏览和搜索
  - [ ] 实现卡组下载功能
  - [ ] 前端卡组市场页面

- [ ] **成就系统**
  - [ ] 设计成就徽章规则
  - [ ] 实现成就检测和解锁逻辑
  - [ ] 前端成就展示界面

- [ ] **排行榜**
  - [ ] 实现排行榜数据视图
  - [ ] 前端排行榜页面

**交付物**：
- 社区中心页面
- 学习小组功能
- 卡组分享市场
- 成就和排行榜系统

---

### Week 11-12：测试、优化和上线 🚀

- [ ] **全面测试**
  - [ ] 单元测试覆盖率达到80%
  - [ ] 集成测试（API端到端测试）
  - [ ] 前端组件测试
  - [ ] 用户接受度测试（UAT）

- [ ] **性能优化**
  - [ ] 数据库查询优化（添加索引、优化查询）
  - [ ] API响应时间优化（缓存、异步处理）
  - [ ] 前端加载速度优化（代码分割、懒加载）
  - [ ] AI响应速度优化（提示词精简、模型调优）

- [ ] **安全审计**
  - [ ] API权限验证审查
  - [ ] SQL注入防护检查
  - [ ] XSS防护检查
  - [ ] 数据加密审查

- [ ] **文档完善**
  - [ ] API文档更新
  - [ ] 用户使用指南
  - [ ] 功能视频教程
  - [ ] 常见问题FAQ

- [ ] **灰度发布**
  - [ ] 选择10%用户进行灰度测试
  - [ ] 收集用户反馈
  - [ ] 修复关键问题
  - [ ] 全量发布

- [ ] **营销准备**
  - [ ] 更新官网功能介绍
  - [ ] 制作功能演示视频
  - [ ] 社交媒体宣传素材
  - [ ] Product Hunt发布准备

**交付物**：
- 完整测试报告
- 性能优化报告
- 上线发布计划
- 用户文档和视频

---

## 技术栈总结

### 后端新增技术

- [ ] **Celery Beat** - 定时任务（每日任务生成、提醒推送）
- [ ] **SendGrid/AWS SES** - 邮件服务
- [ ] **Redis** - 缓存和Celery消息队列
- [ ] **PostgreSQL JSON字段** - 存储灵活的学习计划数据

### 前端新增技术

- [ ] **Chart.js / Recharts** - 数据可视化
- [ ] **Framer Motion** - 动画效果
- [ ] **React Query** - 数据获取和缓存
- [ ] **Zustand/Redux Toolkit** - 全局状态管理（如果需要）

### AI工作流新增

- [ ] **对话状态机** - 管理多轮对话流程
- [ ] **学习路径规划算法** - 根据用户画像生成学习路径
- [ ] **间隔重复算法** - SuperMemo SM-2算法
- [ ] **数据分析工作流** - 学习数据分析和建议生成

---

## 成功指标（KPIs）

### 产品指标

- [ ] **激活率**：注册后7天内使用Coach Mode的用户比例 > 40%
- [ ] **完成率**：完成完整对话并生成学习计划的用户比例 > 60%
- [ ] **留存率**：7日留存率 > 30%，30日留存率 > 15%
- [ ] **付费转化率**：从Free转Personal/Professional > 10%

### 用户参与度指标

- [ ] **每日活跃用户（DAU）**：持续增长
- [ ] **平均学习时长**：> 20分钟/天
- [ ] **连续学习天数**：中位数 > 7天
- [ ] **任务完成率**：每日任务完成率 > 50%

### 商业指标

- [ ] **月度经常性收入（MRR）**：持续增长
- [ ] **客户生命周期价值（LTV）**：> $100
- [ ] **客户获取成本（CAC）**：< $30
- [ ] **LTV/CAC比率**：> 3

---

## 风险和挑战

### 技术风险

- [ ] **AI响应延迟**：对话式交互对响应速度要求高
  - **缓解措施**：提示词优化、模型选择、流式输出

- [ ] **数据量增长**：学习记录数据快速增长
  - **缓解措施**：数据分区、定期归档、查询优化

### 产品风险

- [ ] **用户学习曲线**：Coach Mode可能对部分用户过于复杂
  - **缓解措施**：提供详细引导、保留Quick Mode、添加演示视频

- [ ] **学习计划质量**：AI生成的学习计划可能不够精准
  - **缓解措施**：持续优化提示词、收集用户反馈、支持手动调整

### 商业风险

- [ ] **付费意愿不足**：用户可能不愿为学习工具付费
  - **缓解措施**：提供足够的免费价值、展示明确的学习效果、社交证明

- [ ] **竞争压力**：市场上可能出现类似产品
  - **缓解措施**：快速迭代、建立用户社区、积累用户数据优势

---

## 下一步行动

### 立即开始

1. [ ] **创建项目看板**：在GitHub Projects或Trello创建任务看板
2. [ ] **数据库设计评审**：与团队���审数据库schema
3. [ ] **UI/UX原型设计**：使用Figma设计教练对话界面
4. [ ] **技术选型确认**：确认Celery、邮件服务等技术栈

### 本周完成

1. [ ] **数据库迁移脚本**：完成所有新表的创建
2. [ ] **API框架搭建**：完成教练对话基础API
3. [ ] **前端路由配置**：添加新页面路由
4. [ ] **CI/CD更新**：更新测试和部署流程

---

## 附录：核心代码示例

### A. 对话状态机实现示例

```python
# ai_services/workflows/coach_dialogue.py

from enum import Enum
from typing import Dict, Optional

class DialogueState(Enum):
    """对话状态枚举"""
    START = "start"
    LEARNING_TOPIC = "learning_topic"
    CURRENT_LEVEL = "current_level"
    LEARNING_PURPOSE = "learning_purpose"
    TIME_BUDGET = "time_budget"
    LEARNING_DURATION = "learning_duration"
    MATERIALS = "materials"
    LEARNING_STYLE = "learning_style"
    COMPLETE = "complete"

class CoachDialogueWorkflow:
    """AI教练对话工作流"""

    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.state = DialogueState.START
        self.user_profile = {}

    def get_next_question(self, current_state: DialogueState, answer: Optional[str] = None) -> Dict:
        """
        根据当前状态和用户回答，获取下一个问题

        Returns:
            {
                "question": "问题文本",
                "options": ["选项A", "选项B"],  # 可选
                "next_state": DialogueState.NEXT,
                "progress": 0.3  # 进度：30%
            }
        """
        if current_state == DialogueState.START:
            return {
                "question": "你想学习什么？（例如：Python编程、日语N2、考研英语）",
                "options": None,  # 自由输入
                "next_state": DialogueState.LEARNING_TOPIC,
                "progress": 0.0
            }

        elif current_state == DialogueState.LEARNING_TOPIC:
            # 保存学习主题
            self.user_profile['topic'] = answer

            # 使用AI分析主题，确定难度级别
            topic_analysis = self._analyze_topic(answer)
            self.user_profile['topic_category'] = topic_analysis['category']

            return {
                "question": f"你目前的{answer}水平如何？",
                "options": [
                    "完全零基础，从未接触过",
                    "有一些基础，了解基本概念",
                    "中等水平，能独立完成简单任务",
                    "较高水平，只是想查漏补缺"
                ],
                "next_state": DialogueState.CURRENT_LEVEL,
                "progress": 0.14
            }

        elif current_state == DialogueState.CURRENT_LEVEL:
            self.user_profile['level'] = answer

            return {
                "question": "你的学习目的是什么？",
                "options": [
                    "应试（考试、认证）",
                    "工作需要（职业技能）",
                    "个人兴趣（业余爱好）",
                    "其他"
                ],
                "next_state": DialogueState.LEARNING_PURPOSE,
                "progress": 0.28
            }

        # ... 其他问题的逻辑

        elif current_state == DialogueState.LEARNING_STYLE:
            self.user_profile['style'] = answer

            return {
                "question": "太好了！我已经了解你的学习需求，正在为你生成个性化学习计划...",
                "options": None,
                "next_state": DialogueState.COMPLETE,
                "progress": 1.0
            }

    def _analyze_topic(self, topic: str) -> Dict:
        """使用AI分析学习主题"""
        prompt = f"分析学习主题：{topic}，返回类别（编程/语言/考试/其他）和难度级别"
        result = self.ai_service.chat(prompt)
        return {"category": result.get("category", "其他")}

    def generate_learning_plan(self) -> Dict:
        """根据用户画像生成学习计划"""
        from .learning_plan_generator import LearningPlanGeneratorWorkflow

        generator = LearningPlanGeneratorWorkflow(self.ai_service)
        plan = generator.generate(self.user_profile)
        return plan
```

### B. 学习计划生成提示词示例

```yaml
# ai_services/prompts/learning_plan_generation.yaml

name: learning_plan_generation
description: 根据用户画像生成个性化学习计划

system_prompt: |
  你是AnkiGenix的AI学习教练，专门为用户制定个性化学习计划。

  你的任务是：
  1. 分析用户的学习目标、基础水平、时间预算
  2. 设计符合用户情况的学习路径（分阶段）
  3. 为每个阶段规划闪卡生成计划
  4. 设置合理的里程碑和完成标准

  原则：
  - 计划必须符合用户的时间预算（不要过于激进）
  - 难度要循序渐进（基础->进阶->高级）
  - 结合间隔重复算法安排复习
  - 提供具体的学习资源推荐

user_prompt: |
  请为以下用户生成学习计划：

  【用户画像】
  - 学习主题：{TOPIC}
  - 当前水平：{LEVEL}
  - 学习目的：{PURPOSE}
  - 每日时间：{TIME_BUDGET}
  - 学习周期：{DURATION}
  - 学习偏好：{STYLE}

  【输出要求】
  请以JSON格式返回学习计划，包含：
  1. plan_overview: 计划总览（目标、周期、预计成果）
  2. phases: 学习阶段列表
     - phase_name: 阶段名称
     - duration_weeks: 持续周数
     - goals: 阶段目标
     - flashcard_plan: 闪卡计划
       - total_cards: 总卡片数
       - new_cards_per_day: 每日新卡片数
       - review_cards_per_day: 每日复习卡片数
     - milestones: 里程碑
  3. resources: 推荐学习资源
  4. tips: 学习建议

output_format: json
parse_strategy: json
```

### C. 每日任务生成算法示例

```python
# business/daily_task_generator.py

from datetime import datetime, timedelta
from typing import List, Dict
from business.database.daily_tasks_db import DailyTasksDB
from business.database.learning_plans_db import LearningPlansDB
from business.database.flashcard_db import FlashcardDB

class DailyTaskGenerator:
    """每日任务生成器"""

    def __init__(self):
        self.task_db = DailyTasksDB()
        self.plan_db = LearningPlansDB()
        self.card_db = FlashcardDB()

    def generate_tasks_for_user(self, user_id: str, target_date: datetime) -> List[Dict]:
        """
        为用户生成指定日期的任务

        基于：
        1. 用户的学习计划（当前阶段）
        2. 间隔重复算法（SuperMemo SM-2）
        3. 用户的历史表现（调整难度）
        """
        tasks = []

        # 1. 获取用户的活跃学习计划
        plans = self.plan_db.get_active_plans(user_id)

        for plan in plans:
            # 2. 确定当前学习阶段
            current_phase = self._get_current_phase(plan, target_date)

            if not current_phase:
                continue

            # 3. 生成新卡片学习任务
            new_cards_task = self._generate_new_cards_task(
                plan,
                current_phase,
                target_date
            )
            if new_cards_task:
                tasks.append(new_cards_task)

            # 4. 生成复习任务（基于间隔重复算法）
            review_tasks = self._generate_review_tasks(
                user_id,
                plan['id'],
                target_date
            )
            tasks.extend(review_tasks)

            # 5. 生成薄弱点强化任务（如果有）
            weak_point_task = self._generate_weak_point_task(
                user_id,
                plan['id']
            )
            if weak_point_task:
                tasks.append(weak_point_task)

        # 6. 保存任务到数据库
        for task in tasks:
            self.task_db.create_task(
                user_id=user_id,
                task_date=target_date,
                task_type=task['type'],
                task_data=task['data'],
                plan_id=task.get('plan_id')
            )

        return tasks

    def _generate_new_cards_task(self, plan: Dict, phase: Dict, target_date: datetime) -> Dict:
        """生成新卡片学习任务"""
        new_cards_per_day = phase['flashcard_plan']['new_cards_per_day']

        # 获取用户还未学习的卡片
        unlearned_cards = self.card_db.get_unlearned_cards(
            plan_id=plan['id'],
            phase_id=phase['id'],
            limit=new_cards_per_day
        )

        if not unlearned_cards:
            return None

        return {
            'type': 'new_cards',
            'plan_id': plan['id'],
            'data': {
                'card_ids': [card['id'] for card in unlearned_cards],
                'count': len(unlearned_cards),
                'estimated_time': len(unlearned_cards) * 2  # 每张卡2分钟
            }
        }

    def _generate_review_tasks(self, user_id: str, plan_id: str, target_date: datetime) -> List[Dict]:
        """
        生成复习任务（基于SuperMemo SM-2算法）

        SM-2算法：
        - 间隔 = 前一次间隔 × 难度系数
        - 难度系数根据回答质量调整（0-5分）
        """
        # 查询今天需要复习的卡片
        cards_due_for_review = self.card_db.get_cards_due_for_review(
            user_id=user_id,
            plan_id=plan_id,
            due_date=target_date
        )

        if not cards_due_for_review:
            return []

        # 按难度分组（简单/中等/困难）
        easy_cards = [c for c in cards_due_for_review if c['difficulty'] < 2.0]
        medium_cards = [c for c in cards_due_for_review if 2.0 <= c['difficulty'] < 2.5]
        hard_cards = [c for c in cards_due_for_review if c['difficulty'] >= 2.5]

        tasks = []

        if easy_cards:
            tasks.append({
                'type': 'review_easy',
                'plan_id': plan_id,
                'data': {
                    'card_ids': [c['id'] for c in easy_cards],
                    'count': len(easy_cards),
                    'estimated_time': len(easy_cards) * 1
                }
            })

        if medium_cards:
            tasks.append({
                'type': 'review_medium',
                'plan_id': plan_id,
                'data': {
                    'card_ids': [c['id'] for c in medium_cards],
                    'count': len(medium_cards),
                    'estimated_time': len(medium_cards) * 2
                }
            })

        if hard_cards:
            tasks.append({
                'type': 'review_hard',
                'plan_id': plan_id,
                'data': {
                    'card_ids': [c['id'] for c in hard_cards],
                    'count': len(hard_cards),
                    'estimated_time': len(hard_cards) * 3
                }
            })

        return tasks

    def _get_current_phase(self, plan: Dict, target_date: datetime) -> Dict:
        """根据日期确定当前学习阶段"""
        plan_start_date = datetime.fromisoformat(plan['start_date'])
        days_elapsed = (target_date - plan_start_date).days

        cumulative_weeks = 0
        for phase in plan['phases']:
            phase_weeks = phase['duration_weeks']
            if days_elapsed < (cumulative_weeks + phase_weeks) * 7:
                return phase
            cumulative_weeks += phase_weeks

        return None  # 计划已完成
```

---

## 总结

AnkiGenix 2.0将从"工具"升级为"教练"，通过AI对话式交互、个性化学习计划、每日陪伴式提醒，为用户提供完整的学习解决方案。

**核心差异化**：省心、省时、专业、陪伴、经济

**关键成功因素**：
1. AI对话体验流畅自然
2. 学习计划质量高、个性化强
3. 每日提醒和任务系统可靠
4. 学习分析有价值、建议可执行
5. 快速迭代、响应用户反馈

让我们开始实施，打造用户真正需要的AI学习教练！🚀
