# pythonの実行環境をロード
FROM python:3.8 as python

ENV PROJECT_ROOTDIR /code

WORKDIR $PROJECT_ROOTDIR

# 環境をコピー
COPY . $PROJECT_ROOTDIR

# 実行
RUN pip install -r requirements.txt

RUN bash ./bat.sh

CMD ["tail", "-n", "10", "news.json"]