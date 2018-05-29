import redis


# r = redis.Redis(host='localhost', port=6379, db=1)


class Base(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=1)


class TestKeys(Base):
    """
    KEYS * 匹配数据库中所有 key 。
    KEYS h?llo 匹配 hello ， hallo 和 hxllo 等。
    KEYS h*llo 匹配 hllo 和 heeeeello 等。
    KEYS h[ae]llo 匹配 hello 和 hallo ，但不匹配 hillo 。
    特殊符号用 \ 隔开。
    """

    def test_keys(self):
        result = self.r.keys('*s*')
        print(result)
        return result

    def test_exists(self):
        result = self.r.exists('site')
        print(result)
        return result

    def test_move(self):
        """
        MOVE命令的作用是将当前数据库的 key 移动到给定的数据库 db
        MOVE key db
        """
        result1 = self.r.move('site', 2)
        print(result1)
        result2 = self.r.exists('site')
        print(result2)

    def test_rename(self):
        """RENAME命令可以将原有的 key 修改为新的key名称,
        RENAME key newkey
        """
        result = self.r.rename('rank', 'range')
        print(result)
        return result

    def test_sort(self):
        """SORT命令来实现排序,排序默认以数字作为对象
        SORT key [BY pattern] [LIMIT offset count]
        [GET pattern [GET pattern ...]] [ASC | DESC]
         [ALPHA] [STORE destination]
        """
        result = self.r.sort('myset2', desc=True)
        print(result)
        return result

    def test_dump(self):
        """DUMP命令来序列化给定key的值,
            DUMP key
        """
        result = self.r.dump('user2')
        print(result)
        result2 = self.r.dump('noexists')
        print(result2)

    def test_expire(self):
        """为key设置生存时间需要使用EXPIRE,
            EXPIRE key seconds
        """
        result = self.r.expire('user2', 540)
        print(result)

    def test_ttl(self):
        """TTL命令的作用是获取给定 key 剩余生存时间(TTL, time to live),
            TTL key
        """
        result = self.r.ttl('user2')
        print(result)


def main():
    keys_obj = TestKeys()
    # keys_obj.test_keys()
    # keys_obj.test_exists()
    # keys_obj.test_move()
    # keys_obj.test_rename()
    # keys_obj.test_sort()
    # keys_obj.test_dump()
    # keys_obj.test_expire()
    keys_obj.test_ttl()


if __name__ == '__main__':
    main()
