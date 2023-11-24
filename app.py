from flask import Flask
from conf import *
from routes import rotas

def create_app():
    app=Flask(__name__)

    rotas(app)

    return app

if __name__ == '__main__':
    create_app().run(debug=debug, host=host, port=port)