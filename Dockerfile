FROM python:3.5-alpine
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
