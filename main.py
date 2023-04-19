#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author YWLBTWTK
# @date 2023/4/19
import re
import httpx
from bs4 import BeautifulSoup

headers = {
    'authority': 'sukebei.nyaa.si',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://sukebei.nyaa.si/',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}
http_client = httpx.Client(headers=headers, timeout=None, verify=False)


def to_bytes(size_str):
    units = {'B': 1, 'KiB': 1024, 'MiB': 1024 ** 2, 'GiB': 1024 ** 3, 'TiB': 1024 ** 4}
    size_regex = r'^(\d+(\.\d+)?)\s*(B|KiB|MiB|GiB|TiB)$'
    match = re.match(size_regex, size_str)

    if match:
        size, _, unit = match.groups()
        return int(float(size) * units[unit])
    else:
        raise ValueError('Invalid file size string: {}'.format(size_str))


def format_file_size(sizes):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    unit_idx = 0
    total_bytes = sum(to_bytes(s) for s in sizes)

    while total_bytes > 1024 and unit_idx < len(units):
        total_bytes /= 1024
        unit_idx += 1

    if total_bytes == 0:
        return '0 B'

    return '{:.2f} {}'.format(total_bytes, units[unit_idx])


def page(q: str, p: int = 1):
    page_params = {
        'f': '0',
        'c': '0_0',
        'q': q,
        'p': str(p),
    }
    resp = http_client.get('https://sukebei.nyaa.si/', params=page_params)
    soup = BeautifulSoup(resp, 'lxml')
    soup = soup.tbody
    soup_group = soup.select('tr')
    sum_list = []
    size_list = []
    magnet_list = []
    for i in soup_group:
        title = i.select('td:nth-child(2) > a')[0].text
        size = i.select('td:nth-child(4)')[0].text
        size_list.append(size)
        magnet = BeautifulSoup(str(i.select('td:nth-child(3) > a:last-child')[0]), 'lxml').a['href']
        magnet_list.append(magnet)
        sum_list.append([title, size, magnet])
    return [sum_list, size_list, magnet_list]


def main(q: str):
    params = {
        'f': '0',
        'c': '0_0',
        'q': q,
    }
    resp = http_client.get('https://sukebei.nyaa.si/', params=params)
    soup = BeautifulSoup(resp, 'lxml')
    page_len = (len(soup.select('body > div > div.center > ul > li')))
    if page_len == 0:
        print('未找到结果')
    else:
        sum_list = []
        size_list = []
        magnet_list = []
        for j in range(1, page_len - 1):
            r = page(q, j)
            sum_list.extend(r[0])
            size_list.extend(r[1])
            magnet_list.extend(r[2])
        print(f'搜索“{q}”共有{len(magnet_list)}个链接，合计{format_file_size(size_list)}')
        with open(f'{q}_out.txt', 'a') as f:
            for k in magnet_list:
                f.write(k)
                f.write('\n')
        print(f'磁力链接已保存至{q}_out.txt')


if __name__ == '__main__':
    main(input('搜索内容：'))
