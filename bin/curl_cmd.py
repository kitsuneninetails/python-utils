#!/usr/bin/env python
import argparse
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
    args = parser.parse_args()

    url = args.url
    operation = args.operation
    data = args.data
    mtype = args.media_type

    try:

        if operation == "get":
            ret = curl_utils.curl_get(url)
        elif operation == "put":
            ret = curl_utils.curl_put(url, json_data=data, media_type=mtype)
        elif operation == "post":
            ret = curl_utils.curl_post(url, json_data=data, media_type=mtype)
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
