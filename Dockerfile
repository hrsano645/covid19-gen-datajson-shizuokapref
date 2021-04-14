# pythonの実行環境をロード
FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY patients.py $PROJECT_ROOTDIR
COPY gen_newsjson.py $PROJECT_ROOTDIR
COPY requirements.txt $PROJECT_ROOTDIR
COPY tests/  $PROJECT_ROOTDIR/tests/
COPY bat.sh $PROJECT_ROOTDIR
RUN python -m venv .venv
RUN . .venv/bin/activate

CMD ["bash", "./bat.sh"]