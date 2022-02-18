FROM nytimes/blender:2.93-cpu-ubuntu18.04

ARG FUNCTION_DIR="/home/app/"
RUN mkdir -p ${FUNCTION_DIR}
COPY app/* ${FUNCTION_DIR}
RUN pip install boto3
RUN pip install awslambdaric --target ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

ENTRYPOINT [ "/bin/2.93/python/bin/python3.9", "-m", "awslambdaric" ]

CMD [ "app.handler" ]