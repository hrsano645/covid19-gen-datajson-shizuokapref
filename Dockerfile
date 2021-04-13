# pythonの実行環境をロード
FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY patients.py $PROJECT_ROOTDIR
COPY gen_newsjson.py $PROJECT_ROOTDIR
COPY requirements.txt $PROJECT_ROOTDIR
COPY bat.sh $PROJECT_ROOTDIR

CMD ["bash", "./bat.sh"]