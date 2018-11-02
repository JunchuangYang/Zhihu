### 使用scrapy-redis对知乎用户信息进行分布式爬取

**首先已经确保安装scrapy-redis，如果没有，使用 pip install scrapy-redis** 

scrapy-redis的github上的地址：https://github.com/rmax/scrapy-redis

**修改settings.py配置文件**

在原配置文件中添加

```python
ITEM_PIPELINES = {
    #通过RedisPipeline将item写入key为 spider.name: items的redis的list中，供后面的分布式处理item。
    'scrapy_redis.pipelines.RedisPipeline': 301
}


# 使用scarpy-redis中的调度器，在redis里面分配请求。
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

#scrapy_redis.duperfilter.REPDupeFilter的去重组件，在redis数据库里做去重。
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"


# 远程主机上Redis数据库的配置，有密码的话是这样配置的REDIS_URL = 'redis://user:pass@hostname:9001'
REDIS_URL = 'redis://root@192.168.142.131:6379'

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

```

将上面的代码加入到settings.py中之后，在我们本机上（也就是slave从机）的爬虫项目就配置好了

**远程主机（Master）我使用的是虚拟机中的Ubuntu，同样，在主机上需要安装python，redis服务器**

将redis服务器开启之后，我们使用ifconfig查看虚拟机的ip地址，这个地址就是我们要在从机上连接的redis服务器的地址

然后在从机上使用RedisDesktopManager查看能否连接成功

![](https://i.imgur.com/XKhA9hV.png)

这里在连接上可能会出现一些问题，具体参见https://blog.csdn.net/GLQGLQ/article/details/54176503

我是根据上面的配置以后还不成功，又使用命令** sudo ufw disable **将防火墙关闭，然后重启ubuntu之后连接成功

接着在从机上使用 **scrapy crawl zhihu**运行爬虫，会看见项目正常启动

然后在RedisDesktopManager可以看到虚拟机中的redis数据库中有如下数据：

![](https://i.imgur.com/A91Urxn.png)

我们的第一个从机就配置成功了，如果想要多台主机联合爬取，在另一个从机上拷贝一样的代码，运行之后就能实现分布式爬取。

