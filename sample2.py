#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
import datetime
import requests
import re
from bs4 import BeautifulSoup


# Result
# https://github.com/wyuta/SampleCode/blob/master/sample2_result.txt


SENTENCE = "Virtue signalling is society's version of Proof of Stake"


BASE_URL   = 'http://www.amazon.com/'
BASE_URL_S = 'https://www.amazon.com/'

# Any URLs
CRAWL_TOP_URLS = [
    'https://www.amazon.com/s?&ref=nb_sb_noss&rh=n%3A11057901&url=node%3D11057901',
    'https://www.amazon.com/s?&ref=nb_sb_noss&rh=n%3A5486449011&url=node%3D5486449011',
    'https://www.amazon.com/s?&ref=nb_sb_noss&rh=n%3A13820&url=node%3D13820',
    'https://www.amazon.com/s/ref=nb_sb_noss?url=node%3D9681286011',
    'https://www.amazon.com/s?&ref=nb_sb_noss&rh=n%3A271632011&url=node%3D271632011'
]

WAIT_TIME = 1

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agetn': ''
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36 Sleipnir/4.1.4',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.63 Safari/537.36'
]


user_agent_index = -1
request_count    = 0
candidate_links  = []

search_words   = SENTENCE.split()
pickuped_words = [None for word in search_words]


def main():
    print('START ({time})'.format(time=datetime.datetime.now()))
    print('---------------------------------')
    print('[Sentence]: {sentence}'.format(sentence=SENTENCE))

    try:
        for url in CRAWL_TOP_URLS:
            _crawling(url)

    except KeyboardInterrupt:
        pass

    if None in pickuped_words:
        for index, r in enumerate(pickuped_words):
            if r is None:
                pickuped_words[index] = 'None'

    print('---------------------------------')
    print('END ({time})'.format(time=datetime.datetime.now()))
    print('[Sentence]: {sentence}'.format(sentence=SENTENCE))
    print('[Pickuped]: {pickuped_words}'.format(pickuped_words=' '.join(pickuped_words)))


def _crawling(url):
    global request_count

    is_clawl_top = True

    while True:
        if _is_complete():
            break

        soup, status_code = _request_roop(url)

        if status_code == 200:

            if is_clawl_top:
                is_clawl_top = False
            else:
                request_count = request_count + 1

                print('[{count}]: {url}'.format(count=request_count, url=url))
                _scraping(soup, url)

                if _is_complete():
                    break

            next_page_url = _get_next_page_url(soup)
            if next_page_url:
                url = next_page_url
                continue

        print('End paging')
        break


def _scraping(soup, url):
    # Exclude script and style
    for script in soup(['script', 'style']):
        script.decompose()

    serach_results = soup.find(id='search-results')
    if serach_results is None:
        serach_results = soup.find(class_='s-search-results')
    if serach_results is None:
        return

    title_list = []
    h2s = serach_results.find_all('h2')
    for h2 in h2s:
        title = h2.get_text()
        if title:
            title_list.append(title.replace('\n', ' '))

    if len(title_list) > 0:
        join_title = ' '.join(title_list)
        words = join_title.split(' ')

        for index, search_word in enumerate(search_words):
            if search_word:

                m = None
                for word in words:
                    m = re.search('^' + search_word + '$', word, re.IGNORECASE)
                    if m:
                        break

                if m:
                    pickuped_words[index] = m.group()
                    pickuped_words[index] = ''.join([pickuped_words[index][i].upper() if w.isupper() else pickuped_words[index][i].lower() for i, w in enumerate(search_words[index])])
                    search_words[index] = None

                    print()
                    print('[URL]: {url}'.format(url=url))
                    print('[Hit]: {word}'.format(word=search_word))
                    print('[Original]: {original}'.format(original=m.group()))
                    print('[Date]: {time}'.format(time=datetime.datetime.now()))
                    print('[Search]: ', end='')
                    print(search_words)
                    print('[Pickuped]: ', end='')
                    print(pickuped_words)
                    print()

                    if _is_complete():
                        break


def _get_next_page_url(soup):
      url = None

      # Pager 1
      next_link1 = soup.find(id='pagnNextLink')
      if next_link1:
          href = next_link1.get('href')
          if href:
              url = _get_url(href)

      # Pager 2
      if url is None:
          next_link2 = soup.find(class_='a-last')
          if next_link2:
              a = next_link2.find('a')
              if a:
                  href = a.get('href')
                  if href:
                      url = _get_url(href)
      return url


def _is_complete():
    return not (None in pickuped_words)


def _get_url(link):
    if link.startswith(BASE_URL) or link.startswith(BASE_URL_S):
        return link
    else:
        return BASE_URL + link.lstrip("/")


def _request_roop(url):
    soup = None
    status_code = 0

    while True:
        time.sleep(WAIT_TIME)

        response = requests.get(url, headers=_get_header())
        response.encoding = response.apparent_encoding
        status_code = response.status_code

        if status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')

            if soup.title.string == 'Robot Check':
                print(soup.title.string)
                continue
            else:
                break

        elif status_code == 503:
            print(status_code)
            continue

        else:
            print(url)
            print(status_code)
            break

    return soup, status_code


def _get_header():
    headers = HEADERS
    headers['user-agent'] = _get_user_agent()
    return headers


def _get_user_agent():
    global user_agent_index

    user_agent_index = user_agent_index + 1
    if user_agent_index > len(USER_AGENTS) - 1:
        user_agent_index = 0

    return USER_AGENTS[user_agent_index]


if __name__ == '__main__':
    main()
