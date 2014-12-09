from untwisted.utils.stdio import LOAD, CLOSE
from untwisted.network import Spin, xmap, get_event, spawn, zmap

HTTP_RESPONSE = get_event()

class HttpResponse(object):

    def __init__(self, spin):

        """

        """

        xmap(spin, LOAD, self.store_request)
        self.spin    = spin
        self.header  = bytearray()
        self.message = None

    def store_request(self, spin, data):
        DELIM = '\r\n\r\n'
    
        self.header.extend(data)

        if not DELIM in data:
            return

        self.header, self.message  = self.header.split(DELIM, 1)
        self.response, self.header = self.split_header(str(self.header))

        self.determine_connection_type()
        zmap(spin, LOAD, self.store_request)

    def split_header(self, data):
        DELIM_LINE     = '\r\n'
        DELIM_PAIR     = ': '
        DELIM_RESPONSE = ' '

        data           = data.split(DELIM_LINE)
        response       = data[0]
        response       = response.split(DELIM_RESPONSE)
        header         = dict()

        del data[0]

        for ind in data:
            key, value  = ind.split(DELIM_PAIR, 1)
            header[key] = value

        return response, header

    def determine_connection_type(self):
        print 'determine_connection_type', self.header

        type = self.header.get('Connection')

        if type == 'Keep-Alive':
            self.keep_alive(self.header['Content-Length'])
        elif type == 'close':
            self.non_keep_alive()

    def keep_alive(self, content_length):
        print 'keep alive', content_length

        self.content_length = int(content_length)
        is_complete         = self.check_message_length()

        if is_complete: 
            return

        xmap(self.spin, LOAD, self.store_message_with_length)

    def store_message_with_length(self, spin, data):
        print 'store_message_with_length'
        self.message.extend(data)
        self.check_message_length()

    def check_message_length(self):
        if not len(self.message) >= self.content_length:
            return False
        spawn(self.spin, HTTP_RESPONSE, self.response[0], self.response[1], 
                            self.response[2], self.header, self.message)
        return True

    def non_keep_alive(self):
        print 'non_keep_alive'
        xmap(self.spin, LOAD, self.store_message)

        xmap(self.spin, CLOSE, 
             lambda spin, err: spawn(self.spin, HTTP_RESPONSE, self.response[0], self.response[1], 
                                    self.response[2], self.header, self.message))

    def store_message(self, spin, data):
        self.message.extend(data)

class HttpCode(object):
    def __init__(self, spin):
        xmap(spin, HTTP_RESPONSE, self.spawn_method)

    def spawn_method(self, spin, version, code, reason, header, message):
        spawn(spin, code, version, reason, header, message)

def get(rsc, args={}, version='HTTP/1.1', header={}):
    from urllib import urlencode
    args = '?%s' % urlencode(args) if args else ''
    data  = 'GET %s%s %s\r\n' % (rsc, args, version)

    for key, value in header.iteritems():
        data = data + '%s: %s\r\n' % (key, value)
    data = data + '\r\n'
    return data

def post(addr, rsc, args, header):
    pass






