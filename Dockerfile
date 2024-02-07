from python:3

WORKDIR /main

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install flask ldap3 flask_cors
RUN python3 -m pip install mysql-connector-python pandas ldap3 flask_socketio flask_cors
RUN python3 -m pip install PyPDF2 Unidecode
RUN python3 -m pip install gunicorn pycryptodome


RUN mkdir main

RUN cd /main/

RUN ls

CMD ["python3", "app.py"]
