# -*- coding: utf-8 -*-
import json
from scrapy import Spider,Request
from zhihuuser.items import UserItem
from scrapy_redis.spiders import RedisSpider


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # 初始用户关注的人的URL
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    # 初始用户粉丝的URL
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'


    start_user = 'tianshansoft'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 构造初始请求
    def start_requests(self):

        # 获取用户的信息URL
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query),callback= self.parse_user)

        # 获取用户follows的url
        yield  Request(self.follows_url.format(user = self.start_user,include = self.follows_query,offset = 0,limit = 20),callback=self.parse_follows)

        # 获取用户粉丝，也就是关注他的人的URL
        yield  Request(self.followers_url.format(user = self.start_user,include = self.followers_query,offset = 0,limit = 20),callback=self.parse_followers)

    # 解析用户自身的信息
    def parse_user(self,response):
        # json.loads 把json字符串转换成Python的字符串对象
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)

        yield item
        yield Request(self.follows_url.format(user = result.get('url_token'),include = self.follows_query,offset = 0,limit = 20),callback=self.parse_follows)
        yield Request(self.followers_url.format(user = result.get('url_token'),include = self.followers_query,offset = 0,limit = 20),callback=self.parse_followers)

    # 解析用户的关注者的信息,处理关注列表
    def parse_follows(self, response):

        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),callback= self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page , callback=self.parse_follows)

    # 解析用户的粉丝的信息,处理关注列表
    def parse_followers(self, response):

        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),callback= self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page , callback=self.parse_followers)
