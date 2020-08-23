FROM python:3
MAINTAINER Your Name "fazlur0504@gmail.com"
RUN mkdir -p /sevoucher/backend
COPY . /sevoucher/backend
RUN pip install -r /sevoucher/backend/requirements.txt
WORKDIR /sevoucher/backend
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]

