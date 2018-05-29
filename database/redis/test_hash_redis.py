import redis


# r = redis.Redis(host='localhost', port=6379, db=1)
# Redis的哈希值是字符串字段和字符串值之间的映射。

class Base(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=1)


class TestHash(Base):
    def test_hset(self):
        """HSET命令来将哈希表 key 中的域 field 的值设为 value,
            HSET key field value
        """
        result1 = self.r.hset('site', 'huizhi', 'huizhi.com')
        print(result1)
        return result1

    def test_hmset(self):
        """MHSET命令来将哈希表 key 中的域 field 的值设为 value,
            HMSET key field value [field value ...]
        """
        h = {'google': 'google.com', 'baidu': 'baidu.com'}
        # 不要用*h
        result = self.r.hmset('site', h)
        print(result)
        return result

    def test_hget(self):
        """HGET命令获取哈希表 key 中的域 field 的值 value,
            HGET key field
        """
        result1 = self.r.hget('site', 'huizhi')
        print(result1)
        return result1

    def test_hmget(self):
        """MHGET命令来将哈希表 key 中的域 field 的值设为 value,
            HMSET key field [field...]
        """
        result = self.r.hmget('site', 'huizhi', 'google')
        print(result)
        return result

    def test_hgetall(self):
        """HGETALL key, 获取所有的键值对
        """
        result = self.r.hgetall('site')
        print(result)
        return result

    def test_hkeys(self):
        """HKEYS来获取哈希表 key 中的所有域,
            HKEYS key
        """
        result = self.r.hkeys('site')
        print(result)
        return result

    def test_hexists(self):
        """ key 中是否存在某个 field ,
            HEXISTS key field
        """
        result = self.r.hexists('site', 'google')
        print(result)
        return result

    def test_hlen(self):
        """HLEN命令将返回哈希表 key 中域的数量,
            HLEN key
        """
        result = self.r.hlen('site')
        print(result)
        return result

    def test_hdel(self):
        """删除哈希表 key 中的一个或多个指定域,
            HDEL key field [field ...]
        """
        result = self.r.hdel('site', 'google', 'huizhi')
        print(result)
        return result


def main():
    hash_obj = TestHash()
    # hash_obj.test_hset()
    hash_obj.test_hmset()
    # hash_obj.test_hget()
    # hash_obj.test_hmget()
    # hash_obj.test_hgetall()
    # hash_obj.test_hkeys()
    # hash_obj.test_hexists()
    # hash_obj.test_hlen()
    # hash_obj.test_hdel()


if __name__ == '__main__':
    main()
