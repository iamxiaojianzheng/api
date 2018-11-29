# coding=utf-8
import random
import hashlib
import http.client
import urllib.parse
import json
import os
from json import JSONDecodeError


class YoudaoTranslateAI:

    def __init__(self, appKey, secretKey):
        self.appKey = appKey
        self.secretKey = secretKey
        self.url = '/api'
        self.salt = self.get_salt()

    def get_salt(self):
        return str(random.randint(1, 65536))

    def get_sign(self, text):
        sign = self.appKey + text + self.salt + self.secretKey
        m1 = hashlib.md5()
        m1.update(sign.encode('utf-8'))
        sign = m1.hexdigest()
        return sign

    def quote_text(self, text):
        return urllib.parse.quote(text)

    def get_api_url(self, text, fromLang='auto', toLang='zh-CHS'):
        api_url = '{url}?appKey={appKey}&q={quote_text}&from={fromLang}&to={toLang}&salt={salt}&sign={sign}'.format(
            url=self.url,
            appKey=self.appKey,
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
            httpClient = http.client.HTTPConnection('openapi.youdao.com')
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
                if json_text.get('errorCode') == '0':
                    return json_text.get('translation')[0]
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
    app_key = '应用ID'
    secret_key = '应用密钥'
    youdao = Youdao(app_key, secret_key)
    # result = youdao.translate_word('apple')
    youdao.translate_words_from_file('文件路径')
    # print(result)
