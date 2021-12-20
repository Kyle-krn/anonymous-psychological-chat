from .flask_settings import app

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'Привет'

