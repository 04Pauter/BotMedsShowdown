from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def index():
    return "Hello. I am alive!"

def run():
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def keep_alive():
    server = Thread(target=run)
    server.start()
