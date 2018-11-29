# coding=utf-8
import random
import hashlib
import http.client
import urllib.parse
import json
import os
from json import JSONDecodeError


class BaiduTranslateAI:

    def __init__(self, appid, secretKey):
        self.appid = appid
        self.secretKey = secretKey
        self.url = '/api/trans/vip/translate'
        self.salt = self.get_salt()

    def get_salt(self):
        return str(random.randint(32768, 65536))

    def get_sign(self, text):
        sign = self.appid + text + self.salt + self.secretKey
        m = hashlib.md5()
        m.update(sign.encode('utf-8'))
        sign = m.hexdigest()
        return sign

    def quote_text(self, text):
        return urllib.parse.quote(text)

    def get_api_url(self, text, fromLang='auto', toLang='zh'):
        api_url = '{url}?appid={appid}&q={quote_text}&from={fromLang}&to={toLang}&salt={salt}&sign={sign}'.format(
            url=self.url,
            appid=self.appid,
            quote_text=self.quote_text(text),
            fromLang=fromLang,
            toLang=toLang,
            salt=self.salt,
            sign=self.get_sign(text),
        )
        return api_url

    def get_html(self, word):
        url = self.get_api_url(text=word)
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', url)
            response = httpClient.getresponse()
            html = response.read().decode('utf-8')
            return html
        except Exception as e:
            return ''

    def parse_html_to_json(self, html):
        try:
            json_text = json.loads(html)
            return json_text
        except JSONDecodeError as e:
            return ''

    def translate_word(self, word):
        if not word:
            return ''

        html = self.get_html(word)
        if html:
            json_text = self.parse_html_to_json(html)
            if isinstance(json_text, dict):
                if not json_text.get('error_code') or json_text.get('error_code') == '52000':
                    return json_text.get('trans_result')[0]['dst']
                return html
        return ''

    def translate_words_from_file(self, filepath):
        if not os.path.isfile(filepath):
            return 'file not find.'
        dir, file = os.path.split(filepath)
        translated_file = '{}/{}.txt'.format(dir, 'translated')

        with open(filepath, 'r', encoding='utf-8') as f:
            need_translate_word_list = f.read().splitlines()

        with open(translated_file, 'w', encoding='utf-8') as f:
            for word in need_translate_word_list:
                translated_word = self.translate_word(word)
                format_write_str = '{}\n'.format(translated_word)
                f.write(format_write_str)
                f.flush()
                print(format_write_str, end='\r')


if __name__ == '__main__':
    app_key = '你的APP ID'
    secret_key = '你的密钥'
    baidu = BaiduTranslateAI(app_key, secret_key)
    result = baidu.translate_word('apple')
    # youdao.translate_words_from_file('文件路径')
    print(result)

'''
auto	自动检测
zh	    中文
en	    英语
yue	    粤语
wyw	    文言文
jp	    日语
kor	    韩语
fra	    法语
spa	    西班牙语
th	    泰语
ara	    阿拉伯语
ru	    俄语
pt	    葡萄牙语
de	    德语
it	    意大利语
el	    希腊语
nl	    荷兰语
pl	    波兰语
bul	    保加利亚语
est	    爱沙尼亚语
dan	    丹麦语
fin	    芬兰语
cs	    捷克语
rom	    罗马尼亚语
slo	    斯洛文尼亚语
swe	    瑞典语
hu	    匈牙利语
cht	    繁体中文
vie	    越南语
'''
