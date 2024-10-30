FROM python:3.10.14

RUN mkdir -p /home/needle_pmc

COPY requirements.txt /home/needle_pmc

WORKDIR /home/needle_pmc

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . /home/needle_pmc

CMD ["python", "main.py"]
