FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
WORKDIR /app/project
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "project.wsgi:application","--bind","0.0.0.0:8000"]
