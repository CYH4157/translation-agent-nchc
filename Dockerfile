FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖项
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装 pip 依赖项
RUN pip install --upgrade pip

# 安装 Poetry 和 ffmpy
RUN pip install poetry ffmpy

# 克隆项目仓库
RUN git clone https://github.com/c00cjz00/translation-agent-nchc.git /translation-agent-nchc

# 切换工作目录到根目录并删除/app目录
WORKDIR /

# 定义构建时传入的参数
ARG TAIDE_API_KEY
ARG NVIDIA_API_KEY

# 修改 .env 文件以包含传入的 API keys
RUN sed -i "s|TAIDE_API_KEY=\"ey-\"|TAIDE_API_KEY=\"$TAIDE_API_KEY\"|" /translation-agent-nchc/.env && \
    sed -i "s|NVIDIA_API_KEY=\"nvapi-\"|NVIDIA_API_KEY=\"$NVIDIA_API_KEY\"|" /translation-agent-nchc/.env

# 切换到项目目录并安装项目依赖
WORKDIR /translation-agent-nchc
RUN poetry install --with app

# 设置容器启动时的默认命令
CMD ["poetry", "run"]

# Expose the port (if needed, depending on your app)
EXPOSE 7860
