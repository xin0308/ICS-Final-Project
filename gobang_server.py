import socket
import threading
import random

bind_ip = ""#运行这个程序的终端的IP地址
bind_port = 9999
unsended_buffer1 = False #判断是否有未发送给客户端的数据
unsended_buffer2 = False
buffer = "" #记录将发送的数据
client1_ip = "" #两个客户端的IP地址
client2_ip = ""
c1_side = random.randint(0,1) #随机选黑白方
c2_side = 1 - c1_side
#开始监听端口
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)
print("[*] listening on %s:%d" % (bind_ip, bind_port))
#处理收到的消息
def handle_client(client_socket, ip):
    global unsended_buffer1
    global unsended_buffer2
    global buffer
    request = client_socket.recv(4096)
    if ip == client1_ip:
        if request != b"NULL":
            print("[*] Received: %s" % request)
            if request.decode().split("/")[0] == "OPR":
                buffer = request
                unsended_buffer2 = True #收到操作消息，返回给双方
            if request.decode().split("/")[0] == "INI":
                buffer = ("INI/" + str(c1_side)).encode('gbk') #收到初始化消息，返回给发送方
            if request.decode().split("/")[0] == "RST":
                buffer = request
                unsended_buffer2 = True #收到结果消息，返回给双方
            unsended_buffer1 = True
    if ip == client2_ip:
        if request != b"NULL":
            print("[*] Received: %s" % request)
            if request.decode().split("/")[0] == "OPR":
                buffer = request
                unsended_buffer1 = True
            if request.decode().split("/")[0] == "INI":
                buffer = ("INI/" + str(c2_side)).encode('gbk')
            if request.decode().split("/")[0] == "RST":
                buffer = request
                unsended_buffer1 = True
            unsended_buffer2 = True
    #发送消息给客户端
    if ip == client1_ip and unsended_buffer1:
        client_socket.send(buffer)
        unsended_buffer1 = False
    if ip == client2_ip and unsended_buffer2:
        client_socket.send(buffer)
        unsended_buffer2 = False
        
    client_socket.close()

while True:
    client,addr = server.accept()
    #自动获取客户端IP地址
    if client1_ip == "":
        client1_ip = addr[0]
    elif client2_ip == ""and client1_ip != addr[0]:
        client2_ip = addr[0]
    client_handler = threading.Thread(target = handle_client, args = (client, addr[0]))
    client_handler.start()
