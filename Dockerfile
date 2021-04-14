FROM python:3.8

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

COPY patients.py $PROJECT_ROOTDIR
COPY bat.sh $PROJECT_ROOTDIR
COPY ./tests $PROJECT_ROOTDIR/tests
# requirements.txtコピー

CMD ["bash", "./bat.sh"]