from conf import *
import load_sys
load_sys.load_sys()
from flask import Flask
from objetos.avaliador.routes import rotas
from objetos.candidato.rota_for_candidato import creat_rotas


def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='#D#$FW$%HGVE%YJ¨NHEdwedeDEDEdeDWRGcRthgvh'
    creat_rotas(app)    # rotas de candiadato
    IO=rotas(app)       # rota de servidor

    return IO, app

if __name__ == '__main__':
    IO, app=create_app()
    IO.run(app, debug=debug, host=host_app, port=port, allow_unsafe_werkzeug=True)
