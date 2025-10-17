# Fly.io 部署指南

本项目使用 Docker 和 Fly.io 进行部署。

## 前置要求

1. 安装 [flyctl](https://fly.io/docs/hands-on/install-flyctl/)
2. 注册 Fly.io 账号并登录：
   ```bash
   flyctl auth login
   ```

## 部署步骤

### 1. 首次部署

```bash
# 进入后端目录
cd anki-genix-backend

# 创建 Fly.io 应用（会使用 fly.toml 配置）
flyctl apps create anki-genix-backend

# 设置环境变量（重要！）
flyctl secrets set SECRET_KEY="your-secret-key-here"
flyctl secrets set DEBUG="False"
flyctl secrets set ALLOWED_HOSTS="your-app-name.fly.dev"

# 如果使用 Supabase
flyctl secrets set SUPABASE_URL="your-supabase-url"
flyctl secrets set SUPABASE_KEY="your-supabase-key"

# 如果使用 OpenAI/DeepSeek
flyctl secrets set OPENAI_API_KEY="your-openai-api-key"
flyctl secrets set DEEPSEEK_API_KEY="your-deepseek-api-key"

# 部署应用
flyctl deploy
```

### 2. 后续更新

```bash
# 直接部署
flyctl deploy

# 或指定 Dockerfile
flyctl deploy --dockerfile Dockerfile
```

### 3. 查看应用状态

```bash
# 查看应用状态
flyctl status

# 查看日志
flyctl logs

# 实时查看日志
flyctl logs -f

# 查看应用信息
flyctl info
```

### 4. 访问应用

```bash
# 打开应用
flyctl open

# 或访问
https://your-app-name.fly.dev/api/health
```

## 配置说明

### fly.toml 配置

- **primary_region**: 设置为 `hkg` (香港)，也可选择 `nrt` (东京) 或 `sin` (新加坡)
- **memory**: 512MB（根据需要调整）
- **auto_stop_machines**: 自动停止机器以节省成本
- **min_machines_running**: 设为 0 表示无流量时完全停止

### 环境变量

必须设置的环境变量：
- `SECRET_KEY`: Django 密钥
- `DEBUG`: 生产环境设为 False
- `ALLOWED_HOSTS`: 允许的主机名

可选环境变量：
- `SUPABASE_URL`: Supabase 项目 URL
- `SUPABASE_KEY`: Supabase API 密钥
- `OPENAI_API_KEY`: OpenAI API 密钥
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥

## 数据持久化

应用使用 Fly.io Volume 持久化数据：
- **挂载点**: `/app/data`
- **大小**: 1GB（可在 fly.toml 中调整）
- **用途**: 存储 SQLite 数据库和导出文件

## 故障排查

### 查看详细日志
```bash
flyctl logs -f
```

### SSH 进入容器
```bash
flyctl ssh console
```

### 重启应用
```bash
flyctl apps restart anki-genix-backend
```

### 查看资源使用
```bash
flyctl vm status
```

## 成本优化

- 设置 `auto_stop_machines = 'stop'` 在无流量时停止机器
- 设置 `min_machines_running = 0` 允许完全停止
- 调整 `memory` 和 `cpu` 以匹配实际需求

## 健康检查

应用提供健康检查端点：
- **URL**: `/api/health`
- **方法**: GET
- **响应**: `{"status": "healthy", "service": "anki-genix-backend"}`

## 注意事项

1. 首次部署前确保所有环境变量已设置
2. 生产环境务必设置 `DEBUG=False`
3. 定期查看日志以监控应用状态
4. SQLite 数据库存储在 Volume 中，确保定期备份
