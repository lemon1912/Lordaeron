#coding=utf-8
import re
import pyte
import operator
import paramiko
import os,time,sys
import datetime
import errno
import getpass
import termios
import tty


import struct, fcntl, signal, socket, select

class Tty(object):
    """
    A virtual tty class
    一个虚拟终端类，实现连接ssh和记录日志，基类
    """
    def __init__(self, hostname,username, passwd,port=22):
        self.hostname = hostname
        self.username = username
        self.passwd = passwd
        self.port = port
        self.ip = None
        self.vim_end_pattern = re.compile(r'\x1b\[\?1049', re.X)
        self.vim_flag = False
        self.vim_data = ''
        # self.stream = None
        # self.screen = None
        self.__init_screen_stream()
        self.log_file = None
        self.log_time = None
        self.log_cmd  = None
        self.enable_logging = False

    def __init_screen_stream(self):
        """
        初始化虚拟屏幕和字符流
        """
        self.stream = pyte.ByteStream()
        self.screen = pyte.Screen(80, 24)
        #Adds a given screen to the listener queue
        self.stream.attach(self.screen)

    @staticmethod
    def is_output(strings):
        newline_char = ['\n', '\r', '\r\n']
        for char in newline_char:
            if char in strings:
                return True
        return False

    @staticmethod
    def command_parser(command):
        """
        处理命令中如果有ps1或者mysql的特殊情况,极端情况下会有ps1和mysql
        :param command:要处理的字符传
        :return:返回去除PS1或者mysql字符串的结果
        """
        result = None
        match = re.compile('\[?.*@.*\]?[\$#]\s').split(command)
        if match:
            # 只需要最后的一个PS1后面的字符串
            result = match[-1].strip()
        else:
            # PS1没找到,查找mysql
            match = re.split('mysql>\s', command)
            if match:
                # 只需要最后一个mysql后面的字符串
                result = match[-1].strip()
        return result

    def deal_command(self, data):
        """
        处理截获的命令
        :param data: 要处理的命令
        :return:返回最后的处理结果
        """
        command = ''
        try:
            #把命令添加到输出流
            self.stream.feed(data)
            # 从虚拟屏幕中获取处理后的数据
            #reversed()函数是反转遍历
            #screen.buffer大小应该就是上面设定的(80, 24)
            for line in reversed(self.screen.buffer):
                #operator.attrgetter("data")返回的是一个函数,line应该是个列表,
                #map的左右作用是遍历line依次传递到参数1返回的函数中,并把最终结果以列表形式返回
                line_data = "".join(map(operator.attrgetter("data"), line)).strip()
                if len(line_data) > 0:
                    parser_result = self.command_parser(line_data)
                    if parser_result is not None:
                        # 2个条件写一起会有错误的数据
                        if len(parser_result) > 0:
                            command = parser_result
                    else:
                        command = line_data
                    break
        except Exception:
            pass
        # 重置终端状态为初始值
        self.screen.reset()
        return command

    def get_connection(self):
        """
        获取连接成功后的ssh
        """
        # 发起ssh连接请求 Make a ssh connection
        client = paramiko.SSHClient()
        home_dir = os.path.expanduser('~')
        # ssh.load_system_host_keys()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            #host_keys = home_dir + '/.ssh/known_hosts'
            id_rsa = home_dir + '/.ssh/id_rsa'
            #if  not ssh.load_system_host_keys(host_keys):
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if os.path.isfile(id_rsa):
                p_key = paramiko.RSAKey.from_private_key_file(id_rsa)
                try:
                    client.connect(hostname=self.hostname, port=self.port, username=self.username, pkey=p_key)
                    return client
                except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException):
                    pass
            print '使用私钥登陆失败,开始尝试使用密码登陆'
            client.connect(hostname=self.hostname,
                        port=self.port,
                        username=self.username,
                        password=self.passwd,
                        look_for_keys=False)
            print '登录成功'
        except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException):
            print('认证失败 Authentication Error.')
        except socket.error:
            print('端口可能不正确(Connect SSH Socket Port Error, Please Correct it.)')
            os.sys.exit(-1)
        else:
            self.client = client
            return client

    def logging(self,log_file,log_time,log_cmd):
        self.enable_logging = True
        self.log_file = log_file
        self.log_time = log_time
        self.log_cmd  = log_cmd

class SshTty(Tty):

    @staticmethod
    def get_win_size():
        """
        This function use to get the size of the windows!
        获得terminal窗口大小
        """
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        else:
            TIOCGWINSZ = 1074295912L
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    # def set_win_size(self, sig, data):
    def set_win_size(self, sig, data):
        """
        This function use to set the window size of the terminal!
        设置terminal窗口大小
        """
        try:
            win_size = self.get_win_size()
            # 调整伪终端的大小。 这可以用于更改在先前的get_pty调用中创建的终端仿真的宽度和高度。
            self.channel.resize_pty(height=win_size[0], width=win_size[1])
        except Exception:
            pass

    def posix_shell(self):
        """
        Use paramiko channel connect server interactive.
        使用paramiko模块的channel，连接后端，进入交互式
        """
        # log_file_f, log_time_f = self.get_log()
        #返回包含文件描述符fd的tty属性的列表
        old_tty = termios.tcgetattr(sys.stdin)
        pre_timestamp = time.time()
        data = ''
        input_mode = False

        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            self.channel.settimeout(0.0)

            while True:
                try:
                    r, w, e = select.select([self.channel, sys.stdin], [], [])
                    flag = fcntl.fcntl(sys.stdin, fcntl.F_GETFL, 0)
                    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flag | os.O_NONBLOCK)
                except Exception:
                    pass

                if self.channel in r:
                    try:
                        x = self.channel.recv(10240)
                        if len(x) == 0:
                            break

                        index = 0
                        len_x = len(x)
                        while index < len_x:
                            try:
                                n = os.write(sys.stdout.fileno(), x[index:])
                                sys.stdout.flush()
                                index += n
                            except OSError as msg:
                                if msg.errno == errno.EAGAIN:
                                    continue
                        if self.enable_logging:
                            now_timestamp = time.time()
                            self.log_time.write('%s %s\n' % (round(now_timestamp - pre_timestamp, 4), len(x)))
                            self.log_time.flush()
                            self.log_file.write(x)
                            self.log_file.flush()
                            pre_timestamp = now_timestamp
                        # log_file_f.flush()

                        self.vim_data += x
                        if input_mode:
                            data += x

                    except socket.timeout:
                        pass

                if sys.stdin in r:
                    try:
                        x = os.read(sys.stdin.fileno(), 4096)
                    except OSError:
                        pass
                        # termlog.recoder = True
                    input_mode = True
                    if self.is_output(str(x)):
                        # 如果len(str(x)) > 1 说明是复制输入的
                        if len(str(x)) > 1:
                            data = x
                        match = self.vim_end_pattern.findall(self.vim_data)
                        if match:
                            if self.vim_flag or len(match) == 2:
                                self.vim_flag = False
                            else:
                                self.vim_flag = True
                        elif not self.vim_flag:
                            self.vim_flag = False
                            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            cmd = self.deal_command(data)[0:200]
                            self.log_cmd.write('%s  %s\n' % (current_time, cmd))
                            self.log_cmd.flush()
                            #####################################
                        data = ''
                        self.vim_data = ''
                        input_mode = False

                    if len(x) == 0:
                        break
                    self.channel.send(x)

        except Exception,e:
            pass

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            if self.enable_logging:
                self.log_file.write('End time is %s' % datetime.datetime.now())
                self.log_file.close()
                self.log_time.close()
                self.log_cmd.close()
    def connect(self):
        """
        Connect server.
        连接服务器
        """
        # 发起ssh连接请求 Make a ssh connection
        client = self.get_connection()
        #返回此SSH连接的底层Transport对象。 这可以用于执行较低级别的任务，例如打开特定类型的渠道
        transport = client.get_transport()
        #每隔30秒向服务器发送数据包,用来保持连接
        transport.set_keepalive(30)
        #开启压缩传输,但对交互会话有负面影响
        transport.use_compression(True)

        # 获取连接的隧道并设置窗口大小 Make a channel and set windows size
        # global channel
        win_size = self.get_win_size()
        # self.channel = channel = ssh.invoke_shell(height=win_size[0], width=win_size[1], term='xterm')
        self.channel  = transport.open_session()
        #请求服务器使用伪终端
        self.channel.get_pty(term='xterm', height=win_size[0], width=win_size[1])
        #在此频道上请求交互式shell会话。 如果服务器允许它，那么通道将直接连接到
        # shell的stdin，stdout和stderr。通常你会在这之前调用get_pty，
        # 在这种情况下，shell将通过pty操作，并且通道将被连接到pty的stdin和stdout。
        #当外壳退出时，通道将关闭，不能重复使用。 如果您想打开另一个shell，您必须打开一个新频道。
        self.channel.invoke_shell()

        try:
            #忽略窗口大小的变化
            signal.signal(signal.SIGWINCH, self.set_win_size)
        except:
            pass

        self.posix_shell()

        # Shutdown channel socket
        self.channel.close()
        client.close()
        