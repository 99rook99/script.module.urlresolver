'''
tunepk urlresolver plugin
Copyright (C) 2013 icharania
updated Copyright (C) 2017 Gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re,json
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class TunePkResolver(UrlResolver):
    name = "tune.pk"
    domains = ["tune.pk", "tune.video"]
    pattern = '(?://|\.)(tune\.(?:video|pk))/(?:player|video|play)/(?:[\w\.\?]+=)?(\d+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        if 'Not Found' in html:
            raise ResolverError('File Removed')

        web_url = re.findall("requestURL = '(.*?)'",html)[0]
        response = self.net.http_GET(web_url, headers=headers)
        jdata = json.loads(response.content)
        vids = jdata['data']['details']['player']['sources']
        sources=[]
        for vid in vids:
            sources.append((vid['label'],vid['file']))
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://betaembed.tune.pk/play/{media_id}')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="Video Quality" id="%s_quality" type="enum" values="High|Medium|Low" default="0" />' % (cls.__name__))
        return xml
