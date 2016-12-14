#coding=utf-8
import paramiko
import socket
import traceback
import sys
import os
import interactive



username = 'root'
password = 'Lemon19121010'
hostname = '47.88.192.91'
port = 22

try:
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((hostname, port))
except Exception,e:
    print('*** Connect failed: ' + str(e))
    #获取详细异常信息
    traceback.print_exc()
    sys.exit(-1)

try:
    #Create a new SSH session over an existing socket,or socket-like object
    #参数是sock或者是(ip,port)的元祖类型,感觉写元祖可以少写上面的socket
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        print('*** SSH negotiation failed.')
        sys.exit(1)

    try:
        keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    except IOError:
        print('*** Unable to open host keys file')
        keys = {}



    #获取服务器上与客户端生成的秘钥
    key = t.get_remote_server_key()
    if hostname not in keys:
        print('*** WARNING: Unknown host key!')
    #key.get_name() 获取的是秘钥类型 keys[hostname]获取的是秘钥秘钥类型和加密内容
    #如果出现加密类型不匹配打印报警
    elif key.get_name() not in keys[hostname]:
        print('*** WARNING: Unknown host key!')
    #更换过服务器的IP会出现这个问题
    elif keys[hostname][key.get_name()] != key:
        print('*** WARNING: Host key has changed!!!')
        sys.exit(1)
    else:
        print('*** Host key OK.')

    t.auth_password(username=username,password=password)

    if not t.is_authenticated():
        print('*** Authentication failed. :(')
        t.close()
        sys.exit(1)


    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    interactive.interactive_shell(chan)

    chan.close()
    t.close()

except Exception as e:

    print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))

    traceback.print_exc()

    try:

        t.close()

    except:

        pass

    sys.exit(1)



