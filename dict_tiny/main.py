#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import requests
from lxml import html
import re
import argparse

APP_DESC="""
tiny dictionary
"""


# def try_funtion():
#     if len(sys.argv) == 1:
#         sys.argv.append('--help')
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-q','--qua',type=int,default=0,help="")
#     parser.add_argument('-v','--verb', default=0,help="")
#     parser.add_argument('url',metavar='URL',nargs='+', help="")
#     args = parser.parse_args()
#     url = (args.url)[0]
#     print(len(args.verbose))
#     print(args.verbose[0])


def main(word="dictionary"):
    if len(sys.argv) > 1:
        word = sys.argv[1]
    request_url = "http://youdao.com/w/%s" % word
    result = requests.get(request_url).content
    #tree = html.etree
    selector = html.etree.HTML(result)
    content = selector.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li//text()')
    if len(content) >= 1:
        for each_result in content:
            print(each_result)
    else:
        print("None.")



if __name__ == "__main__":
    main()