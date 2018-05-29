import redis


# r = redis.Redis(host='localhost', port=6379, db=0)

class Base(object):
    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=1)


class TestSet(Base):
    """
    sadd/srem -- 添加/删除元素
    sismember --判断是否为set的一个元素
    smembers --返回该集合的所有成员
    sdiff -- 返回一个集合与其它集合的差异
    sinter  -- 返回几个集合的交集
    sunion -- 返回几个集合的并集
    """

    def test_sadd(self):
        "SADD命令可以将一个或多个 member 元素加入到集合 key 当中"
        z = ['Tom', 'Andy', 'Lucy']
        result = self.r.sadd('room', *z)
        print(result)
        rest = self.r.smembers('room')
        print(rest)
        return result

    def test_spop(self):
        "随机取出集合中某个元素spop"
        result = self.r.spop('room')
        print(result)
        rest = self.r.smembers('room')
        print(rest)
        return result

    def test_scard(self):
        "查看集合中元素的数量SDIFF"
        result = self.r.scard('room')
        print(result)
        return result

    def test_sset(self):
        """取得集合中两个集合的差集SDIFF,
        取得集合中两个集合的交集SINTER,
        取得集合中两个集合的并集SUNION
        """
        rest1 = self.r.smembers('myset1')
        rest2 = self.r.smembers('myset2')
        print(rest1)
        print(rest2)
        result_diff = self.r.sdiff('myset1', 'myset2')
        result_inter = self.r.sinter('myset1', 'myset2')
        result_union = self.r.sunion('myset1', 'myset2')
        print(result_diff)
        print(result_inter)
        print(result_union)

    def test_sismember(self):
        "判断集合是否包含某个元素SISMEMBER"
        result1 = self.r.sismember('room', 'Lucy')
        print(result1)
        result2 = self.r.sismember('room', 'Jack')
        print(result2)

    def test_smove(self):
        "smove将 member 元素从 source 集合移动到 destination 集合"
        result = self.r.smove('myset1', 'myset2', 1)
        print(result)
        return result

    def test_srem(self):
        "SREM可以将元素从集合中移除"
        result = self.r.srem('myset2', 1)
        print(result)
        return result


def main():
    set_obj = TestSet()
    # set_obj.test_sadd()
    # set_obj.test_spop()
    # set_obj.test_scard()
    # set_obj.test_sdiff()
    # set_obj.test_sset()
    # set_obj.test_sismember()
    # set_obj.test_smove()
    set_obj.test_srem()

if __name__ == '__main__':
    main()
