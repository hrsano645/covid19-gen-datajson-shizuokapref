# pythonの実行環境をロード
FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY patients.py $PROJECT_ROOTDIR
COPY gen_newsjson.py $PROJECT_ROOTDIR
COPY requirements.txt $PROJECT_ROOTDIR
COPY docker_bat.sh $PROJECT_ROOTDIR

RUN pip install -r requirements.txt

ENTRYPOINT ["bash", "./docker_bat.sh"]