from ldap3 import Server, Connection, ALL
from conf import host_sli

server=Server(host_sli , get_info=ALL)

def login_user(user, pwd):
    user=user+'@server.local'
    try:
        con= Connection(server,user,pwd)
        return con.bind() 
    except:
        return '000'
