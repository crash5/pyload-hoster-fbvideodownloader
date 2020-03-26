from module.plugins.internal.Hoster import Hoster

import re


class FacebookVideoDownloader(Hoster):
    __name__ = 'FacebookVideoDownloader'
    __version__ = '0.1'
    __pattern__ = r'https://www.facebook.com/[^/]+/videos/([^/]+)'

    __config__ = [
        ('activated', 'bool', 'Activated', True)
    ]

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

