from pbf import PBF
from utils.RegCmd import RegCmd
import sys, requests, telnetlib, threading, os, random, traceback, re
from tcping import Ping
from bs4 import BeautifulSoup as bs

from plugins.tools import tools

_name = "网站系统"
_version = "1.0.1"
_description = "黑白系统，包括与猪比官网互联、站长工具"
_author = "xzyStudio"
_cost = 0.00

class website(PBF):
    def __enter__(self):
        return [
            RegCmd(
                name = "QQ绑定 ",
                usage = "QQ绑定 <用户ID> <密钥>",
                permission = "anyone",
                function = "website@connectQQ",
                description = "将该用户与网站账户绑定",
                mode = "官网功能",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "QQ群绑定 ",
                usage = "QQ群绑定 <用户QQ号>",
                permission = "ao",
                function = "website@connectQG",
                description = "将该用户绑定到此QQ群，他可以管理该群设置",
                mode = "官网功能",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "QQ群解绑 ",
                usage = "QQ群解绑 <用户QQ号>",
                permission = "admin",
                function = "website@disconnectQG",
                description = "将该用户解绑到此QQ群",
                mode = "官网功能",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "ping ",
                usage = "ping <IP> <Port>",
                permission = "anyone",
                function = "website@ping_check",
                description = "ping某IP",
                mode = "站长工具",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "whois ",
                usage = "whois <域名>",
                permission = "anyone",
                function = "website@whois",
                description = "查询某域名的whois信息",
                mode = "站长工具",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "扫描端口 ",
                usage = "扫描端口 <IP>",
                permission = "admin",
                function = "website@telnetport",
                description = "扫描某IP开放的端口，刷屏警告！",
                mode = "站长工具",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "SEO查询 ",
                usage = "SEO查询 <域名>",
                permission = "anyone",
                function = "website@seoCheck",
                description = "查询SEO权重",
                mode = "站长工具",
                hidden = 0,
                type = "command"
            )
        ]
    
    def disconnectQG(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        uuid = self.data.uuid
        
        self.mysql.commonx('DELETE FROM `botConnectqg` WHERE `uuid`=%s and `uid`=%s and `gid`=%s', (uuid, uid, gid))
        self.client.msg().raw('[CQ:face,id=54] 解绑成功！')
    
    def connectQG(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        uuid = self.data.uuid
        
        if not gid:
            return self.client.msg().raw('请在要绑定的群组中使用该指令！')
        
        if not self.mysql.selectx('SELECT * FROM `botConnectqg` WHERE `uuid`=%s and `uid`=%s and `gid`=%s', (uuid, uid, gid)):
            self.mysql.commonx('INSERT INTO `botConnectqg` (`uuid`,`uid`,`gid`) VALUES (%s, %s, %s);', (uuid, message, gid))
            self.client.msg().raw('[CQ:face,id=54] 绑定成功！')
        else:
            self.client.msg().raw('[CQ:face,id=151] 该用户已经绑定过本群了！')
    
    def connectQQ(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        message1 = message.split(' ')
        userid = message1[0]
        pswd = message1[1]
        listt = self.mysql.selectx("SELECT * FROM `into` WHERE `id` = %s", (userid), database='php10')[0]
        if listt.get('qqpswd') == pswd and listt.get('qqpswd') != '':
            self.mysql.commonx('UPDATE `into` SET `qqstate`=%s, `qqpswd`="" WHERE `id`=%s', (uid, userid), database='php10')
            self.client.msg().raw('[CQ:face,id=54] 绑定成功！')
        else:
            self.client.msg().raw('[CQ:face,id=151] 参数二（密钥）不正确，禁止冒充他人绑定！')
            
            
    # ---站长工具---
    def get_ip_status(self, ip, port):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        
        server = telnetlib.Telnet()
        try:
            server.open(ip,port)
            self.client.msg().raw('{0} port {1} is open'.format(ip, port))
        finally:
            server.close()
            
    def telnetport(self, minport=20, maxport=36500):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        if '127.0.0.1' in message:
            self.client.msg().raw('禁止扫描我的服务器！')
            return 
        
        host = message
        threads = []
        for port in range(minport, maxport):
            t = threading.Thread(target=self.get_ip_status,args=(host, port))
            t.start()
            threads.append(t)
     
        for t in threads:
            t.join()
    
    def whois(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        con = os.popen('whois '+str(message))
        con = con.read()
        if con:
            self.client.msg().raw(con)
        else:
            self.client.msg().raw('没有查询到')
    
    def ping_check(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        message1 = message.split(' ')
        ip = message1[0]
        port = message1[1]
        
        self.client.msg().raw('正在努力ping中...')
        ping = Ping(ip, port, 60)
        ping.ping(10)
    
        ret = ping.result.rows
        for r in ret:
            self.client.msg().raw(r)
        ret = ping.result.raw
        ret = ping.result.table
    
    # 伪造请求，取得html页面
    def get_html(self, url):
        # 定义http的请求Header
        headers = {} 
        # random.randint(1,99) 为了生成1到99之间的随机数，让UserAgent变的不同。
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537." + str(random.randint(1, 99))
        # Referer地址使用待查询的网址
        headers['Referer'] = "http://seo.chinaz.com/" + url + "/"
        html = ''
        try:
            html = requests.get("http://seo.chinaz.com/" + url + "/", headers=headers, timeout=5).text
        except Exception as e:
            pass
        return html
    
    # 利用BeautifulSoup模块从html页面中提取数据
    def get_data(self, html, url):
        try:
            if not html:
                return url, 0
            soup = bs(html, "lxml")
            p_tag = soup.select("p.ReLImgCenter")[0]
            src = p_tag.img.attrs["src"]
            regexp = re.compile(r'^http:.*?(\d).gif')
            br = regexp.findall(src)[0]
            return url, br
        except Exception as e:
            pass
    
    def seoCheck(self):
        self.client.msg().raw("Loading...")
        # html = self.get_html(self.data.message)
        # data = self.get_data(html, self.data.message)
        # self.CrashReport(data)
        self.data.message = "http://seo.chinaz.com/{}".format(self.data.message)
        toolsClazz = tools(self.data)
        toolsClazz.getWP(echo=False, length=1000)