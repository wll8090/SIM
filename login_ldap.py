from ldap3 import Server, Connection, ALL

server=Server('10.253.251.13', get_info=ALL)

def login_user(user, pwd):
    user=user+'@server.local'
    con= Connection(server,user,pwd)
    return con.bind() 