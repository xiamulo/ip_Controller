import redis
from hashlib import md5
class redis_util(object):
    def __init__(self,type="",db=0):
        self.pool = redis.ConnectionPool(host='49.235.94.229', port=6379, decode_responses=True,password="a13479860462A",max_connections=100000)
        self.r = redis.Redis(connection_pool=self.pool)
        self.type=type

    def insert(self,key):
        self.r.sadd(self.type,key)
    def set(self,key):
        self.r.set(self.type,key,ex=3600*24)
    def get(self,key):
        ret = self.r.get(self.type)
        return ret
    def is_exit(self,key):
        ret = self.r.sismember(self.type, key)
        return ret
    def get_tuple(self,):
        ret = self.r.sscan(self.type)
        return ret
    def insert_list(self,key):
        ret = self.r.lpush(self.type, key)
        return ret
    def ex(self,name,time):
        ret = self.r.expire(name, time)
        return ret
    def list_iter(self,name):
        """
        自定义redis列表增量迭代
        :param name: redis中的name，即：迭代name对应的列表
        :return: yield 返回 列表元素
        """
        list_count = self.r.llen(name)
        for index in range(list_count):
            yield self.r.lindex(name, index)

    def llen(self,key):
        ret = self.r.llen(key)
        return ret

    def lindex(self,key,index):
        ret = self.r.lindex(key,index)
        return ret
    def get_all(self, ):
        ret = self.r.smembers(self.type)
        return ret
class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    def __init__(self,host='49.235.94.229', port=6379, decode_responses=True,password="a13479860462A", db=1, blockNum=1, key='question'):
        """
        :param host: the host of Redis
        :param port: the port of Redis
        :param db: witch db in Redis
        :param blockNum: one blockNum for about 90,000,000; if you have more strings for filtering, increase it.
        :param key: the key's name in Redis
        """
        self.Pool = redis.ConnectionPool(host=host, port=port, max_connections=100)
        self.server = redis.Redis(connection_pool=self.Pool,decode_responses=True)
        self.bit_size = 1 << 31  # Redis的String类型最大容量为512M，现使用256M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = key
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    def isContains(self, str_input):
        if not str_input:
            return False
        m5 = md5()
        m5.update(str_input.encode('utf-8'))
        str_input = m5.hexdigest()
        ret = True
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def insert(self, str_input):
        m5 = md5()
        m5.update(str_input.encode('utf-8'))
        str_input = m5.hexdigest()
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)


if __name__ == '__main__':
    bf = BloomFilter()
    if bf.isContains('http://www.baidu.com'):  # 判断字符串是否存在
        print('exists!')
    else:
        print('not exists!')
        bf.insert('http://www.baidu.com')
""" 第一次运行时会显示 not exists!，之后再运行会显示 exists! """


