FROM python:3.8

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY techtrends/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY techtrends /app/

RUN python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]