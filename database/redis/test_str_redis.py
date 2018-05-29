import redis


# r = redis.Redis(host='localhost', port=6379, db=0)


class TestString(object):
    """
    set -- 设置值
    get -- 获取值
    mset -- 设置多个键值对
    mget -- 获取多个键值对
    append -- 添加字符串
    del -- 删除
    incr/decr -- 增加/减少 1
    incrby/decrby -- 增加减少是定值
    """

    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=1)

    def test_set(self):
        result = self.r.set('user1', 'Amy')
        print(result)
        return result

    def test_get(self):
        result = self.r.get('user1')
        print(result)
        return result

    def test_mset(self):
        d = {
            'user2': 'Bob',
            'user3': 'Box'
        }
        result = self.r.mset(d)
        print(result)
        return result

    def test_mget(self):
        keys = ['user2', 'user3']
        result = self.r.mget(keys)
        print(result)
        return result

    def test_append(self):
        result = self.r.append('user1', 'Andy')
        print(result)
        return result

    def test_del(self):
        result = self.r.delete('user3')
        print(result)
        return result

    def test_setrange(self):
        result = self.r.setrange('user1', 7, 'hua')
        print(result)
        return result

    def test_strlen(self):
        result = self.r.strlen('user1')
        print(result)
        return result


def main():
    str_obj = TestString()
    # str_obj.test_set()
    # str_obj.test_get()
    # str_obj.test_mset()
    # str_obj.test_mget()
    # str_obj.test_append()
    # str_obj.test_del()
    # str_obj.test_setrange()
    str_obj.test_strlen()


if __name__ == '__main__':
    main()
