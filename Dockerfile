from python:3

WORKDIR /main

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install flask ldap3 flask_cors
RUN python3 -m pip install mysql-connector-python pandas ldap3 flask_socketio flask_cors
RUN python3 -m pip install PyPDF2 Unidecode



RUN mkdir main

CMD ["python3","/main/app.py"]

