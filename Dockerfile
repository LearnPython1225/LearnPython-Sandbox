# 使用轻量级 Python 基础镜像
FROM python:3.10-slim

# 创建工作目录
WORKDIR /sandbox

# 拷贝运行文件到容器
COPY run_code.py /sandbox/run_code.py
COPY app.py /sandbox/app.py

# 安装必要的依赖
RUN pip install --no-cache-dir --upgrade pip

# 默认命令
CMD ["python3", "app.py"]