from ldap3 import Server, Connection, ALL
from conf import host_sli
import sys

server=Server(host_sli, get_info=ALL)


def login_user(user, pwd):
    user=user+'@server.local'
    if user.upper() in sys.argv.get('autorizados'):
        try:
            con= Connection(server,user,pwd)
            return con.bind() 
        except:
            return '000'
    else:
        return False
