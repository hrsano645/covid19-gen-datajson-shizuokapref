FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY patients.py $PROJECT_ROOTDIR
COPY docker_bat.sh $PROJECT_ROOTDIR

CMD ["bash", "./docker_bat.sh"]