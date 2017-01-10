#!/usr/bin/env python
import argparse
import base64
from python_utils.net import curl_utils


def curl_cmd():
    # Parse args
    parser = argparse.ArgumentParser(
        description='CURL Utils functions',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-u', '--url', action='store', default=None,
                        help='URL', required=True)
    parser.add_argument('-o', '--operation', action='store', default='get',
                        help='Operation', required=False)
    parser.add_argument('-d', '--data', action='store', default=None,
                        help='Data to PUT/POST', required=False)
    parser.add_argument('-m', '--media-type', action='store',
                        default='application/json',
                        help='Media type to use', required=False)
    parser.add_argument('-a', '--auth-url', action='store',
                        default=None,
                        help='URL to use to get auth token', required=False)
    parser.add_argument('-n', '--auth-username', action='store',
                        default=None,
                        help='Auth username', required=False)
    parser.add_argument('-p', '--auth-pass', action='store',
                        default=None,
                        help='Auth password', required=False)
    parser.add_argument('--extra-headers', action='store',
                        default=None,
                        help='Extra Headers as a comma-delimited key=value '
                             'list (no spaces)',
                        required=False)
    parser.add_argument('--extra-auth-headers', action='store',
                        default=None,
                        help='Extra Headers for authorization as a '
                             'comma-delimited key=value list (no spaces)',
                        required=False)
    args = parser.parse_args()

    url = args.url
    operation = args.operation
    data = args.data
    mtype = args.media_type
    auth_url = args.auth_url
    auth_user = args.auth_username
    auth_pass = args.auth_pass
    extra_headers = args.extra_headers
    extra_auth_headers = args.extra_auth_headers
    headers = {}

    try:
        token = None

        if auth_url:
            auth = ('' +
                    (auth_user if auth_user else '') +
                    ((':' + auth_pass) if auth_pass else ''))

            auth_headers = {'Authorization': 'Basic ' + base64.b64encode(auth)}
            if extra_auth_headers:
                for h in [n.split('=') for n in extra_auth_headers.split(',')]:
                    auth_headers.update(dict((tuple(h),)))

            token_ret = curl_utils.curl_post(auth_url, json_data={},
                                             headers=auth_headers)

            headers['X-Auth-Token'] = (
                curl_utils.curl_get_data_as_dict(token_ret)['key'])

        if extra_headers:
            for h in [n.split('=') for n in extra_headers.split(',')]:
                headers.update(dict((tuple(h),)))

        if operation == "get":
            ret = curl_utils.curl_get(url, headers=headers)
        elif operation == "put":
            ret = curl_utils.curl_put(url, json_data=data, headers=headers,
                                      media_type=mtype)
        elif operation == "post":
            ret = curl_utils.curl_post(url, json_data=data, headers=headers,
                                       media_type=mtype)
        elif operation == "delete":
            ret = curl_utils.curl_delete(url)
        else:
            raise Exception("Undefined operation: " + operation)

    except Exception as e:
        print("Error running CURL command: " + str(e))
        return -1

    print(ret)


if __name__ == "__main__":
    curl_cmd()
