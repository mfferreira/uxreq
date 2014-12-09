cd ~/lib/uxreq-code/uxreq
quit()

python -i

from request import HttpResponse, HTTP_RESPONSE, get
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client
from untwisted.network import Spin, xmap, core
import sys

HEADER = {
'Host':'127.0.0.1',
'User-Agent':"uxreq/1.0", 
'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
'Keep-Alive':'300',
'Connection':'keep-alive',
}


ADDR   = '127.0.0.1'
PORT   = 80
con    = Spin()

data   = get('/', header=HEADER)
data

Client(con)
con.connect_ex((ADDR, PORT))


def set_up_con(con):
    Stdin(con)
    Stdout(con)
    
    HttpResponse(con)
    con.dump(data)
    
    print 'installing http_response'

def handle_http_response(spin, version, code, reason, header, message):
    print 'message', repr(message)
    print 'version', version
    print 'code', code
    print 'header', header


xmap(con, CONNECT, set_up_con)
xmap(con, HTTP_RESPONSE, handle_http_response)
xmap(con, CLOSE, lambda con, err: lose(con))
xmap(con, CLOSE, lambda con, err: sys.stdout.write('Closed !\n'))
core.gear.mainloop()

##############################################################################
quit()
python -i

from request import HttpResponse, HTTP_RESPONSE, get
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client
from untwisted.network import Spin, xmap, core
import sys

HEADER = {
'Host':'127.0.0.1',
'User-Agent':"uxreq/1.0", 
'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
'Connection':'close',
}


ADDR   = '127.0.0.1'
PORT   = 80
con    = Spin()

data   = get('/', header=HEADER)
data

Client(con)
con.connect_ex((ADDR, PORT))


def set_up_con(con):
    Stdin(con)
    Stdout(con)
    
    HttpResponse(con)
    # Clients using Connection: close shouldn't
    # destroy the spin on CLOSE but on HTTP_RESPONSE.
    # It might sound odd at first though.
    # 
    xmap(con, HTTP_RESPONSE, lambda con, *args: lose(con))
    
    con.dump(data)
    
    print 'installing http_response'

def handle_http_response(spin, version, code, reason, header, message):
    print 'message', repr(message)
    print 'version', version
    print 'code', code
    print 'header', header


xmap(con, CONNECT, set_up_con)
xmap(con, HTTP_RESPONSE, handle_http_response)
xmap(con, CLOSE, lambda con, err: sys.stdout.write('Closed !\n'))
core.gear.mainloop()

