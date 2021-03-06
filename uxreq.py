from untwisted.utils.stdio import LOAD, CLOSE
from untwisted.network import Spin, xmap, get_event, spawn, zmap
from urllib import urlencode

HTTP_RESPONSE = get_event()

class HttpClient(object):

    def __init__(self, spin):

        """

        """

        xmap(spin, LOAD, self.get_header)
        self.spin     = spin
        self.header   = ''
        self.data     = ''
        self.response = ''
        self.size     = 0

    def get_header(self, spin, data):
        """

        """

        DELIM       = '\r\n\r\n'
        self.header = self.header + data

        if not DELIM in data:
            return

        self.header, self.data     = self.header.split(DELIM, 1)
        self.response, self.header = self.split_header(self.header)
        zmap(spin, LOAD, self.get_header)
        self.check_data_existence()

    def split_header(self, data):
        """

        """


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

    def check_data_existence(self):
        """

        """

        try:
            self.size = int(self.header['Content-Length'])
        except KeyError:
            pass

        # Assume there is a body size larger than 0.
        # Since we will call check_data_size anyway.
        xmap(self.spin, LOAD, self.get_data)
        self.check_data_size()


    def spawn_response(self):
        """

        """

        
        spawn(self.spin, HTTP_RESPONSE, self.response[0], self.response[1], 
                                    self.response[2], self.header, self.data)
        self.__init__(self.spin)

    def get_data(self, spin, data):
        """

        """

        self.data = self.data + data
        self.check_data_size()

    def check_data_size(self):
        """

        """
        if not len(self.data) >= self.size:
            return

        zmap(self.spin, LOAD, self.get_data)
        self.spawn_response()

class HttpCode(object):
    def __init__(self, spin):
        xmap(spin, HTTP_RESPONSE, self.spawn_method)

    def spawn_method(self, spin, version, code, reason, header, message):
        spawn(spin, code, version, reason, header, message)

def get(rsc, args={}, version='HTTP/1.1', header={}):
    args = '?%s' % urlencode(args) if args else ''
    data  = 'GET %s%s %s\r\n' % (rsc, args, version)

    for key, value in header.iteritems():
        data = data + '%s: %s\r\n' % (key, value)
    data = data + '\r\n'
    return data

def post_data(rsc, data={}, version='HTTP/1.1', header={}):
    params                   = urlencode(data)
    data                     = 'POST %s %s\r\n' % (rsc, version)
    header['Content-Type']   = 'application/x-www-form-urlencoded'
    header['Content-Length'] = len(params)

    for key, value in header.iteritems():
        data = data + '%s: %s\r\n' % (key, value)

    data = data + '\r\n'
    data = data + params
    return data

def auth(username, password):
    from base64 import encodestring
    base = encodestring('%s:%s' % (username, password))
    base = base.replace('\n', '')
    return "Basic %s" % base

def post_file():
    pass





