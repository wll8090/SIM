from flask import render_template

def rotas(app):
    @app.route('/doc/')
    def doc():
        return render_template('doc.html')