# pythonの実行環境をロード
FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY requirements.txt $PROJECT_ROOTDIR

ENV VIRTUAL_ENV=.venv
RUN python3 -m venv .venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt

CMD ["bash", "./bat.sh"]