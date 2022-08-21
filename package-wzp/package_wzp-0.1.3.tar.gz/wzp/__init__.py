import pygame
import requests
import json
from pygame.locals import *
import sys

def hello():
    print('hello world')

def game():
    FPS = 30
    WINDOWWIDTH = 700
    WINDOWHEIGHT = 700
    BOXSIZE = 12
    BOARDWIDTH = 50
    BOARDHEIGHT = 50

    XMARGIN = (WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2
    YMARGIN = (WINDOWHEIGHT - BOARDHEIGHT * BOXSIZE) / 2

    #               R    G    B
    WHITE = (255, 255, 255)
    GRAY = (185, 185, 185)
    BLACK = (0, 0, 0)
    RED = (155, 0, 0)
    LIGHTRED = (175, 20, 20)
    GREEN = (0, 255, 127)
    LIGHTGREEN = (20, 175, 20)
    BLUE = (0, 255, 255)
    LIGHTBLUE = (20, 20, 175)
    YELLOW = (255, 153, 18)
    LIGHTYELLOW = (175, 175, 20)
    BUTTON = (210, 105, 30)

    BGCOLOR = YELLOW
    BOXCOLOR = YELLOW

    def DrawBoard():
        playerSurf = BIGFONT.render(player, 1, BLACK)
        playerRect = playerSurf.get_rect()
        if player == 'A':
            playerRect.topleft = (0, 0)
        else:
            playerRect.topright = (WINDOWWIDTH, 0)
        DISPLAYSURF.blit(playerSurf, playerRect)
        for y in range(len(board)):
            for x in range(len(board)):
                if x != (len(board) - 1) and y != (len(board) - 1):
                    location = (XMARGIN + BOARDWIDTH * x, YMARGIN + BOARDHEIGHT * y, BOARDWIDTH, BOARDHEIGHT)
                    pygame.draw.rect(DISPLAYSURF, BLACK, location, 1)
                if board[y][x] == 1:
                    pygame.draw.circle(DISPLAYSURF, BLACK, (XMARGIN + BOARDWIDTH * x, YMARGIN + BOARDHEIGHT * y), 20)
                elif board[y][x] == 0:
                    pygame.draw.circle(DISPLAYSURF, WHITE, (XMARGIN + BOARDWIDTH * x, YMARGIN + BOARDHEIGHT * y), 20)

    def generatebooard():
        board = []
        for x in range(BOXSIZE + 1):
            xboard = []
            for y in range(BOXSIZE + 1):
                xboard.append(-1)
            board.append(xboard)
        return board

    def game_waiting():
        startsurf = BIGFONT.render('Start', True, BLACK)
        startrect = startsurf.get_rect()
        startrect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2 + 100))
        x, y = pygame.mouse.get_pos()
        if 300 < x < 400 and 420 < y < 480:
            pygame.draw.rect(DISPLAYSURF, BUTTON, (275, 420, 150, 60), 30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP and 300 < x < 400 and 420 < y < 480:
                return 1

        DISPLAYSURF.blit(startsurf, startrect)
        return 0

    def game_running():
        global player, game_status
        DISPLAYSURF.fill(BGCOLOR)
        DrawBoard()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if ((x - XMARGIN) % BOARDWIDTH < 15 or (x - XMARGIN) % BOARDWIDTH > 45) and (
                        (y - YMARGIN) % BOARDHEIGHT < 15 or (y - YMARGIN) % BOARDHEIGHT > 45):
                    if (x - XMARGIN) % BOARDWIDTH < 15:
                        pointx = int((x - XMARGIN) // BOARDWIDTH)
                    else:
                        pointx = int((x - XMARGIN) // BOARDWIDTH + 1)
                    if (y - YMARGIN) % BOARDHEIGHT < 15:
                        pointy = int((y - YMARGIN) // BOARDHEIGHT)
                    else:
                        pointy = int((y - YMARGIN) // BOARDHEIGHT + 1)
                    if player == 'A' and board[pointy][pointx] == -1:
                        board[pointy][pointx] = 1
                        if checkwin(pointy, pointx):
                            game_status = 2
                            return
                        player = 'B'
                    elif player == 'B' and board[pointy][pointx] == -1:
                        board[pointy][pointx] = 0
                        if checkwin(pointy, pointx):
                            game_status = 2
                            return
                        player = 'A'
        pygame.display.update()
        FPSCLOCK.tick(FPS)

    def checkwin(x, y):
        if player == 'A':
            win = 1
        else:
            win = 0
        if x > 4:
            if board[x - 4][y] == board[x - 3][y] == board[x - 2][y] == board[x - 1][y] == board[x][y] == win:
                return True
        if x > 4 and y > 4:
            if board[x - 4][y - 4] == board[x - 3][y - 3] == board[x - 2][y - 2] == board[x - 1][y - 1] == board[x][
                y] == win:
                return True
        if x > 4 and y < BOXSIZE - 3:
            if board[x - 4][y + 4] == board[x - 3][y + 3] == board[x - 2][y + 2] == board[x - 1][y + 1] == board[x][
                y] == win:
                return True
        if x < BOXSIZE - 3:
            if board[x][y] == board[x + 1][y] == board[x + 2][y] == board[x + 3][y] == board[x + 4][y] == win:
                return True
        if x < BOXSIZE - 3 and y > 4:
            if board[x][y] == board[x + 1][y - 1] == board[x + 2][y - 2] == board[x + 3][y - 3] == board[x + 4][
                y - 4] == win:
                return True
        if x < BOXSIZE - 3 and y < BOXSIZE - 3:
            if board[x][y] == board[x + 1][y + 1] == board[x + 2][y + 2] == board[x + 3][y + 3] == board[x + 4][
                y + 4] == win:
                return True
        if y > 4:
            if board[x][y - 4] == board[x][y - 3] == board[x][y - 2] == board[x][y - 1] == board[x][y] == win:
                return True
        if y < BOXSIZE - 3:
            if board[x][y] == board[x][y + 1] == board[x][y + 2] == board[x][y + 3] == board[x][y + 4] == win:
                return True
        return False

    def game_over():
        global game_status, board
        DrawBoard()
        winSurf = BIGFONT.render(f'player{player} Win!', 1, BLACK)
        winRect = winSurf.get_rect()
        winRect.centerx = int(WINDOWWIDTH / 2)
        winRect.top = 0
        startSurf = BASICFONT.render('Press a key to play again', 1, BLACK)
        startRect = startSurf.get_rect()
        startRect.centerx = int(WINDOWWIDTH) / 2
        startRect.top = 50
        DISPLAYSURF.blit(winSurf, winRect)
        DISPLAYSURF.blit(startSurf, startRect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                board = generatebooard()
                game_status = 0

    def main():
        global BOXSIZE, XMARGIN, YMARGIN, FPSCLOCK, DISPLAYSURF, BASICFONT, boxboard, BIGFONT, BG, BGRect, game_status, board, player, ChFONT, ChBFONT

        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('game')
        BASICFONT = pygame.font.Font('freesansbold.ttf', 30)
        BIGFONT = pygame.font.Font('freesansbold.ttf', 50)

        game_status = 0
        board = generatebooard()
        player = 'A'

        while True:
            """
            res = requests.get('http://192.168.1.15:8080/get_qp')
            boxboard = json.loads(res.text)[0]
            boxboard = eval(boxboard)
            DISPLAYSURF.fill(BGCOLOR)
            DrawBoard(boxboard)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            x = input('请输入x坐标：')
            y = input('请输入y坐标：')
            req = requests.post('http://192.168.1.15:8080/update_qp', data={'x':x, 'y':y, 'p':'A'})
            """
            if game_status == 0:
                game_status = game_waiting()
            elif game_status == 1:
                game_running()
            elif game_status == 2:
                game_over()

            pygame.display.update()
            FPSCLOCK.tick(FPS)

    if __name__ == "__main__":
        main()