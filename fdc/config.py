# -*- coding: utf-8 -*-
import sqlite3
import StringIO
import sys, time

reload(sys)
sys.setdefaultencoding("utf-8")


class Memsql(object):
    """内存操作类"""

    def __init__(self, arg):
        super(Memsql, self).__init__()
        self.arg = arg

    def memcon(self):
        con = sqlite3.connect(":memory:")
        cur = con.cursor()
        return cur

    def meminsert(self):
        cur = self.memcon()
        cur.execute('insert into quotes(code,high,open,low,close,amount,volume) values(?,?,?,?,?,?,?)',
                    ('600036', 12.0, 11.8, 11.7, 11.9, 999999, 8999))

    def memsqlall(self):
        # 生成内存数据库脚本
        str_buffer = StringIO.StringIO()
        # con.itrdump() dump all sqls
        for line in con.iterdump():
            str_buffer.write('%s\n' % line)

        # 关闭内存数据库
        cur.close()

    def memtodb():
        # 打开文件数据库
        con_file = sqlite3.connect('quotes.db3')
        cur_file = con_file.cursor()
        # 执行内存数据库脚本
        cur_file.executescript(str_buffer.getvalue())
        # 关闭文件数据库
        cur_file.close()


class Con(object):
    """docstring for Con"""
    quyulist = [[u"东北地区",
                 [u"沈阳", u"大连", u"鞍山", u"锦州", u"抚顺", u"营口", u"盘锦", u"朝阳", u"丹东", u"辽阳", u"本溪", u"葫芦岛", u"铁岭", u"阜新",
                  u"庄河", u"瓦房店", u"哈尔滨", u"大庆", u"齐齐哈尔", u"牡丹江", u"绥化", u"佳木斯", u"鸡西", u"双鸭山", u"鹤岗", u"黑河", u"伊春",
                  u"七台河", u"大兴安岭", u"长春", u"吉林", u"四平", u"延边", u"松原", u"白城", u"通化", u"白山", u"辽源"]],
                [u"华北地区",
                 [u"北京", u"天津", u"石家庄", u"保定", u"唐山", u"廊坊", u"邯郸", u"秦皇岛", u"沧州", u"邢台", u"衡水", u"张家口", u"承德", u"定州",
                  u"馆陶", u"张北", u"赵县", u"正定", u"太原", u"临汾", u"大同", u"运城", u"晋中", u"长治", u"晋城", u"阳泉", u"吕梁", u"忻州",
                  u"朔州", u"临猗", u"清徐", u"呼和浩特", u"包头", u"赤峰", u"鄂尔多斯", u"通辽", u"呼伦贝尔", u"巴彦淖尔市", u"乌兰察布", u"锡林郭勒",
                  u"兴安盟", u"乌海", u"阿拉善盟", u"海拉尔"]],
                [u"华中地区",
                 [u"郑州", u"洛阳", u"新乡", u"南阳", u"许昌", u"平顶山", u"安阳", u"焦作", u"商丘", u"开封", u"濮阳", u"周口", u"信阳", u"驻马店",
                  u"漯河", u"三门峡", u"鹤壁", u"济源", u"明港", u"鄢陵", u"禹州", u"长葛", u"武汉", u"宜昌", u"襄阳", u"荆州", u"十堰", u"黄石",
                  u"孝感", u"黄冈", u"恩施", u"荆门", u"咸宁", u"鄂州", u"随州", u"潜江", u"天门", u"仙桃", u"神农架", u"宜都", u"长沙", u"株洲",
                  u"益阳", u"常德", u"衡阳", u"湘潭", u"岳阳", u"郴州", u"邵阳", u"怀化", u"永州", u"娄底", u"湘西", u"张家界", u"南昌", u"赣州",
                  u"九江", u"宜春", u"吉安", u"上饶", u"萍乡", u"抚州", u"景德镇", u"新余", u"鹰潭", u"永新"]],
                [u"华东地区",
                 [u"青岛", u"济南", u"烟台", u"上海", u"潍坊", u"江西", u"临沂", u"淄博", u"济宁", u"泰安", u"聊城", u"威海", u"枣庄", u"德州",
                  u"日照", u"东营", u"菏泽", u"滨州", u"莱芜", u"章丘", u"垦利", u"诸城", u"寿光", u"苏州", u"南京", u"无锡", u"常州", u"徐州",
                  u"南通", u"扬州", u"盐城", u"淮安", u"连云港", u"泰州", u"宿迁", u"镇江", u"沭阳", u"大丰", u"如皋", u"启东", u"溧阳", u"海门",
                  u"东海", u"扬中", u"兴化", u"新沂", u"泰兴", u"如东", u"邳州", u"沛县", u"靖江", u"建湖", u"海安", u"东台", u"丹阳", u"杭州",
                  u"宁波", u"温州", u"金华", u"嘉兴", u"台州", u"绍兴", u"湖州", u"丽水", u"衢州", u"舟山", u"台湾", u"乐清", u"瑞安", u"义乌",
                  u"余姚", u"诸暨", u"象山", u"温岭", u"桐乡", u"慈溪", u"长兴", u"嘉善", u"海宁", u"德清", u"合肥", u"芜湖", u"蚌埠", u"阜阳",
                  u"淮南", u"安庆", u"宿州", u"六安", u"淮北", u"滁州", u"马鞍山", u"铜陵", u"宣城", u"亳州", u"黄山", u"池州", u"巢湖", u"和县",
                  u"霍邱", u"桐城", u"宁国", u"天长"]],
                [u"华南地区",
                 [u"香港", u"澳门", u"深圳", u"广州", u"东莞", u"佛山", u"中山", u"珠海", u"惠州", u"江门", u"汕头", u"湛江", u"肇庆", u"茂名",
                  u"揭阳", u"梅州", u"清远", u"阳江", u"韶关", u"河源", u"云浮", u"汕尾", u"潮州", u"台山", u"阳春", u"顺德", u"惠东", u"博罗",
                  u"福州", u"厦门", u"泉州", u"莆田", u"漳州", u"宁德", u"三明", u"南平", u"龙岩", u"武夷山", u"石狮", u"晋江", u"南安", u"南宁",
                  u"柳州", u"桂林", u"玉林", u"梧州", u"北海", u"贵港", u"钦州", u"百色", u"河池", u"来宾", u"贺州", u"防城港", u"崇左", u"海口",
                  u"三亚", u"五指山", u"三沙", u"琼海", u"文昌", u"万宁", u"屯昌", u"琼中", u"陵水", u"东方", u"定安", u"澄迈", u"保亭", u"白沙",
                  u"儋州"]],
                [u"西北地区",
                 [u"西安", u"咸阳", u"宝鸡", u"渭南", u"汉中", u"榆林", u"延安", u"安康", u"商洛", u"铜川", u"乌鲁木齐", u"昌吉", u"巴音郭楞", u"伊犁",
                  u"阿克苏", u"喀什", u"哈密", u"克拉玛依", u"博尔塔拉", u"吐鲁番", u"和田", u"石河子", u"克孜勒苏", u"阿拉尔", u"五家渠", u"图木舒克",
                  u"库尔勒", u"阿勒泰", u"塔城", u"兰州", u"天水", u"白银", u"庆阳", u"平凉", u"酒泉", u"张掖", u"武威", u"定西", u"金昌", u"陇南",
                  u"临夏", u"嘉峪关", u"甘南", u"银川", u"吴忠", u"石嘴山", u"中卫", u"固原", u"西宁", u"海西", u"海北", u"果洛", u"海东", u"黄南",
                  u"玉树", u"海南"]],
                [u"西南地区",
                 [u"重庆", u"成都", u"绵阳", u"德阳", u"南充", u"宜宾", u"自贡", u"乐山", u"泸州", u"达州", u"内江", u"遂宁", u"攀枝花", u"眉山",
                  u"广安", u"资阳", u"凉山", u"广元", u"雅安", u"巴中", u"阿坝", u"甘孜", u"昆明", u"曲靖", u"大理", u"红河", u"玉溪", u"丽江",
                  u"文山", u"楚雄", u"西双版纳", u"昭通", u"德宏", u"普洱", u"保山", u"临沧", u"迪庆", u"怒江", u"贵阳", u"遵义", u"黔东南", u"黔南",
                  u"六盘水", u"毕节", u"铜仁", u"安顺", u"黔西南", u"拉萨", u"日喀则", u"山南", u"林芝", u"昌都", u"那曲", u"阿里", u"日土", u"改则"]],
                [u"其他", [u"全国", u"其他"]]]

    def __init__(self, arg):
        super(Con, self).__init__()
        self.arg = arg

    @staticmethod
    def quyu():
        return [[u"东北地区",
                 [u"沈阳", u"大连", u"鞍山", u"锦州", u"抚顺", u"营口", u"盘锦", u"朝阳", u"丹东", u"辽阳", u"本溪", u"葫芦岛", u"铁岭", u"阜新",
                  u"庄河", u"瓦房店", u"哈尔滨", u"大庆", u"齐齐哈尔", u"牡丹江", u"绥化", u"佳木斯", u"鸡西", u"双鸭山", u"鹤岗", u"黑河", u"伊春",
                  u"七台河", u"大兴安岭", u"长春", u"吉林", u"四平", u"延边", u"松原", u"白城", u"通化", u"白山", u"辽源"]],
                [u"华北地区",
                 [u"北京", u"天津", u"石家庄", u"保定", u"唐山", u"廊坊", u"邯郸", u"秦皇岛", u"沧州", u"邢台", u"衡水", u"张家口", u"承德", u"定州",
                  u"馆陶", u"张北", u"赵县", u"正定", u"太原", u"临汾", u"大同", u"运城", u"晋中", u"长治", u"晋城", u"阳泉", u"吕梁", u"忻州",
                  u"朔州", u"临猗", u"清徐", u"呼和浩特", u"包头", u"赤峰", u"鄂尔多斯", u"通辽", u"呼伦贝尔", u"巴彦淖尔市", u"乌兰察布", u"锡林郭勒",
                  u"兴安盟", u"乌海", u"阿拉善盟", u"海拉尔"]],
                [u"华中地区",
                 [u"郑州", u"洛阳", u"新乡", u"南阳", u"许昌", u"平顶山", u"安阳", u"焦作", u"商丘", u"开封", u"濮阳", u"周口", u"信阳", u"驻马店",
                  u"漯河", u"三门峡", u"鹤壁", u"济源", u"明港", u"鄢陵", u"禹州", u"长葛", u"武汉", u"宜昌", u"襄阳", u"荆州", u"十堰", u"黄石",
                  u"孝感", u"黄冈", u"恩施", u"荆门", u"咸宁", u"鄂州", u"随州", u"潜江", u"天门", u"仙桃", u"神农架", u"宜都", u"长沙", u"株洲",
                  u"益阳", u"常德", u"衡阳", u"湘潭", u"岳阳", u"郴州", u"邵阳", u"怀化", u"永州", u"娄底", u"湘西", u"张家界", u"南昌", u"赣州",
                  u"九江", u"宜春", u"吉安", u"上饶", u"萍乡", u"抚州", u"景德镇", u"新余", u"鹰潭", u"永新"]],
                [u"华东地区",
                 [u"青岛", u"济南", u"烟台", u"上海", u"潍坊", u"江西", u"临沂", u"淄博", u"济宁", u"泰安", u"聊城", u"威海", u"枣庄", u"德州",
                  u"日照", u"东营", u"菏泽", u"滨州", u"莱芜", u"章丘", u"垦利", u"诸城", u"寿光", u"苏州", u"南京", u"无锡", u"常州", u"徐州",
                  u"南通", u"扬州", u"盐城", u"淮安", u"连云港", u"泰州", u"宿迁", u"镇江", u"沭阳", u"大丰", u"如皋", u"启东", u"溧阳", u"海门",
                  u"东海", u"扬中", u"兴化", u"新沂", u"泰兴", u"如东", u"邳州", u"沛县", u"靖江", u"建湖", u"海安", u"东台", u"丹阳", u"杭州",
                  u"宁波", u"温州", u"金华", u"嘉兴", u"台州", u"绍兴", u"湖州", u"丽水", u"衢州", u"舟山", u"台湾", u"乐清", u"瑞安", u"义乌",
                  u"余姚", u"诸暨", u"象山", u"温岭", u"桐乡", u"慈溪", u"长兴", u"嘉善", u"海宁", u"德清", u"合肥", u"芜湖", u"蚌埠", u"阜阳",
                  u"淮南", u"安庆", u"宿州", u"六安", u"淮北", u"滁州", u"马鞍山", u"铜陵", u"宣城", u"亳州", u"黄山", u"池州", u"巢湖", u"和县",
                  u"霍邱", u"桐城", u"宁国", u"天长"]],
                [u"华南地区",
                 [u"香港", u"澳门", u"深圳", u"广州", u"东莞", u"佛山", u"中山", u"珠海", u"惠州", u"江门", u"汕头", u"湛江", u"肇庆", u"茂名",
                  u"揭阳", u"梅州", u"清远", u"阳江", u"韶关", u"河源", u"云浮", u"汕尾", u"潮州", u"台山", u"阳春", u"顺德", u"惠东", u"博罗",
                  u"福州", u"厦门", u"泉州", u"莆田", u"漳州", u"宁德", u"三明", u"南平", u"龙岩", u"武夷山", u"石狮", u"晋江", u"南安", u"南宁",
                  u"柳州", u"桂林", u"玉林", u"梧州", u"北海", u"贵港", u"钦州", u"百色", u"河池", u"来宾", u"贺州", u"防城港", u"崇左", u"海口",
                  u"三亚", u"五指山", u"三沙", u"琼海", u"文昌", u"万宁", u"屯昌", u"琼中", u"陵水", u"东方", u"定安", u"澄迈", u"保亭", u"白沙",
                  u"儋州"]],
                [u"西北地区",
                 [u"西安", u"咸阳", u"宝鸡", u"渭南", u"汉中", u"榆林", u"延安", u"安康", u"商洛", u"铜川", u"乌鲁木齐", u"昌吉", u"巴音郭楞", u"伊犁",
                  u"阿克苏", u"喀什", u"哈密", u"克拉玛依", u"博尔塔拉", u"吐鲁番", u"和田", u"石河子", u"克孜勒苏", u"阿拉尔", u"五家渠", u"图木舒克",
                  u"库尔勒", u"阿勒泰", u"塔城", u"兰州", u"天水", u"白银", u"庆阳", u"平凉", u"酒泉", u"张掖", u"武威", u"定西", u"金昌", u"陇南",
                  u"临夏", u"嘉峪关", u"甘南", u"银川", u"吴忠", u"石嘴山", u"中卫", u"固原", u"西宁", u"海西", u"海北", u"果洛", u"海东", u"黄南",
                  u"玉树", u"海南"]],
                [u"西南地区",
                 [u"重庆", u"成都", u"绵阳", u"德阳", u"南充", u"宜宾", u"自贡", u"乐山", u"泸州", u"达州", u"内江", u"遂宁", u"攀枝花", u"眉山",
                  u"广安", u"资阳", u"凉山", u"广元", u"雅安", u"巴中", u"阿坝", u"甘孜", u"昆明", u"曲靖", u"大理", u"红河", u"玉溪", u"丽江",
                  u"文山", u"楚雄", u"西双版纳", u"昭通", u"德宏", u"普洱", u"保山", u"临沧", u"迪庆", u"怒江", u"贵阳", u"遵义", u"黔东南", u"黔南",
                  u"六盘水", u"毕节", u"铜仁", u"安顺", u"黔西南", u"拉萨", u"日喀则", u"山南", u"林芝", u"昌都", u"那曲", u"阿里", u"日土", u"改则"]],
                [u"其他", [u"全国", u"其他"]]]

    @classmethod
    def sqlfire(cls, tablename=None):
        if tablename:
            return '''CREATE TABLE IF NOT EXISTS {tablename} ("公司名称"  text NOT NULL,"城市"  text,"区域"  text,"link"  text NOT NULL,"法人" text,"企业联系人" text,"企业性质" text,"规模" text,"地址" text,"行业" text,"经度" text,"纬度" text,"简介" text,"电话" text,"招聘联系人" text,"职位" text,"要求" text,"薪资" text,"福利" text, "timenow"  text,
UNIQUE ("公司名称" ASC) ON CONFLICT IGNORE);'''.format(tablename=tablename);

    @classmethod
    def sqlinsert(cls, tablename=None, fromname=None, tname=None):
        if tablename and fromname and tname:
            return '''INSERT INTO "{tablename}" (公司名称,城市,区域,link,法人,企业联系人,企业性质,规模,地址,行业,经度,纬度,简介,电话,招聘联系人,职位,要求,薪资,福利,timenow) SELECT "公司名称","城市","区域","link","法人","企业联系人","企业性质","规模","地址","行业","经度","纬度","简介","电话","招聘联系人","职位","要求","薪资","福利","timenow" FROM "{fromname}" WHERE 公司名称 = "{tname}";'''.format(
                tablename=tablename, fromname=fromname, tname=tname);

    @classmethod
    def exincname(cls, conn=None, tablename=None, incname=None):
        incnamecount = conn.execute(
            '''SELECT count(公司名称) FROM "{inserttable}" WHERE "公司名称"={incname};'''.format(inserttable=tablename,
                                                                                         incname=incname))
        exnum = incnamecount.fetchone()[0]
        # print 'incnamecount:',exnum
        if exnum >= 1:
            return True
        else:
            return False

    @classmethod
    def exphone(cls, conn=None, tablename=None, incname=None):
        _incnamecount = conn.execute(
            '''SELECT 城区, 规模, 电话 FROM "{inserttable}" WHERE "公司名称"={incname};'''.format(inserttable=tablename,
                                                                                        incname=incname))
        _r0, _r1, _r2 = _incnamecount.fetchone()
        # print '_incnamecount:',_r0,_r1

        if _r0 and _r1 and _r0 != '' and _r1 != '' and _r2 and _r2 != '' and _r2 != '[]' and _r1 != '[]' and _r0 != '[]':
            return True
        else:
            return False

    @classmethod
    def retlist(cls, diqu=None):
        quyu = cls.quyulist
        for qu in quyu:
            # print json.dumps(qu, ensure_ascii=False)
            # print json.dumps(qu[0], ensure_ascii=False)
            # print json.dumps(qu[1], ensure_ascii=False)
            if diqu in qu[1]:
                return qu[0]
        return "未知"

    @classmethod
    def gosqlite(cls, conn, insname, diqu, quyu1, inc_name1, link1, faren, inclianxi, incxingzhi, guimo, dizhi, hangye,
                 jingdu, weidu, incjianjie, phoneno, zplianxi, zhiwei, yaoqiu, xinzi, fuli):
        quyu = cls.quyulist
        city = inc_name1
        print(insname)
        print(cls.retlist(diqu))
        fenquname = cls.retlist(diqu)
        tablename = insname + fenquname
        sqlfire = '''CREATE TABLE IF NOT EXISTS {tablename} ("公司名称"  text NOT NULL,"城市"  text,"区域"  text,"link"  text NOT NULL,"法人" text,"企业联系人" text,"企业性质" text,"规模" text,"地址" text,"行业" text,"经度" text,"纬度" text,"简介" text,"电话" text,"招聘联系人" text,"职位" text,"要求" text,"薪资" text,"福利" text, "timenow"  text,
UNIQUE ("公司名称" ASC) ON CONFLICT IGNORE);'''.format(tablename=tablename);
        sqlinsert = '''INSERT INTO {instable} (公司名称,城市,区域,link,法人,企业联系人,企业性质,规模,地址,行业,经度,纬度,简介,电话,招聘联系人,职位,要求,薪资,福利,timenow) VALUES ({inc_name},"{city}",{quyu},"{link}","{faren}","{inclianxi}","{incxingzhi}","{guimo}","{dizhi}","{hangye}","{jingdu}","{weidu}","{incjianjie}","{phoneno}","{zplianxi}","{zhiwei}","{yaoqiu}","{xinzi}","{fuli}","{timenow}");'''.format(
            instable=tablename, city=city, quyu=quyu1, inc_name=inc_name1, link=link1, faren=faren, inclianxi=inclianxi,
            incxingzhi=incxingzhi, guimo=guimo, dizhi=dizhi, hangye=hangye, jingdu=jingdu, weidu=weidu,
            incjianjie=incjianjie, phoneno=phoneno, zplianxi=zplianxi, zhiwei=zhiwei, yaoqiu=yaoqiu, xinzi=xinzi,
            fuli=fuli, timenow=time.strftime('%Y-%m-%d %H:%M:%S'));
        # print sqlfire.decode('utf-8')
        try:
            conn.execute(sqlfire)
            conn.execute(sqlinsert)
        except Exception as  e:
            print(str(e))
