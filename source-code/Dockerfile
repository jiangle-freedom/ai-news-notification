FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p data logs

# 设置文件权限
RUN chmod +x main.py

# 暴露端口（如果需要）
# EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30m --timeout=10s --start-period=1m --retries=3 \
    CMD python main.py --mode status || exit 1

# 运行应用
CMD ["python", "main.py", "--mode", "run"]
