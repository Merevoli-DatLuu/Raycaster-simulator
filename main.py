import pygame
import math
from pygame.locals import *
import sys

pygame.init()

SIZE = WIDTH, HEIGHT = 960, 480
SIZE_MAP = (12, 12)
BLOCK_SIZE = WIDTH//(2*SIZE_MAP[0])
LINE_WEIGHT = 1
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

screen = pygame.display.set_mode(SIZE)


class ScreenMap():
    def __init__(self):
        self.block_map = [[0 for i in range(SIZE_MAP[0])] for l in range(SIZE_MAP[0])]
        self.height_unit = 100

    def check_pos(self, pos):
        block_x, block_y = pos[0]//BLOCK_SIZE, pos[1]//BLOCK_SIZE

        return  0 <= block_x < SIZE_MAP[0] and \
                0 <= block_y < SIZE_MAP[1] and \
                self.block_map[block_x][block_y]

    def render(self):
        pygame.draw.line(screen, white, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

        for row in range(len(self.block_map)):
            for col in range(len(self.block_map[row])):
                if self.block_map[col][row]:
                    pygame.draw.rect(
                        screen, 
                        black, 
                        (
                            col*BLOCK_SIZE, 
                            row*BLOCK_SIZE, 
                            BLOCK_SIZE, 
                            BLOCK_SIZE
                        )
                    )

                    pygame.draw.rect(
                        screen, 
                        white, 
                        (
                            col*BLOCK_SIZE + LINE_WEIGHT, 
                            row*BLOCK_SIZE + LINE_WEIGHT, 
                            BLOCK_SIZE - 2*LINE_WEIGHT, 
                            BLOCK_SIZE - 2*LINE_WEIGHT
                        )
                )

    def update(self):
        click = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if click != (0, 0, 0) and mouse_pos[0] <= WIDTH//2 - 1:
            block_x, block_y = mouse_pos[0]//BLOCK_SIZE, mouse_pos[1]//BLOCK_SIZE
            if click[0]:
                self.block_map[block_x][block_y] = 1
            if click[2]:
                self.block_map[block_x][block_y] = 0

        self.render()

class ViewPoint():

    def __init__(self, pos):
        self.pos = pos
        self.angel_of_straight_edge = 0
        self.angel_of_view = 60
        self.num_line = 40
        self.point_size = 6
        self.distance = 5*WIDTH//(SIZE_MAP[0]*2)
        self.moves = {
            K_a: [-1, 0],
            K_w: [0, -1],
            K_d: [1, 0],
            K_s: [0, 1]
        }

    def distance_2_point(self, point_1, point_2):
        return math.sqrt((point_1[0] - point_2[0])**2 + (point_1[1] - point_2[1])**2)

    def render_line(self, angel):
        angel += self.angel_of_straight_edge
        p = math.tan(angel/180*math.pi)
        vec_y = math.sqrt(self.distance**2/(p**2 + 1))
        if 90 < angel <= 270:
            vec_y = - vec_y
        vec_x = vec_y*p

        # pygame.draw.line(screen, white, self.pos, (self.pos[0] + vec_x, self.pos[1] - vec_y), 1)

        # TODO: Limit wall

        vec_max = int(max(abs(vec_x), abs(vec_y)))
        flag = True
        re_pos = ()
        for i in range(1, vec_max + 1):
            re_pos = (self.pos[0] + int(vec_x*i/vec_max), self.pos[1] - int(vec_y*i/vec_max))
            if screen_map.check_pos(re_pos):
                pygame.draw.circle(screen, (255, 0, 0), re_pos, 3)
                pygame.draw.line(screen, white, self.pos, re_pos, 1)
                flag = False
                break

        if flag:
            pygame.draw.line(screen, white, self.pos, (self.pos[0] + vec_x, self.pos[1] - vec_y), 1)

        if flag == False:
            length_line = self.distance/self.distance_2_point(self.pos, re_pos)*screen_map.height_unit
            distance_line = (WIDTH//2)*(angel - self.angel_of_straight_edge)//(self.angel_of_view)
            pygame.draw.line(
                screen, 
                white, 
                (WIDTH//4 + WIDTH//2 + distance_line, HEIGHT//2 - length_line//2), 
                (WIDTH//4 + WIDTH//2 + distance_line, HEIGHT//2 + length_line//2)
            )

    def render(self):
        pygame.draw.circle(screen, white, self.pos, self.point_size)

        self.render_line(0)
        for angel in range(1, self.num_line//2 + 1):
            self.render_line(angel*self.angel_of_view/self.num_line)
            self.render_line(-angel*self.angel_of_view/self.num_line)

    def update(self):
        key = pygame.key.get_pressed()

        for k in self.moves.keys():
            if key[k]:
                re_pos = (self.pos[0] + self.moves[k][0], self.pos[1] + self.moves[k][1])
                if  not (screen_map.check_pos((re_pos[0] - self.point_size, re_pos[1])) or
                    screen_map.check_pos((re_pos[0], re_pos[1] - self.point_size)) or
                    screen_map.check_pos((re_pos[0] + self.point_size, re_pos[1])) or
                    screen_map.check_pos((re_pos[0], re_pos[1] + self.point_size))
                    ) and\
                    (
                        re_pos[0] - self.point_size >= 0 and
                        re_pos[0] + self.point_size < WIDTH//2 - 1 and
                        re_pos[1] - self.point_size >= 0 and
                        re_pos[1] + self.point_size < HEIGHT
                    ):
                    self.pos = re_pos

        if key[K_q]:
            self.angel_of_straight_edge = (self.angel_of_straight_edge-1)%360
        elif key[K_e]:
            self.angel_of_straight_edge = (self.angel_of_straight_edge+1)%360

        mouse_pos = pygame.mouse.get_pos()
        vec_x = mouse_pos[0] - self.pos[0]
        vec_y = mouse_pos[1] - self.pos[1]

        if vec_x == 0:
            if vec_y > 0:
                new_angel_of_root = 180
            else:
                new_angel_of_root = 0

        elif vec_y == 0:
            if vec_x > 0:
                new_angel_of_root = 90
            else:
                new_angel_of_root = 270
    
        else:   
            new_angel_of_root = math.atan(vec_y/vec_x)*180/math.pi + 90
            if vec_x < 0:
                new_angel_of_root = 180 + new_angel_of_root

        self.angel_of_straight_edge = new_angel_of_root
        
        self.render()

flag = True
screen_map = ScreenMap()
view_point = ViewPoint((0, 0))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
    
    
    click = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if click[1] and flag:
        view_point = ViewPoint(mouse_pos)
        flag = False

    screen.fill(black)
    screen_map.update()

    if not flag:
        view_point.update()
    pygame.display.flip()