# Sử dụng image Ubuntu 24.04 làm cơ sở
FROM ubuntu:24.04

# Cập nhật và cài đặt các gói cần thiết
RUN apt-get update && \
    apt-get install -y software-properties-common wget build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Tải và cài đặt Python 3.8.10
RUN wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz && \
    tar -xf Python-3.8.10.tgz && \
    cd Python-3.8.10 && \
    ./configure --enable-optimizations && \
    make && \
    make install && \
    cd .. && \
    rm -rf Python-3.8.10 Python-3.8.10.tgz

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Copy the rest of the application code
COPY . .

# Tạo và kích hoạt venv, sau đó cài đặt các phụ thuộc Python
# RUN python3.8 -m venv venv && \
#     . venv/bin/activate && \
#     pip install --upgrade pip && \
#     pip install -r requirements.txt
RUN python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install -r requirements.txt

# Đặt biến môi trường để sử dụng venv theo mặc định
# ENV PATH="/app/venv/bin:$PATH"

# Chạy ứng dụng khi container khởi động
CMD ["python3.8", "main.py"]