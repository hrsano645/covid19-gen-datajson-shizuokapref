# pythonの実行環境をロード
FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY requirements.txt $PROJECT_ROOTDIR
RUN python -m venv .venv
RUN .venv/bin/python -m pip install -r requirements.txt

CMD ["bash", "./bat.sh"]