from module.plugins.internal.Hoster import Hoster
from module.network.HTTPRequest import HTTPRequest
from module.network.CookieJar import CookieJar

import re


class FacebookVideoDownloader(Hoster):
    __name__ = 'FacebookVideoDownloader'
    __version__ = '0.1'
    __pattern__ = r'https://www.facebook.com/[^/]+/videos/([^/]+)'

    __config__ = [
        ('activated', 'bool', 'Activated', True)
    ]

    def setup(self):
        try:
            self.req.http.close()
        except Exception:
            pass

        self.req.http = BIGHTTPRequest(
            cookies=CookieJar(None),
            options=self.pyload.requestFactory.getOptions(),
            limit=5000000)

    def init(self):
        self.sd_url_pattern = r'sd_src:"(.+?)"'
        self.title_pattern = r'(?s)<title id="pageTitle">(.+?)</title>'

    def process(self, pyfile):
        html_source = self.load(pyfile.url, decode=False)

        sd_match = re.search(self.sd_url_pattern, html_source)
        if sd_match is None:
            self.fail(_('Video pattern not found'))
        sd_url = sd_match.group(1)

        title_match = re.search(self.title_pattern, html_source)
        if title_match is not None:
            pyfile.name = '%s.%s' % (title_match.group(1).decode('utf8'), 'mp4')

        self.download(sd_url)


# From youtube hoster because the html source is too big for the load method
class BIGHTTPRequest(HTTPRequest):
    """
    Overcome HTTPRequest's load() size limit to allow
    loading very big web pages by overrding HTTPRequest's write() function
    """

    # @TODO: Add 'limit' parameter to HTTPRequest in v0.4.10
    def __init__(self, cookies=None, options=None, limit=2000000):
        self.limit = limit
        HTTPRequest.__init__(self, cookies=cookies, options=options)

    def write(self, buf):
        """ writes response """
        if self.limit and self.rep.tell() > self.limit or self.abort:
            rep = self.getResponse()
            if self.abort:
                raise Abort()
            f = open("response.dump", "wb")
            f.write(rep)
            f.close()
            raise Exception("Loaded Url exceeded limit")

        self.rep.write(buf)

