from computer_shop.celery import app

@app.task
def test():
    print('Работает')