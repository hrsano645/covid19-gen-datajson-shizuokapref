# pythonの実行環境をロード
FROM python:3.8 as python

# こちらを参考に試す
# https://blog.a-1.dev/post/2019-06-30-docker-volume/

ENV PROJECT_ROOTDIR /code
WORKDIR $PROJECT_ROOTDIR

VOLUME ["./dist", "%{$PROJECT_ROOTDIR}"]

RUN pwd
RUN mkdir dist
RUN ls -la
RUN echo test > dist/test.txt

CMD ["echo", "test"]


# RUN pwd

# # 環境をコピー
# COPY patients.py $PROJECT_ROOTDIR
# COPY gen_newsjson.py $PROJECT_ROOTDIR
# COPY requirements.txt $PROJECT_ROOTDIR
# COPY docker_bat.sh $PROJECT_ROOTDIR
# # COPY . $PROJECT_ROOTDIR

# # 実行
# RUN pip install -r requirements.txt
# # RUN mkdir ./dist
# RUN ls -la
# RUN bash ./docker_bat.sh

# CMD ["echo", "end docker covid19-datagen"]