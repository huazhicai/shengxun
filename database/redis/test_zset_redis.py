import redis


# r = redis.Redis(host='localhost', port=6379, db=1)

class Base(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=1)


class TestZset(Base):
    def test_zadd(self):
        """ZADD命令将一个或多个 member 元素及其 score 值加入到有序集 key 当中
        redis.zadd('my-key', 'name1', 1.1, 'name2', 2.2, name3=3.3, name4=4.4)"""
        z = ['google.com', 1, 'baidu.com', 2, 'huizhi.com', 3]
        result = self.r.zadd('rank', *z)
        print(result)
        rest = self.r.zrange('rank', 0, -1, withscores=True)
        print(rest)

    def test_zrem(self):
        "ZREM命令可以移除指定成员"
        result = self.r.zrem('rank', 'baidu.com')
        print(result)
        rest = self.r.zrange('rank', 0, -1, withscores=True)
        print(rest)

    def test_zscore(self):
        "ZSCORE命令来获取成员评分, ZSCORE key member"
        result = self.r.zscore('rank', 'google.com')
        print(result)
        return result

    def test_zcard(self):
        "ZCARD查看集合成员的数量, ZCARD key"
        result = self.r.zcard('rank')
        print(result)
        return result

    def test_zcount(self):
        "ZCOUNT命令可以设定评分的最小和最大值, ZCOUNT key min max"
        result = self.r.zcount('rank', 1, 2)
        print(result)
        return result

    def test_zrank(self):
        "ZRANK依据 评分（score） 值递增(从小到大)顺序排列, ZRANK key member"
        result = self.r.zrank('rank', 'huizhi.com')  # 获取排名
        print(result)
        return result

    def test_zincrby(self):
        "ZINCRBY命令可以为给定的成员评分值加上增量, ZINCRBY key increment member"
        result = self.r.zincrby('rank', 'huizhi.com', 3)  # 获取排名
        print(result)
        return result


def main():
    zset_obj = TestZset()
    # zset_obj.test_zadd()
    # zset_obj.test_zrem()
    # zset_obj.test_zscore()
    # zset_obj.test_zcard()
    # zset_obj.test_zcount()
    # zset_obj.test_zrank()
    zset_obj.test_zincrby()


if __name__ == '__main__':
    main()
