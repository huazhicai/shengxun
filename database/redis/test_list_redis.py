import redis


# r = redis.Redis(host='localhost', port=6379, db=2)


class TestList(object):
    """
    lpush/rpush  -- 从左/右插入数据
    lrange -- 获取指定长度的数据
    ltrim -- 截取一定长度的数据
    lpop/rpop --移除最左/右的元素并返回
    lpushx/rpushx -- key存在的时候才插入数据，不存在时不做任何处理
    """

    def __init__(self):
        self.r = redis.StrictRedis(host="localhost", port=6379, db=1)

    def test_push(self):
        "lpush/rpush  -- 从左/右插入数据 "
        t = ['Tony', 'Jhon', 'Amy', 'Jack']
        result = self.r.lpush('friends', *t)
        print(result)
        rest = self.r.lrange('friends', 0, -1)
        print(rest)

    def test_lset(self):
        "LSET可以将列表 key 下标为index的元素的值设置为 value"
        result = self.r.lset('friends', 0, 'Lucy')
        print(result)
        return result

    def test_lpop(self):
        "LPOP命令执行时会移除列表第一个元素"
        result = self.r.lpop('friends')
        print(result)
        rest = self.r.lrange('friends', 0, -1)
        print(rest)
        return result

    def test_lindex(self):
        "如果要获取列表元素，LINDEX"
        result = self.r.lindex('friends', 0)
        print(result)
        return result

    def test_linsert(self):
        "LINSERT可以将值 value 插入到列表 key 当中，位于值 pivot 之前或之后"
        result = self.r.linsert('friends', 'before', 'Jhon', 'Lucy')
        print(result)
        return result

    def test_lrem(self):
        "移除列表元素使用LREM"
        result = self.r.lrem('friends', 2, 'Lucy')
        print(result)
        return result

    def test_llen(self):
        "LLEN命令可以获取到列表的长度"
        result = self.r.llen('friends')
        print(result)
        return result

    def test_ltrim(self):
        "LTRIM可以对一个列表进行修剪"
        result = self.r.ltrim('friends', 1, 2)
        print(result)
        return result


def main():
    list_obj = TestList()
    # list_obj.test_push()
    # list_obj.test_lset()
    # list_obj.test_lpop()
    # list_obj.test_lindex()
    # list_obj.test_linsert()
    # list_obj.test_lrem()
    # list_obj.test_llen()
    list_obj.test_ltrim()


if __name__ == '__main__':
    main()
