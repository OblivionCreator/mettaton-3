FROM python:3.11
WORKDIR /app
COPY . /app
RUN pwd
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]