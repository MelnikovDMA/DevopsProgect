FROM python:3.8-slim-buster
WORKDIR /app
COPY app/requirements.txt ./
RUN pip install python-dotenv flask-sqlalchemy flask-migrate psycopg2-binary
COPY app .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "./app.py"]
