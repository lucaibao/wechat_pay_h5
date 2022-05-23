FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt ./
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY . .
CMD [ "/bin/bash"]
