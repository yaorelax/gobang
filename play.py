import pygame
import numpy as np
import os
import sys
import json
import subprocess as sub
import requests
import time
import re
from random import randint
from pygame.locals import *
from sko.GA import GA
from sko.operators import ranking, crossover, mutation


SCREEN_X = 900
SCREEN_Y = 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
checkerboard_image_name = 'Resource/Image/Checkerboard.jpg'
curtain_image_name = 'Resource/Image/curtain.jpg'
black_image_name = 'Resource/Image/Black.png'
white_image_name = 'Resource/Image/White.png'
pygame.font.init()
font = pygame.font.SysFont('arial', 40)
font_chs = pygame.font.SysFont('simsunnsimsun', 25)
font_setting = pygame.font.SysFont('simsunnsimsun', 40)
font_title = pygame.font.SysFont('simsunnsimsun', 100)
natapp_address = 'Resource/Plugin/natapp.exe'
server_address = 'http://fj5pab.natappfree.cc'
host = '127.0.0.1'
port = '8866'
global screen, checkerboard, curtain, black, white, white_list, black_list, dot_list
global mode, flag, win, step, last, _pos, my_color
global live_5, live_4, sleep_4, live_3, sleep_3, live_2, sleep_2

def start_up():
    global screen, checkerboard, curtain, black, white, dot_list
    pygame.init()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (150, 100)
    screen_size = (SCREEN_X, SCREEN_Y)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('五子棋-yaorelax')
    checkerboard = pygame.image.load(checkerboard_image_name).convert()
    curtain = pygame.image.load(curtain_image_name).convert()
    black = pygame.image.load(black_image_name).convert_alpha()
    white = pygame.image.load(white_image_name).convert_alpha()
    dot_list = [(20 + i * 40 - white.get_width() / 2,
                 20 + j * 40 - white.get_height() / 2)
                for i in range(15) for j in range(15)]

class Button(object):
    def __init__(self, text, color, font_button, x=None, y=None, **kwargs):
        self.surface = font_button.render(text, True, color)
        self.WIDTH = self.surface.get_width()
        self.HEIGHT = self.surface.get_height()

        if 'centered_x' in kwargs and kwargs['centered_x']:
            self.x = SCREEN_X // 2 - self.WIDTH // 2
        else:
            self.x = x

        if 'centered_y' in kwargs and kwargs['cenntered_y']:
            self.y = SCREEN_Y // 2 - self.HEIGHT // 2
        else:
            self.y = y

    def display(self):
        screen.blit(self.surface, (self.x, self.y))

    def check_click(self, position):
        x_match = position[0] > self.x and position[0] < self.x + self.WIDTH
        y_match = position[1] > self.y and position[1] < self.y + self.HEIGHT

        if x_match and y_match:
            return True
        else:
            return False


def welcome():
    screen.blit(curtain, (0, 0))
    game_title = font_title.render('五子棋', True, BLACK)
    font_button = pygame.font.SysFont('simsunnsimsun', 55)

    play_button = Button('开始', BLACK, font_button, None, 330, centered_x=True)
    exit_button = Button('退出', BLACK, font_button, None, 400, centered_x=True)

    while True:
        if play_button.check_click(pygame.mouse.get_pos()):
            play_button = Button('开始', RED, font_button, None, 330, centered_x=True)
        else:
            play_button = Button('开始', BLACK, font_button, None, 330, centered_x=True)

        if exit_button.check_click(pygame.mouse.get_pos()):
            exit_button = Button('退出', RED, font_button, None, 400, centered_x=True)
        else:
            exit_button = Button('退出', BLACK, font_button, None, 400, centered_x=True)

        screen.blit(curtain, (0, 0))
        screen.blit(game_title, (SCREEN_X // 2 - game_title.get_width() // 2, 150))
        play_button.display()
        exit_button.display()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONUP:
                if play_button.check_click(pygame.mouse.get_pos()):
                    return
                if exit_button.check_click(pygame.mouse.get_pos()):
                    sys.exit()
        pygame.event.pump()


def init_checkerboard():
    global white_list, black_list, flag, win, step
    screen.blit(checkerboard, (0, 0))
    if mode != 200:
        screen.blit(font_setting.render('按R新局', True, (0, 0, 0)), (666, 450))
    screen.blit(font_setting.render('按M选模式', True, (0, 0, 0)), (666, 500))
    if my_color == 0:
        screen.blit(font_setting.render('你是黑', True, (0, 0, 0)), (666, 10))
    elif my_color == 1:
        screen.blit(font_setting.render('你是白', True, (0, 0, 0)), (666, 10))
    elif my_color == -1:
        pass
    white_list = np.zeros((15, 15), dtype=int)
    black_list = np.zeros((15, 15), dtype=int)
    pygame.event.set_blocked(
        [1, 4, KEYUP, JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, MOUSEBUTTONUP])
    pygame.event.set_allowed([MOUSEBUTTONDOWN, MOUSEBUTTONUP, 12, KEYDOWN])
    flag = 0
    win = 0
    step = 0
    god1.restart()
    god2.restart()
    paint_present_player()
    pygame.display.update()

def select_mode():
    global mode, my_color, server_address
    my_color = -1
    screen.blit(curtain, (0, 0))
    screen.blit(font_setting.render('选择模式', True, (0, 0, 0)), (350, 20))

    font_button = font_chs

    button_0 = Button('玩家vs玩家', BLACK, font_button, 40, 100)
    button_1 = Button('玩家vs猴子', BLACK, font_button, 40, 140)
    button_2 = Button('玩家vs智障', BLACK, font_button, 40, 180)
    button_3 = Button('玩家vs初中生', BLACK, font_button, 40, 220)
    button_4 = Button('玩家vs生物学家', BLACK, font_button, 40, 260)
    button_5 = Button('玩家vs高中生', BLACK, font_button, 40, 300)
    button_6 = Button('玩家vs大学生', BLACK, font_button, 40, 340)
    button_7 = Button('玩家vs神', BLACK, font_button, 40, 380)
    button_8 = Button('玩家vs神强化', BLACK, font_button, 40, 420)

    button_101 = Button('猴子vs猴子', BLACK, font_button, 300, 140)
    button_102 = Button('智障vs智障', BLACK, font_button, 300, 180)
    button_103 = Button('初中生vs初中生', BLACK, font_button, 300, 220)
    button_104 = Button('生物学家vs生物学家', BLACK, font_button, 300, 260)
    button_105 = Button('高中生vs高中生', BLACK, font_button, 300, 300)
    button_106 = Button('大学生vs大学生', BLACK, font_button, 300, 340)
    button_107 = Button('神vs神', BLACK, font_button, 300, 380)
    button_108 = Button('神强化vs神强化', BLACK, font_button, 300, 420)

    button_156 = Button('高中生vs大学生', BLACK, font_button, 600, 140)
    button_167 = Button('大学生vs神', BLACK, font_button, 600, 180)
    button_160 = Button('大学生vs玩家', BLACK, font_button, 600, 220)

    # button_200 = Button('WAN(在server_address.ini中填写服务器地址)', BLACK, font_button, None, 480, centered_x=True)


    while True:
        if button_0.check_click(pygame.mouse.get_pos()):
            button_0 = Button('玩家vs玩家', RED, font_button, 40, 100)
        else:
            button_0 = Button('玩家vs玩家', BLACK, font_button, 40, 100)
        if button_1.check_click(pygame.mouse.get_pos()):
            button_1 = Button('玩家vs猴子', RED, font_button, 40, 140)
        else:
            button_1 = Button('玩家vs猴子', BLACK, font_button, 40, 140)
        if button_2.check_click(pygame.mouse.get_pos()):
            button_2 = Button('玩家vs智障', RED, font_button, 40, 180)
        else:
            button_2 = Button('玩家vs智障', BLACK, font_button, 40, 180)
        if button_3.check_click(pygame.mouse.get_pos()):
            button_3 = Button('玩家vs初中生', RED, font_button, 40, 220)
        else:
            button_3 = Button('玩家vs初中生', BLACK, font_button, 40, 220)
        if button_4.check_click(pygame.mouse.get_pos()):
            button_4 = Button('玩家vs生物学家', RED, font_button, 40, 260)
        else:
            button_4 = Button('玩家vs生物学家', BLACK, font_button, 40, 260)
        if button_5.check_click(pygame.mouse.get_pos()):
            button_5 = Button('玩家vs高中生', RED, font_button, 40, 300)
        else:
            button_5 = Button('玩家vs高中生', BLACK, font_button, 40, 300)
        if button_6.check_click(pygame.mouse.get_pos()):
            button_6 = Button('玩家vs大学生', RED, font_button, 40, 340)
        else:
            button_6 = Button('玩家vs大学生', BLACK, font_button, 40, 340)
        if button_7.check_click(pygame.mouse.get_pos()):
            button_7 = Button('玩家vs神', RED, font_button, 40, 380)
        else:
            button_7 = Button('玩家vs神', BLACK, font_button, 40, 380)
        if button_8.check_click(pygame.mouse.get_pos()):
            button_8 = Button('玩家vs神强化', RED, font_button, 40, 420)
        else:
            button_8 = Button('玩家vs神强化', BLACK, font_button, 40, 420)
        if button_101.check_click(pygame.mouse.get_pos()):
            button_101 = Button('猴子vs猴子', RED, font_button, 300, 140)
        else:
            button_101 = Button('猴子vs猴子', BLACK, font_button, 300, 140)
        if button_102.check_click(pygame.mouse.get_pos()):
            button_102 = Button('智障vs智障', RED, font_button, 300, 180)
        else:
            button_102 = Button('智障vs智障', BLACK, font_button, 300, 180)
        if button_103.check_click(pygame.mouse.get_pos()):
            button_103 = Button('初中生vs初中生', RED, font_button, 300, 220)
        else:
            button_103 = Button('初中生vs初中生', BLACK, font_button, 300, 220)
        if button_104.check_click(pygame.mouse.get_pos()):
            button_104 = Button('生物学家vs生物学家', RED, font_button, 300, 260)
        else:
            button_104 = Button('生物学家vs生物学家', BLACK, font_button, 300, 260)
        if button_105.check_click(pygame.mouse.get_pos()):
            button_105 = Button('高中生vs高中生', RED, font_button, 300, 300)
        else:
            button_105 = Button('高中生vs高中生', BLACK, font_button, 300, 300)
        if button_106.check_click(pygame.mouse.get_pos()):
            button_106 = Button('大学生vs大学生', RED, font_button, 300, 340)
        else:
            button_106 = Button('大学生vs大学生', BLACK, font_button, 300, 340)
        if button_107.check_click(pygame.mouse.get_pos()):
            button_107 = Button('神vs神', RED, font_button, 300, 380)
        else:
            button_107 = Button('神vs神', BLACK, font_button, 300, 380)
        if button_108.check_click(pygame.mouse.get_pos()):
            button_108 = Button('神强化vs神强化', RED, font_button, 300, 420)
        else:
            button_108 = Button('神强化vs神强化', BLACK, font_button, 300, 420)
        if button_156.check_click(pygame.mouse.get_pos()):
            button_156 = Button('高中生vs大学生', RED, font_button, 600, 140)
        else:
            button_156 = Button('高中生vs大学生', BLACK, font_button, 600, 140)
        if button_167.check_click(pygame.mouse.get_pos()):
            button_167 = Button('大学生vs神', RED, font_button, 600, 180)
        else:
            button_167 = Button('大学生vs神', BLACK, font_button, 600, 180)
        if button_160.check_click(pygame.mouse.get_pos()):
            button_160 = Button('大学生vs玩家', RED, font_button, 600, 220)
        else:
            button_160 = Button('大学生vs玩家', BLACK, font_button, 600, 220)
        # if button_200.check_click(pygame.mouse.get_pos()):
        #     button_200 = Button('WAN(在server_address.ini中填写服务器地址)', RED, font_button, None, 480, centered_x=True)
        # else:
        #     button_200 = Button('WAN(在server_address.ini中填写服务器地址)', BLACK, font_button, None, 480, centered_x=True)

        screen.blit(curtain, (0, 0))

        button_0.display()
        button_1.display()
        button_2.display()
        button_3.display()
        button_4.display()
        button_5.display()
        button_6.display()
        button_7.display()
        button_8.display()
        button_101.display()
        button_102.display()
        button_103.display()
        button_104.display()
        button_105.display()
        button_106.display()
        button_107.display()
        button_108.display()
        button_156.display()
        button_167.display()
        button_160.display()
        # button_200.display()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONUP:
                if button_0.check_click(pygame.mouse.get_pos()):
                    mode = 0
                    my_color = -1
                    return
                if button_1.check_click(pygame.mouse.get_pos()):
                    mode = 1
                    my_color = 0
                    return
                if button_2.check_click(pygame.mouse.get_pos()):
                    mode = 2
                    my_color = 0
                    return
                if button_3.check_click(pygame.mouse.get_pos()):
                    mode = 3
                    my_color = 0
                    return
                if button_4.check_click(pygame.mouse.get_pos()):
                    mode = 4
                    my_color = 0
                    return
                if button_5.check_click(pygame.mouse.get_pos()):
                    mode = 5
                    my_color = 0
                    return
                if button_6.check_click(pygame.mouse.get_pos()):
                    mode = 6
                    my_color = 0
                    return
                if button_7.check_click(pygame.mouse.get_pos()):
                    mode = 7
                    my_color = 0
                    return
                if button_8.check_click(pygame.mouse.get_pos()):
                    mode = 8
                    my_color = 0
                    return

                if button_101.check_click(pygame.mouse.get_pos()):
                    mode = 101
                    return
                if button_102.check_click(pygame.mouse.get_pos()):
                    mode = 102
                    return
                if button_103.check_click(pygame.mouse.get_pos()):
                    mode = 103
                    return
                if button_104.check_click(pygame.mouse.get_pos()):
                    mode = 104
                    return
                if button_105.check_click(pygame.mouse.get_pos()):
                    mode = 105
                    return
                if button_106.check_click(pygame.mouse.get_pos()):
                    mode = 106
                    return
                if button_107.check_click(pygame.mouse.get_pos()):
                    mode = 107
                    return
                if button_108.check_click(pygame.mouse.get_pos()):
                    mode = 108
                    return

                if button_156.check_click(pygame.mouse.get_pos()):
                    mode = 156
                    return
                if button_167.check_click(pygame.mouse.get_pos()):
                    mode = 167
                    return
                if button_160.check_click(pygame.mouse.get_pos()):
                    mode = 160
                    my_color = 1
                    return

                # if button_200.check_click(pygame.mouse.get_pos()):
                #     mode = 200
                #     with open('server_address.ini') as F:
                #         content = F.read()
                #         url = re.findall(r'http://(.+?).cc', content)
                #         url = 'http://' + url[0] + '.cc'
                #         server_address = url
                #         F.close()
                #     my_color = online_player()
                #     return

        pygame.event.pump()


def paint_present_player():
    if flag:
        screen.blit(pygame.transform.scale(white, (150, 150)), (666, 66))
    else:
        screen.blit(pygame.transform.scale(black, (150, 150)), (666, 66))

def check_event_wait():
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        sys.exit()
    if event.type == KEYDOWN:
        if event.key == K_r and mode != 200:
            init_checkerboard()
            return
        if event.key == K_m:
            select_mode()
            init_checkerboard()
    if event.type == MOUSEBUTTONDOWN:
        check_click()

def check_event_no_wait():
    if win == 1:
        check_event_wait()
        return
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_r and mode != 200:
                init_checkerboard()
                return
            if event.key == K_m:
                select_mode()
                init_checkerboard()

def check_click():
    x, y = pygame.mouse.get_pos()
    m = -1
    n = -1
    for i in range(15):
        if (x >= 5 + i * 40) and (x <= 35 + i * 40):
            m = i
            break
    for i in range(15):
        if (y >= 5 + i * 40) and (y <= 35 + i * 40):
            n = i
            break
    if m != -1 and n != -1:
        placing(n, m)

def placing(n, m):
    global flag, win, step, last_pos

    print(step)
    if step == 225:
        screen.blit(font.render('end in a draw!!!', True, (0, 0, 0)), (625, 300))
        screen.blit(font.render('press R to restart', True, (0, 0, 0)), (620, 380))
        god1.restart()
        god2.restart()
        win = 1
        pygame.display.update()
        return
    if win:
        return
    if (white_list[n][m] == 0) and (black_list[n][m] == 0):

        if flag:
            screen.blit(white, dot_list[15 * m + n])
            screen.blit(pygame.font.SysFont('arial', 20).render('E', True, (255, 0, 0)),
                        (dot_list[15 * m + n][0] + 13, dot_list[15 * m + n][1] + 8))
            if step > 0:
                screen.blit(black, dot_list[15 * last_pos[1] + last_pos[0]])
#                screen.blit(pygame.font.SysFont('arial', 20).render('E', True, (255, 0, 0)),
#                            (dot_list[15 * last_pos[1] + last_pos[0]][0] + 13,
#                             dot_list[15 * last_pos[1] + last_pos[0]][1] + 8))
            last_pos = (n, m)
            white_list[n][m] = 1
            if judge(white_list):
                step += 1
                win = 1
                flag = not flag
                if mode == 200:
                    online_win()
                    if my_color == 1:
                        online_post()
                screen.blit(font.render('white win!!!', True, (0, 0, 0)), (666, 300))
                if mode != 200:
                    screen.blit(font.render('press R to restart', True, (0, 0, 0)), (620, 380))
                god1.restart()
                god2.restart()
                pygame.display.update()
                return
        else:
            screen.blit(black, dot_list[15 * m + n])
            screen.blit(pygame.font.SysFont('arial', 20).render('E', True, (255, 0, 0)),
                        (dot_list[15 * m + n][0] + 13, dot_list[15 * m + n][1] + 8))
            if step > 0:
                screen.blit(white, dot_list[15 * last_pos[1] + last_pos[0]])
                # screen.blit(pygame.font.SysFont('arial', 20).render('E', True, (255, 0, 0)),
                #             (dot_list[15 * last_pos[1] + last_pos[0]][0] + 13,
                #              dot_list[15 * last_pos[1] + last_pos[0]][1] + 8))
            last_pos = (n, m)
            black_list[n][m] = 1
            if judge(black_list):
                step += 1
                win = 1
                flag = not flag
                if mode == 200:
                    online_win()
                    if my_color == 0:
                        online_post()
                screen.blit(font.render('black win!!!', True, (0, 0, 0)), (666, 300))
                if mode != 200:
                    screen.blit(font.render('press R to restart', True, (0, 0, 0)), (620, 380))
                god1.restart()
                god2.restart()
                pygame.display.update()
                return

        flag = not flag
        step += 1

        paint_present_player()
        pygame.display.update()
        pygame.event.pump()

def judge(piece_list):
    global win
    for i in range(11):
        for j in range(11):
            if (piece_list[i][j] == 1) \
                    and (piece_list[i + 1][j + 1] == 1) \
                    and (piece_list[i + 2][j + 2] == 1) \
                    and (piece_list[i + 3][j + 3] == 1) \
                    and (piece_list[i + 4][j + 4] == 1):
                win = 1
                return 1
            if (piece_list[i + 4][j] == 1) \
                    and (piece_list[i + 3][j + 1] == 1) \
                    and (piece_list[i + 2][j + 2] == 1) \
                    and (piece_list[i + 1][j + 3] == 1) \
                    and (piece_list[i][j + 4] == 1):
                win = 1
                return 1
    for i in range(11):
        for j in range(15):
            if (piece_list[i][j] == 1) \
                    and (piece_list[i + 1][j] == 1) \
                    and (piece_list[i + 2][j] == 1) \
                    and (piece_list[i + 3][j] == 1) \
                    and (piece_list[i + 4][j] == 1):
                win = 1
                return 1
            if (piece_list[j][i] == 1) \
                    and (piece_list[j][i + 1] == 1) \
                    and (piece_list[j][i + 2] == 1) \
                    and (piece_list[j][i + 3] == 1) \
                    and (piece_list[j][i + 4] == 1):
                win = 1
                return 1
    return 0

def rob_random():
    n = randint(0, 14)
    m = randint(0, 14)
    while True:
        if (white_list[n][m] == 0) and (black_list[n][m] == 0):
            placing(n, m)
            return
        n = randint(0, 14)
        m = randint(0, 14)

def rob_assess_each_point():
    n = -1
    m = -1
    max_score = -10000
    for i in range(15):
        for j in range(15):
            if (white_list[i][j] == 0) and (black_list[i][j] == 0):
                s, k = assess(i, j)
                score = s[0] * 100 + s[1] * 60 + s[2] * 33 + s[3] * 5 - k[0] * 130 - k[1] * 60 - k[2] * 20 - k[3] * 3
                if score > max_score:
                    max_score = score
                    n = i
                    m = j
    placing(n, m)

def assess(n, m):
    s = [0, 0, 0, 0]
    k = [0, 0, 0, 0]
    for i in range(8):
        for j in range(4):
            row = [n - j - 1, n - j - 1, n, n + j + 1, n + j + 1, n + j + 1, n, n - j - 1]
            line = [m, m + j + 1, m + j + 1, m + j + 1, m, m - j - 1, m - j - 1, m - j - 1]
            if 0 < row[i] < 15 and 0 < line[i] < 15:
                if flag:
                    if white_list[row[i]][line[i]] == 1:
                        s[j] += 1
                    if black_list[row[i]][line[i]] == 1:
                        k[j] += 1
                else:
                    if white_list[row[i]][line[i]] == 1:
                        k[j] += 1
                    if black_list[row[i]][line[i]] == 1:
                        s[j] += 1
            else:
                k[j] += 1
    return s, k

def rob_normal():
    global white_list, black_list, flag
    n = -1
    m = -1
    max_score = -1000000000
    score = 0
    for i in range(15):
        for j in range(15):
            if (white_list[i][j] == 0) and (black_list[i][j] == 0):
                if flag:
                    white_list[i][j] = 1
                else:
                    black_list[i][j] = 1
                detect()
                self_live_5 = live_5
                self_live_4 = live_4
                self_sleep_4 = sleep_4
                self_live_3 = live_3
                self_sleep_3 = sleep_3
                self_live_2 = live_2
                self_sleep_2 = sleep_2
                flag = not flag
                detect()
                rival_live_5 = live_5
                rival_live_4 = live_4
                rival_sleep_4 = sleep_4
                rival_live_3 = live_3
                rival_sleep_3 = sleep_3
                rival_live_2 = live_2
                rival_sleep_2 = sleep_2
                flag = not flag
                if flag:
                    white_list[i][j] = 0
                else:
                    black_list[i][j] = 0
                if self_live_5 >= 1:
                    placing(i, j)
                    return
                score = self_live_5 * 10000 + \
                        self_live_4 * 3000 + \
                        self_sleep_4 * 600 + \
                        self_live_3 * 300 + \
                        self_sleep_3 * 40 + \
                        self_live_2 * 4 + \
                        self_sleep_2 * 1 - \
                        rival_live_5 * 99999 - \
                        rival_live_4 * 9000 - \
                        rival_sleep_4 * 7000 - \
                        rival_live_3 * 700 - \
                        rival_sleep_3 * 90 - \
                        rival_live_2 * 5 - \
                        rival_sleep_2 * 2
                if score > max_score:
                    max_score = score
                    n = i
                    m = j
                    o_self_live_5 = self_live_5
                    o_self_live_4 = self_live_4
                    o_self_sleep_4 = self_sleep_4
                    o_self_live_3 = self_live_3
                    o_self_sleep_3 = self_sleep_3
                    o_self_live_2 = self_live_2
                    o_self_sleep_2 = self_sleep_2
                    o_rival_live_5 = rival_live_5
                    o_rival_live_4 = rival_live_4
                    o_rival_sleep_4 = rival_sleep_4
                    o_rival_live_3 = rival_live_3
                    o_rival_sleep_3 = rival_sleep_3
                    o_rival_live_2 = rival_live_2
                    o_rival_sleep_2 = rival_sleep_2
    print('score:', max_score)
    print(o_self_live_5, o_self_live_4, o_self_sleep_4, o_self_live_3, o_self_sleep_3, o_self_live_2, o_self_sleep_2)
    print(o_rival_live_5, o_rival_live_4, o_rival_sleep_4, o_rival_live_3, o_rival_sleep_3, o_rival_live_2,
          o_rival_sleep_2)
    if score == 0:
        n = randint(5, 9)
        m = randint(5, 9)
        while True:
            if (white_list[n][m] == 0) and (black_list[n][m] == 0):
                placing(n, m)
                return
            n = randint(5, 9)
            m = randint(5, 9)
    placing(n, m)

def detect():
    global live_5, live_4, sleep_4, live_3, sleep_3, live_2, sleep_2
    if flag:
        self_list = white_list
        rival_list = black_list
    else:
        self_list = black_list
        rival_list = white_list
    present_list = np.zeros((15, 15), dtype=int)
    for i in range(15):
        for j in range(15):
            present_list[i][j] = self_list[i][j]
            if rival_list[i][j] == 1:
                present_list[i][j] = -1
    live_5, live_4, sleep_4, live_3, sleep_3, live_2, sleep_2 = 0, 0, 0, 0, 0, 0, 0
    for i in range(15):
        analyse_line_1 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        analyse_line_2 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        for j in range(15):
            analyse_line_1[j + 1] = present_list[i][j]
            analyse_line_2[j + 1] = present_list[j][i]
        analyse(analyse_line_1, 15)
        analyse(analyse_line_2, 15)
    for i in range(4, 15):
        analyse_line_3 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        analyse_line_4 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        for j in range(i + 1):
            analyse_line_3[j + 1] = present_list[i - j][j]
            analyse_line_4[j + 1] = present_list[i - j][14 - j]
        analyse(analyse_line_3, i + 1)
        analyse(analyse_line_4, i + 1)
    for i in range(4, 14):
        analyse_line_5 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        analyse_line_6 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        for j in range(i + 1):
            analyse_line_5[j + 1] = present_list[14 - i + j][14 - j]
            analyse_line_6[j + 1] = present_list[14 - i + j][j]
        analyse(analyse_line_5, i + 1)
        analyse(analyse_line_6, i + 1)

def analyse(analyse_line, analyse_bits):
    global live_5, live_4, sleep_4, live_3, sleep_3, live_2, sleep_2
    if analyse_bits - 2 <= 0:
        return
    for i in range(analyse_bits - 2):
        if analyse_line[i] == 1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1:
            live_5 += 1
            return
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1:
            sleep_4 += 1
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1:
            sleep_4 += 1
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1:
            sleep_4 += 1
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1:
            sleep_3 += 1
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1:
            sleep_3 += 1
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1:
            sleep_3 += 1
        elif analyse_line[i] == 1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1:
            sleep_2 += 1
    if analyse_bits - 3 <= 0:
        return
    for i in range(analyse_bits - 3):
        if analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            live_4 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_4 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            sleep_4 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            live_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            live_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_3 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 0 and \
                analyse_line[i + 5] == 0:
            sleep_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_3 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            sleep_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_3 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            sleep_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 0 and \
                analyse_line[i + 5] == 0:
            live_2 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            live_2 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_2 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_2 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == -1:
            sleep_2 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 0 and \
                analyse_line[i + 5] == 0:
            sleep_2 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 0 and \
                analyse_line[i + 5] == 0:
            sleep_2 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 1 and \
                analyse_line[i + 2] == 0 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0:
            sleep_2 += 1
    if analyse_bits - 4 <= 0:
        return
    for i in range(analyse_bits - 4):
        if analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == 0:
            live_3 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == 0:
            live_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == -1:
            live_3 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 1 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == -1:
            sleep_3 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == 0:
            live_2 += 1
        elif analyse_line[i] == -1 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == 0:
            live_2 += 1
        elif analyse_line[i] == 0 and \
                analyse_line[i + 1] == 0 and \
                analyse_line[i + 2] == 1 and \
                analyse_line[i + 3] == 0 and \
                analyse_line[i + 4] == 1 and \
                analyse_line[i + 5] == 0 and \
                analyse_line[i + 6] == -1:
            live_2 += 1

def rob_ga():
    if step <= 1:
        n = randint(5, 9)
        m = randint(5, 9)
        while True:
            if (white_list[n][m] == 0) and (black_list[n][m] == 0):
                placing(n, m)
                return
            n = randint(5, 9)
            m = randint(5, 9)
    ga = GA(func=ga_problem, n_dim=2, size_pop=10, max_iter=10, lb=[0, 0], ub=[14, 14], precision=[1, 1])
    ga.register(operator_name='ranking', operator=ranking.ranking). \
        register(operator_name='crossover', operator=crossover.crossover_2point). \
        register(operator_name='mutation', operator=mutation.mutation)
    best_pos, best_score = ga.run()
    print('best_pos:', best_pos, 'best_score:', -best_score)
    placing(int(best_pos[0]), int(best_pos[1]))

def ga_problem(x):
    global flag
    i = int(x[0])
    j = int(x[1])
    if i < 0 or i >= 15 or j < 0 or j >= 15:
        return 1000000
    if (white_list[i][j] == 0) and (black_list[i][j] == 0):
        if flag:
            white_list[i][j] = 1
        else:
            black_list[i][j] = 1
        detect()
        self_live_5 = live_5
        self_live_4 = live_4
        self_sleep_4 = sleep_4
        self_live_3 = live_3
        self_sleep_3 = sleep_3
        self_live_2 = live_2
        self_sleep_2 = sleep_2
        flag = not flag
        detect()
        rival_live_5 = live_5
        rival_live_4 = live_4
        rival_sleep_4 = sleep_4
        rival_live_3 = live_3
        rival_sleep_3 = sleep_3
        rival_live_2 = live_2
        rival_sleep_2 = sleep_2
        flag = not flag
        if flag:
            white_list[i][j] = 0
        else:
            black_list[i][j] = 0
        score = self_live_5 * 10000 + \
                self_live_4 * 3000 + \
                self_sleep_4 * 600 + \
                self_live_3 * 300 + \
                self_sleep_3 * 40 + \
                self_live_2 * 4 + \
                self_sleep_2 * 1 - \
                rival_live_5 * 99999 - \
                rival_live_4 * 9000 - \
                rival_sleep_4 * 7000 - \
                rival_live_3 * 700 - \
                rival_sleep_3 * 90 - \
                rival_live_2 * 5 - \
                rival_sleep_2 * 2
        return -score
    else:
        return 1000000

def rob_fast():
    if step == 0:
        n = randint(5, 9)
        m = randint(5, 9)
        while True:
            if (white_list[n][m] == 0) and (black_list[n][m] == 0):
                placing(n, m)
                return
            n = randint(5, 9)
            m = randint(5, 9)
    n = -1
    m = -1
    max_score = -1000000000
    for i in range(15):
        for j in range(15):
            if (white_list[i][j] == 0) and (black_list[i][j] == 0):
                score = detect_around(i, j)
                if score > max_score:
                    max_score = score
                    n = i
                    m = j
                elif score == max_score and score > 0:
                    r = randint(0, 100)
                    if r % 2 == 0:
                        n = i
                        m = j
    print(n, m, 'score:', max_score)
    placing(n, m)

def detect_around(n, m):
    score = 0
    offset = [(1, 0), (0, 1), (1, 1), (1, -1)]
    if flag:
        self_list = white_list
        rival_list = black_list
    else:
        self_list = black_list
        rival_list = white_list
    present_list = np.zeros((15, 15), dtype=int)
    for i in range(15):
        for j in range(15):
            present_list[i][j] = self_list[i][j]
            if rival_list[i][j] == 1:
                present_list[i][j] = 2
    for pos in offset:
        score += get_direction_score(present_list, n, m, pos[0], pos[1])
    return score

def get_direction_score(present_list, n, m, x_offset, y_offset):
    self_count = 0
    rival_count = 0
    self_space = None
    rival_space = None
    self_both = 0
    rival_both = 0
    which = get_stone_color(present_list, n, m, x_offset, y_offset, True)
    if which != 0:
        for lens in range(1, 6):
            x = n + lens * x_offset
            y = m + lens * y_offset
            if 0 <= x < 15 and 0 <= y < 15:
                if which == 1:
                    if present_list[x][y] == 1:
                        self_count += 1
                        if self_space is False:
                            self_space = True
                    elif present_list[x][y] == 2:
                        rival_both += 1
                        break
                    else:
                        if self_space is None:
                            self_space = False
                        else:
                            break
                elif which == 2:
                    if present_list[x][y] == 1:
                        rival_both += 1
                        break
                    elif present_list[x][y] == 2:
                        rival_count += 1
                        if rival_space is False:
                            rival_space = True
                    else:
                        if rival_space is None:
                            rival_space = False
                        else:
                            break
            else:
                if which == 1:
                    self_both += 1
                elif which == 2:
                    rival_both += 1

    if self_space is False:
        self_space = None
    if rival_space is False:
        rival_space = None
    which = get_stone_color(present_list, n, m, -x_offset, -y_offset, True)
    if which != 0:
        for lens in range(1, 6):
            x = n - lens * x_offset
            y = m - lens * y_offset
            if 0 <= x < 15 and 0 <= y < 15:
                if which == 1:
                    if present_list[x][y] == 1:
                        self_count += 1
                        if self_space is False:
                            self_space = True
                    elif present_list[x][y] == 2:
                        rival_both += 1
                        break
                    else:
                        if self_space is None:
                            self_space = False
                        else:
                            break
                elif which == 2:
                    if present_list[x][y] == 1:
                        rival_both += 1
                        break
                    elif present_list[x][y] == 2:
                        rival_count += 1
                        if rival_space is False:
                            rival_space = True
                    else:
                        if rival_space is None:
                            rival_space = False
                        else:
                            break
            else:
                if which == 1:
                    self_both += 1
                elif which == 2:
                    rival_both += 1
    if self_count == 4:
        score = 10000
    elif rival_count == 4:
        score = 9000
    elif self_count == 3:
        if self_both == 0:
            score = 1000
        elif self_both == 1:
            score = 100
        else:
            score = 0
    elif rival_count == 3:
        if rival_both == 0:
            score = 900
        elif rival_both == 1:
            score = 90
        else:
            score = 0
    elif self_count == 2:
        if self_both == 0:
            score = 100
        elif self_both == 1:
            score = 10
        else:
            score = 0
    elif rival_count == 2:
        if rival_both == 0:
            score = 90
        elif rival_both == 1:
            score = 9
        else:
            score = 0
    elif self_count == 1:
        score = 10
    elif rival_count == 1:
        score = 9
    else:
        score = 0
    if self_space or rival_space:
        score /= 2
    return score

def get_stone_color(present_list, n, m, x_offset, y_offset, next):
    x = n + x_offset
    y = m + y_offset
    if 0 <= x < 15 and 0 <= y < 15:
        if present_list[x][y] == 1:
            return 1
        elif present_list[x][y] == 2:
            return 2
        else:
            if next:
                return get_stone_color(present_list, x, y, x_offset, y_offset, False)
            else:
                return 0
    else:
        return 0

AA = [(int(i / 5) - 2, int(i % 5) - 2) for i in range(25)]
DEP = 1

class HardAi:
    def __init__(self):
        file = open('Resource/Data/policy.csv', 'r')
        self.state_score = json.loads(file.read())
        file.close()

    def next(self, player, board):
        houxuanBoard = [[0 for j in range(15)] for i in range(15)]
        for row in range(15):
            for col in range(15):
                if board[row][col] == player:
                    board[row][col] = 1
                if board[row][col] == 3 - player:
                    board[row][col] = 2
                for aa in AA:
                    if self._hefa(row + aa[0], col + aa[1]):
                        houxuanBoard[row][col] += 1 if board[row + aa[0]][col + aa[1]] > 0 else 0
        score = 0
        for i in range(15):
            score += self._row_score(board, i, 0) - self._row_score(board, i, 0, rev=True)
            score += self._col_score(board, 0, i) - self._col_score(board, 0, i, rev=True)

        score += self._rd_score(board, 0, 0) - self._rd_score(board, 0, 0, rev=False)
        for i in range(1, 15):
            score += self._rd_score(board, i, 0) - self._rd_score(board, i, 0, rev=False)
            score += self._rd_score(board, 0, i) - self._rd_score(board, 0, i, rev=False)

        score += self._ru_score(board, 14, 0) - self._ru_score(board, 14, 0, rev=False)
        for i in range(0, 14):
            score += self._ru_score(board, i, 0) - self._ru_score(board, i, 0, rev=False)
        for i in range(1, 15):
            score += self._ru_score(board, 14, i) - self._rd_score(board, 14, i, rev=False)

        pos, minmax = self.search(board, houxuanBoard, score, 0)
        return pos

    def _hefa(self, x, y):
        if x < 0 or x >= 15 or y < 0 or y >= 15:
            return False
        return True

    # def _value(self,board):

    def _rev(self, a):
        if a == 0:
            return 0
        return 3 - a

    def _row_score(self, board, row, col, rev=False):
        ret = 0
        if rev:
            for col in range(15):
                ret = ret * 3 + self._rev(board[row][col])
        else:
            for col in range(15):
                ret = ret * 3 + board[row][col]
        return self.state_score[ret]

    def _col_score(self, board, row, col, rev=False):
        ret = 0
        if rev:
            for row in range(15):
                ret = ret * 3 + self._rev(board[row][col])
        else:
            for row in range(15):
                ret = ret * 3 + board[row][col]
        return self.state_score[ret]

    def _rd_score(self, board, row, col, rev=False):
        ret = 0
        m = min(row, col)
        row -= m
        col -= m
        cnt = 0
        if rev:
            while row < 15 and col < 15:
                ret = ret * 3 + self._rev(board[row][col])
                row += 1
                col += 1
                cnt += 1
        else:
            while row < 15 and col < 15:
                ret = ret * 3 + board[row][col]
                row += 1
                col += 1
                cnt += 1
        while cnt < 15:
            ret = ret * 3 + 2
            cnt += 1
        return self.state_score[ret]

    def _ru_score(self, board, row, col, rev=False):
        ret = 0
        m = min(col, 14 - row)
        col -= m
        row += m
        cnt = 0
        if rev:
            while row >= 0 and col < 15:
                ret = ret * 3 + self._rev(board[row][col])
                row -= 1
                col += 1
                cnt += 1
        else:
            while row >= 0 and col < 15:
                ret = ret * 3 + board[row][col]
                row -= 1
                col += 1
                cnt += 1
        while cnt < 15:
            ret = ret * 3 + 2
            cnt += 1
        return self.state_score[ret]

    def _delta_score(self, board, row, col):
        score = 0
        score += self._row_score(board, row, col) - self._row_score(board, row, col, rev=True)
        score += self._col_score(board, row, col) - self._col_score(board, row, col, rev=True)
        score += self._rd_score(board, row, col) - self._rd_score(board, row, col, rev=True)
        score += self._ru_score(board, row, col) - self._ru_score(board, row, col, rev=True)
        return score

    def search(self, board, houxuanBoard, score, dep):
        if dep >= DEP:
            return None, score

        pos = (0, 0)
        minmax = -100000 if dep % 2 == 0 else 100000
        for row in range(15):
            for col in range(15):
                if board[row][col] == 0 and houxuanBoard[row][col] > 0:
                    old_delta_score = self._delta_score(board, row, col)
                    board[row][col] = 1
                    new_delta_score = self._delta_score(board, row, col)
                    for aa in AA:
                        if self._hefa(row + aa[0], col + aa[1]):
                            houxuanBoard[row + aa[0]][col + aa[1]] += 1
                    sub_pos, val = self.search(board, houxuanBoard, score + new_delta_score - old_delta_score,
                                               dep + 1)
                    if dep % 2 == 0:
                        if val > minmax:
                            pos = (row, col)
                            minmax = val
                    else:
                        if val < minmax:
                            pos = (row, col)
                            minmax = val

                    board[row][col] = 0
                    for aa in AA:
                        if self._hefa(row + aa[0], col + aa[1]):
                            houxuanBoard[row + aa[0]][col + aa[1]] -= 1
        return pos, minmax

rob_hard_ai = HardAi()


def rob_hard():
    if flag:
        self_list = white_list
        rival_list = black_list
    else:
        self_list = black_list
        rival_list = white_list
    present_list = np.zeros((15, 15), dtype=int)
    for i in range(15):
        for j in range(15):
            if rival_list[i][j] == 1:
                present_list[i][j] = 2
                continue
            if self_list[i][j] == 1:
                present_list[i][j] = 1

    pos = rob_hard_ai.next(1, present_list)
    print(pos)
    placing(pos[0], pos[1])

class YiXin:
    def __init__(self):
        startupinfo = sub.STARTUPINFO()
        startupinfo.dwFlags = sub.CREATE_NEW_CONSOLE | sub.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = sub.SW_HIDE
        self.mYixin = sub.Popen('Resource/Plugin/Yixin.exe', stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE,
                                startupinfo=startupinfo)
        self.input('START 15')
        self.input('INFO timeout_match 0')
        self.input('INFO timeout_turn 0')  # 控制思考快慢
        self.output()

    def input(self, str):
        if ',' in str:
            print('Human: ' + str[5:])
        self.mYixin.stdin.write((str + '\n').encode())
        self.mYixin.stdin.flush()

    def output(self):
        while True:
            str = bytes.decode(self.mYixin.stdout.readline())
            if (',' in str) or ('OK' in str):
                break
        self.mYixin.stdout.flush()
        if ',' in str:
            print('God: ' + str, end='')
            return str

    def restart(self):
        self.input('RESTART 15')
        self.output()

god1 = YiXin()
god2 = YiXin()

def rob_niubility(god):
    if step == 0:
        god.input('BEGIN')
    else:
        god.input('TURN %s,%s' % (str(last_pos[0]), str(last_pos[1])))
    pos = god.output()
    a = pos.find(',')
    b = pos.find('\r')
    pos = (int(pos[0:a]), int(pos[a + 1:b]))
    placing(pos[0], pos[1])


def rob_niubility_ex(god):
    if step == 0 or step == 1:
        god.input('INFO timeout_turn 10000')
    if step == 0:
        god.input('BEGIN')
    else:
        god.input('TURN %s,%s' % (str(last_pos[0]), str(last_pos[1])))
    pos = god.output()
    a = pos.find(',')
    b = pos.find('\r')
    pos = (int(pos[0:a]), int(pos[a + 1:b]))
    placing(pos[0], pos[1])


def online_player():
    cnt = 0
    while True:
        cnt += 1
        data = {'identity': 'yaorelax'}
        r = requests.post(server_address + '/player', data)
        if r.text.startswith('<!DOCTYPE html>'):
            if cnt == 3:
                exit()
            screen.blit(font_chs.render('服务器地址错误或服务器未启动，尝试连接', True, (0, 0, 0)), (100, 500))
            pygame.display.update()
            print('join failure')
            time.sleep(5)
        elif r.text.startswith('full'):
            screen.blit(font_chs.render('人满了！', True, (0, 0, 0)), (100, 500))
            pygame.display.update()
            print('full')
            time.sleep(5)
            exit()
        else:
            break
    return int(r.text)

def online_post():
    data = {'identity': 'yaorelax', 'step': step - 1, 'n': last_pos[0], 'm': last_pos[1]}
    while True:
        r = requests.post(server_address + '/post', data)
        if r.text.startswith('<!DOCTYPE html'):
            print('post failure without connection', data)
            time.sleep(5)
        elif r.text.startswith('failure'):
            print('post multiple', data)
            break
        else:
            break

def online_get():
    data = {'identity': 'yaorelax', 'step': step}
    while True:
        r = requests.post(server_address + '/get', data)
        if r.text.startswith('<!DOCTYPE html'):
            print('get failure without connection')
            time.sleep(5)
        elif r.text.startswith('failure'):
            print('get failure without step')
            time.sleep(3)
        else:
            break
    pos = eval(r.text)
    n = pos['n']
    m = pos['m']
    placing(int(n), int(m))

def online_win():
    while True:
        data = {'identity': 'yaorelax'}
        r = requests.post(server_address + '/win', data)
        if r.text.startswith('<!DOCTYPE html>'):
            print('win failure')
            time.sleep(5)
        else:
            break


def local_server():
    pass

def local_client():
    pass

def main():
    start_up()
    welcome()
    select_mode()
    init_checkerboard()
    while True:
        if mode == 101:
            check_event_no_wait()
            rob_random()
        elif mode == 102:
            check_event_no_wait()
            rob_assess_each_point()
        elif mode == 103:
            check_event_no_wait()
            rob_normal()
        elif mode == 104:
            check_event_no_wait()
            rob_ga()
        elif mode == 105:
            check_event_no_wait()
            rob_fast()
        elif mode == 106:
            check_event_no_wait()
            rob_hard()
        elif mode == 107:
            check_event_no_wait()
            rob_niubility(god1)
            rob_niubility(god2)
        elif mode == 108:
            check_event_no_wait()
            rob_niubility_ex(god1)
            rob_niubility_ex(god2)
        elif mode == 156:
            check_event_no_wait()
            rob_fast()
            rob_hard()
        elif mode == 167:
            check_event_no_wait()
            rob_hard()
            rob_niubility(god1)
        elif mode == 160:
            if not flag:
                rob_niubility_ex(god1)
            check_event_wait()
        elif mode == 200:
            if my_color == 0:
                check_event_wait()
                if flag and (not win):
                    online_post()
                    online_get()
            elif my_color == 1:
                if not flag:
                    if step > 0 and (not win):
                        online_post()
                        print('post in <main>')
                    if not win:
                        online_get()
                check_event_wait()
        else:
            check_event_wait()
            if flag:
                if mode == 0:
                    pass
                elif mode == 1:
                    rob_random()
                elif mode == 2:
                    rob_assess_each_point()
                elif mode == 3:
                    rob_normal()
                elif mode == 4:
                    rob_ga()
                elif mode == 5:
                    rob_fast()
                elif mode == 6:
                    rob_hard()
                elif mode == 7:
                    rob_niubility(god1)
                elif mode == 8:
                    rob_niubility_ex(god1)

if __name__ == '__main__':
    main()
