# coding=utf-8

import requests
import jieba
import re
from urllib.parse import quote
from collections import Counter
from scrapy.selector import Selector
import operator
import json
from json import JSONDecodeError

countries_json_file = r'./all_countries.json'

with open(countries_json_file, 'r', encoding='utf-8') as f:
    countries = json.load(f)
countries = set(countries)


def is_chinese(text):
    '''
        判断是否为中文
    '''
    return True if re.findall('([\u4e00-\u9fa5]+)', text) else False


def get_wiki(keyword):
    '''
        通过关键词，获取wiki反馈的html信息
    '''
    # wiki_api = 'https://w.bk.wjbk.site/wiki/{}'
    wiki_api = 'https://baike.baidu.com/item/{}'
    headers = {
        'User-Agent': ua.random,
    }
    url = wiki_api.format(quote(keyword), 'utf-8')
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    return r.text


def get_tags_text_by_xpath(text, xpath):
    '''
        通过xpath获取标签的文本信息
    '''
    # html = HTML(text)
    # tags_text_list = html.xpath(xpath)
    selector = Selector(text=text).xpath(xpath)
    tags_text_list = selector.extract()
    return tags_text_list


def get_text_segment(text):
    '''
        结巴分词
    '''
    if isinstance(text, str):
        return list(jieba.cut_for_search(text))
    elif isinstance(text, list):
        segment_list = list()
        for w in text:
            segment_list.extend(jieba.cut_for_search(w))
        return segment_list


def get_list_most_element(list_all):
    '''
        返回一个列表中元素个数最多的那个元素
    '''
    # 进行统计
    counted_list = dict(Counter(list_all))
    # 进行排序
    sorted_list = sorted(counted_list.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_list[0][0]


def get_country_from_text(data):
    '''
        从字符串中提取出出现频率最高国家名称
    '''
    # 对字符串进行分词
    segment_list = get_text_segment(data)
    # 过滤非国家名称字符串
    segment_list = list(filter(lambda s: True if s in countries else False, segment_list))
    # 如果列表中含有国家名称则进行统计排序，返回频率最高的国家名称
    if segment_list:
        country = get_list_most_element(segment_list)
        return country
    return ''


def get_text_by_xpath(html, xpath):
    return Selector(text=html).xpath(xpath).extract()


def get_text_by_re(text, regex):
    return re.findall(regex, text)
    

def get_country_from_wiki_on_keyword(keyword):
    '''
        通过关键词，获取wiki反馈的html信息
    '''
    wiki_api = \
    '''
    https://w.bk.wjbk.site/w/api.php?
format=json&action=query&generator=search&gsrnamespace=0&gsrlimit=10&prop=pageimages|extracts&pilimit=max
&exintro&explaintext&exsentences=1&exlimit=max&origin=*&gsrsearch={}
    '''
    url = wiki_api.format(quote(keyword), 'utf-8')
    html = get_html(url)
    chinese_list = re.findall('[\u4e00-\u9fa5]+', html)
    country = get_country_from_text(chinese_list)
    if country:
        return country
    return ''


def get_country_from_baike_on_keyword(keyword):
    '''
        通过关键词，获取wiki反馈的html信息
    '''
    baike_api = 'https://baike.baidu.com/item/{}'
    xpath = '//div[re:test(@class, "lemma-summary|lemmaWgt-lemmaTitle|basic-info|poster")]//text()'
    
    url = baike_api.format(quote(keyword), 'utf-8')
    html = get_html(url)
    text_list = get_text_by_xpath(html, xpath)
    chinese_list = re.findall('[\u4e00-\u9fa5]+', ''.join(text_list))
    country = get_country_from_text(chinese_list)
    if country:
        return country
    return ''
