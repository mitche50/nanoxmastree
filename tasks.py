from celery import Celery

app = Celery()

@app.task
def print_message(message):
    print(message)
    return