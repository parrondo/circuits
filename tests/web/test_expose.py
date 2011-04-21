try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError

from circuits.web import expose, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

    @expose("+test")
    def test(self):
        return "test"

    @expose("foo+bar", "foo_bar")
    def foobar(self):
        return "foobar"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

    f = urlopen("%s/+test" % webapp.server.base)
    s = f.read()
    assert s == b"test"

    f = urlopen("%s/foo+bar" % webapp.server.base)
    s = f.read()
    assert s == b"foobar"

    f = urlopen("%s/foo_bar" % webapp.server.base)
    s = f.read()
    assert s == b"foobar"
