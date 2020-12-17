FROM python:3.9.1
WORKDIR /usr/src/kasjflow
# Lets us print without worrying about flushing the output buffer
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "kasjflow.py"]