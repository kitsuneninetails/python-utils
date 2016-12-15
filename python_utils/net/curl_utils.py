import json
import pycurl
from StringIO import StringIO


def _curl_do_cmd(url, json_data=None, filename=None,
                 media_type='application/json', custom_request=None):
    cbuffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, cbuffer)

    if json_data:
        c.setopt(c.HTTPHEADER, ["Content-Type: " + media_type])
        c.setopt(c.POSTFIELDS, json.dumps(json_data))
    if filename:
        c.setopt(c.HTTPPOST, [('fileupload', (c.FORM_FILE, file))])
    if custom_request:
        c.setopt(pycurl.CUSTOMREQUEST, custom_request)
    c.perform()
    c.close()
    body = cbuffer.getvalue()
    return body


def curl_get(url):
    return _curl_do_cmd(
        url, json_data=None, filename=None)


def curl_post(url, json_data, filename=None,
              media_type='application/json'):
    return _curl_do_cmd(
        url, json_data=json_data, filename=filename, media_type=media_type)


def curl_put(url, json_data=None, filename=None,
             media_type='application/json'):
    return _curl_do_cmd(
        url, json_data=json_data, filename=filename, media_type=media_type,
        custom_request="PUT")


def curl_delete(url):
    return _curl_do_cmd(
        url, json_data=None, filename=None, custom_request="DELETE")
