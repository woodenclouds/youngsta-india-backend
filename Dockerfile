# Use an official Python runtime as a parent image
FROM python:3.8.2

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install gunicorn
RUN pip install -r requirements.txt


# Copy the Django project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

CMD ['python','manage.py','makemigrations']
CMD ['python','manage.py','migrate']

# Run the application
CMD ["gunicorn", "server.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["python","manage.py","runserver"]