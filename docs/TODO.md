# AnkiGenIX 后端待办事项

## 任务验证功能优化

### 【待实现】前端创建任务时记录内容长度

**背景**：
- 当前后端已实现文本和URL的长度验证功能
- 验证逻辑：对比 `input_data.text_length` 或 `input_data.url_length` 与实际提交内容的长度
- 目的：防止用户使用不同的内容绕过任务系统

**前端需要做的改动**：

#### 1. 创建文本类型任务时
在 `input_data` 中添加 `text_length` 字段：

```javascript
// 前端创建任务
const textContent = "用户输入的文本内容...";

const taskData = {
  user_id: userId,
  task_type: "text",
  workflow_type: "direct_generate",
  status: "processing",
  input_data: {
    text_length: textContent.length,  // 记录文本长度
    language: "zh",
    card_count: 10
  }
};

// 插入到 Supabase task_info 表
await supabase.from('task_info').insert(taskData);
```

#### 2. 创建URL类型任务时
在 `input_data` 中添加 `url_length` 字段：

```javascript
// 前端创建任务
const url = "https://example.com/article";

const taskData = {
  user_id: userId,
  task_type: "web",
  workflow_type: "direct_generate",
  status: "processing",
  input_data: {
    url_length: url.length,  // 记录URL长度
    language: "zh",
    card_count: 10
  }
};

// 插入到 Supabase task_info 表
await supabase.from('task_info').insert(taskData);
```

**后端验证逻辑**（已实现）：
- 文本接口：`/api/flashcards/generate/text/`
  - 验证 `len(text_content) == input_data.text_length`
- URL接口：`/api/flashcards/generate/url/`
  - 验证 `len(url) == input_data.url_length`

**注意事项**：
- 如果 `input_data` 中没有 `text_length` 或 `url_length` 字段，后端会跳过长度验证（向后兼容）
- 长度验证失败时，API 返回 400 错误

**优先级**：低
**状态**：暂缓实现
**记录时间**：2025-10-14

---

## 其他待办事项

（后续可在此添加新的待办事项）
