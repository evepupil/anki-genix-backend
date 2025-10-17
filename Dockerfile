# 使用 Python 3.12.8 官方镜像作为基础镜像
FROM python:3.12.8-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs && \
    touch logs/anki_genix.log && \
    chmod 666 logs/anki_genix.log

# 创建导出目录
RUN mkdir -p exports && \
    chmod 777 exports

# 暴露端口（fly.io 默认使用 8080）
EXPOSE 8080

# 启动命令 - 使用 gunicorn 运行 Django
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "wsgi:application"]
