import socket
import time
import sys
import threading
import pygame #需要pip install一下


target_host = ""#这个是服务器的ip地址，要改成那个Gobang Server.py运行的地方的IP地址
target_port = 9999
message = "NULL" #发送给服务器的消息
response = "" #从服务器接收到的消息
side = 1 #0 代表黑方/1 代表白方
FPS = 60 #帧率（可调）
event_list = []
#定义颜色变量
brown = pygame.Color(240, 180, 110)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
#定义记录棋子位置的列表
black_piece_list = []
white_piece_list = []
turn = 0 #记录轮到谁下棋
size = 10 #布局的尺寸（可调）
timer = int(time.time())

#定义一个持续和服务器交互的函数
def interaction():
    global response
    global message
    while turn != -1:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((target_host, target_port))
        client.send(message.encode('gbk'))
        message = "NULL" #通过不停发送"NULL"消息来监听服务器的返回值，因为服务器只有收到消息才能返回消息
        response = client.recv(4096).decode()
        pygame.time.Clock().tick(FPS) #设置帧率

def request_handler(surface):
    global message
    global timer
    pos_x, pos_y = 0, 0
    piece_x, piece_y = 0, 0
    message = "INI" #发送初始化请求，获取黑方/白方信息
    time.sleep(1)
    if side:
        cursor_color = pygame.Color(255, 255, 255, 200)
    else:
        cursor_color = pygame.Color(0, 0, 0, 200)
    while turn != -1:
        surface.fill(brown)
        #绘制棋盘
        for i in range(1, 16):
            pygame.draw.line(surface, black, (size, (i * size * 3 - size * 2)), ((size * 45 - size * 2), (i * size * 3 - size * 2)), 2)
            pygame.draw.line(surface, black, ((i * size * 3 - size * 2), size), ((i * size * 3 - size * 2), (size * 45 - size * 2)), 2)
        cursor = pygame.draw.circle(surface, cursor_color, ((piece_x * size * 3 - size * 2), (piece_y * size * 3 - size * 2)), size)

        for event in event_list:
            if event.type == pygame.MOUSEMOTION: #监听鼠标移动，把棋子吸附到格点处
                pos_x, pos_y = pygame.mouse.get_pos()
                piece_x = 15
                piece_y = 8
                for i in range(1,16):
                    if abs(pos_x - (i * size * 3 - size * 2)) <= size * 3 / 2:
                        piece_x = i
                    if abs(pos_y - (i * size * 3 - size * 2)) <= size * 3 / 2:
                        piece_y = i
                    
            elif event.type == pygame.MOUSEBUTTONDOWN: #落子
                if event.button == 1 and (turn + side) % 2 == 0:
                    if not (piece_x, piece_y) in black_piece_list + white_piece_list:
                        message = "OPR/" + str(side) + "/" + str((piece_x, piece_y))
                        judge(piece_x, piece_y)
        #绘制棋子
        for piece in black_piece_list:
            pygame.draw.circle(surface, black, (piece[0] * size * 3 - size * 2, piece[1] * size * 3 - size * 2), size)
        for piece in white_piece_list:
            pygame.draw.circle(surface, white, (piece[0] * size * 3 - size * 2, piece[1] * size * 3 - size * 2), size)
            
        font = pygame.font.SysFont('arial', 20)
        if (turn + side) % 2 == 0:
            time_left = 30 - (int(time.time()) - timer) #限制时长30s
        else:
            time_left = 30
        txtsurface = font.render(str(time_left), False, white)
        txtrect = txtsurface.get_rect()
        txtrect.center = (size * 45 + 40, size * 5)
        surface.blit(txtsurface, txtrect)
        if time_left <= 0:
            message = "RST/" + str(1 - side)
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

#定义一个处理服务器返回数据的函数
def response_handler(surface):
    global response
    global side
    global turn
    global timer
    while turn != -1:
        if response != "":
            if response.split("/")[0] == "INI":#返回选边
                if response.split("/")[1] == "0":
                    side = 0
                else:
                    side = 1
                print(response)
                print(side)
            if response.split("/")[0] == "OPR":#返回操作
                turn += 1
                if response.split("/")[1] == '1':
                    white_piece_list.append(eval(response.split("/")[2]))
                else:
                    black_piece_list.append(eval(response.split("/")[2]))
                if response.split("/")[1] != str(side):
                    timer = int(time.time())
            if response.split("/")[0] == "RST":#返回游戏结果
                turn = -1
                if response.split("/")[1] == str(side):
                    win(surface)
                else:
                    lose(surface)
        response = ""
        pygame.time.Clock().tick(FPS)

#初始化窗口
def client_init():
    pygame.init()
    surface = pygame.display.set_mode(((size * 45 + 80), (size * 45 - size)))
    pygame.display.set_caption('Gobang')
    surface.fill(brown)
    for i in range(1, 16):
        pygame.draw.line(surface, black, (size, (i * size * 3 - size * 2)), ((size * 45 - size * 2), (i * size * 3 - size * 2)), 2)
        pygame.draw.line(surface, black, ((i * size * 3 - size * 2), size), ((i * size * 3 - size * 2), (size * 45 - size * 2)), 2)
    pygame.display.flip()
    return surface

#定义五子连棋的判断函数
#算法：在落子后预先枚举包含这个子的20种五子相连的可能，一一带入棋子位置列表检查
def judge(piece_x, piece_y):
    global message
    combo_list = []
    combo = 0
    directions = [(0, 1), (1, 1), (1, 0), (1, -1)]
    try:
        for direction in directions:
            for index in range(0, 5):
                combo_list = []
                combo = 0
                for i in range(-4, 1):
                    if index + i != 0:
                        combo_list.append((piece_x + direction[0] * (index + i), piece_y + direction[1] * (index + i)))
                for combo_piece in combo_list:
                    if (combo_piece in black_piece_list and side == 0) or (combo_piece in white_piece_list and side == 1):
                        combo += 1
                    if combo == 4:#五子连棋
                        time.sleep(0.5)
                        message = "RST/" + str(side)#发送胜利消息
                        raise StopIteration
    except StopIteration:#通过报错跳出外循环（这个try...except...语句不要也可以）
        pass

#获胜函数（你可以自己再改改）
def win(surface):
    global turn
    font = pygame.font.SysFont('arial', 32)
    txtsurface = font.render(u'You Win!', False, white)
    txtrect = txtsurface.get_rect()
    txtrect.center = (size * 25, size * 25)
    surface.blit(txtsurface, txtrect)
    print("You win")
    turn = -1
    time.sleep(5)

#失败函数
def lose(surface):
    global turn
    font = pygame.font.SysFont('arial', 32)
    txtsurface = font.render(u'You Lose!', False, white)
    txtrect = txtsurface.get_rect()
    txtrect.center = (size * 25, size * 25)
    surface.blit(txtsurface, txtrect)
    print("You lose")
    turn = -1
    time.sleep(5)

#主函数
def main():
    global turn
    global event_list
    surface = client_init() #初始化
    #多线程
    interaction_thread = threading.Thread(target = interaction)
    interaction_thread.start()
    handle_request = threading.Thread(target = request_handler, args = (surface, ))
    handle_request.start()
    handle_response = threading.Thread(target = response_handler, args = (surface, ))
    handle_response.start()
    while turn != -1:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                turn = -1
                pygame.quit()
                sys.exit()
        pygame.time.Clock().tick(FPS)

if __name__ == "__main__":
    main()
