FROM python:3

ADD ./chat_app /chat_app

WORKDIR /chat_app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]