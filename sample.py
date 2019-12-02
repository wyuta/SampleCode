#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import requests
import re
from time import sleep
from bs4 import BeautifulSoup

"""
This source is sample programe to crawl and pickup words from Amazon.com.
If there are target words on the Amazon.com site, can pickup.
"""


SENTENCE = "Virtue signalling is society's version of Proof of Stake"

MAX_CLAWLING_PAGE = 100

URL_BASE   = 'https://www.amazon.com/gp/bestsellers/{category}?pg={page}'
CATEGORIES = ['wireless', 'pc', 'fashion', 'sporting-goods']


words   = SENTENCE.split()
results = ['None' for word in words]


def main():
    print('Start ********************')

    crawling()

    print('')
    print('End ********************')

    print('')
    print('[Search]: ' + SENTENCE)
    print('[Result]: ' + ' '.join(results))


def crawling():
    for category in CATEGORIES:
        print('')
        print('[Category]: ' + category + ' -------------------------------')

        for i in range(MAX_CLAWLING_PAGE):
            url = URL_BASE.format(category=category, page=(i + 1))

            if search(url):
                continue
            else:
                break


def search(url):
    while True:
        sleep(1)

        print(url)

        response = requests.get(url)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            print('200 ok.')
            scraping(response.text)
            break

        elif response.status_code == 503:
            print('503 retry.')
            continue

        elif response.status_code == 404:
            print('404 end.')
            break

        else:
            print('other end.')
            break

    if response.status_code == 404:
        return False
    else:
        return True


def scraping(text):
    soup = BeautifulSoup(text, 'html.parser')
    divs = soup.find_all('div', class_='p13n-sc-truncate')

    for div in divs:
        str = div.get_text()

        for index, word in enumerate(words):
            if word and word in str:
                m = re.search(word, str)

                words[index] = None
                results[index] = m.group()

                print('[Hit]: ' + word)
                """
                print(word)
                print(words)
                print(results)
                print('---------------')
                """


if __name__ == '__main__':
    main()
