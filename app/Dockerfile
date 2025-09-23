FROM python:3.14.0rc3-slim-trixie

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY static/ /app/static/

EXPOSE 80

CMD ["python", "app.py"]