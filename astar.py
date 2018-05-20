#!/usr/bin/env python3

import math
import random
import time
import threading

import pygame

running = True
pathFound = False

infinite = 0xffffffff

gridpos = (0, 0)
width = 30
height = 30
gridsize = 20
blocksize = 18

grid = []
for i in range(height):
    grid.append([])
    for j in range(width):
        grid[i].append({
            "type": "free",
            "cost": infinite,
            "score": 0,
            "examinated": False,
            "previous": None
        })

startPos = (0, 20)
endPos = (20, 5)

for i in range(height):
    for j in range(width):
        if random.uniform(0, 1) < 0.3 and (j, i) not in [startPos, endPos]:
            grid[i][j]["type"] = "block"


def sigmoid(val):
    return 1/(1+math.exp(-val))


def pathFinding():
    openList = []

    def neighborListGet(node):
        x = node[0]
        y = node[1]
        retList = []
        dirList = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        for dir in dirList:
            nx = x+dir[0]
            ny = y+dir[1]
            if (nx >= 0 and nx < width and
                ny >= 0 and ny < height and
                    grid[ny][nx]["type"] == "free"):
                retList.append((nx, ny))
        return retList

    def heuristic(node):
        d = math.sqrt((node[0]-endPos[0])**2 + (node[1]-endPos[1])**2)
        c = grid[node[1]][node[0]]["cost"]
        return d - c*0.3

    cellData = grid[startPos[1]][startPos[0]]
    cellData["cost"] = 0
    cellData["score"] = heuristic(startPos)
    openList.append(startPos)

    while len(openList) > 0:
        if not running:
            break
        time.sleep(0.05)
        openList = list(
            sorted(openList, key=lambda n: grid[n[1]][n[0]]["score"]))
        best = openList.pop(0)
        if best == endPos:
            global pathFound
            pathFound = True
            print("Reached end point")
            break

        # examinated
        bestData = grid[best[1]][best[0]]
        bestData["examinated"] = True

        # explore neighbors
        neighbors = neighborListGet(best)
        for nb in neighbors:
            nbData = grid[nb[1]][nb[0]]

            if nbData["examinated"]:
                continue  # skip examinated node

            if not nb in openList:
                openList.append(nb)

            tmpCost = bestData["cost"] + 1
            if tmpCost >= nbData["cost"]:
                continue

            # record
            nbData["previous"] = best
            nbData["cost"] = tmpCost
            nbData["score"] = nbData["cost"] + heuristic(nb)


def update():
    global pathFound
    pathFinding()


def drawPath(screen, pos):
    def realPosGet(pos):
        offset = gridsize/2
        return (gridsize*pos[0]+offset, gridsize*pos[1]+offset)

    color = (0, 150, 0)
    curr = pos
    cellData = grid[curr[1]][curr[0]]
    while cellData["previous"]:
        prev = curr
        curr = cellData["previous"]
        pygame.draw.line(screen, color, realPosGet(prev), realPosGet(curr), 3)
        cellData = grid[curr[1]][curr[0]]


def grid_draw(screen):
    for y in range(height):
        for x in range(width):
            data = grid[y][x]
            color = (200, 200, 200)
            if data['type'] == 'block':
                color = (20, 20, 20)
            elif data['examinated']:
                color = (180, 180, 200)
            cellpos = (x*gridsize+gridpos[0], y*gridsize+gridpos[1])
            rect = pygame.Rect(cellpos[0]+gridsize/2-blocksize/2,
                               cellpos[1]+gridsize/2-blocksize/2, blocksize, blocksize)
            pygame.draw.rect(screen, color, rect)

            if (x, y) in [startPos, endPos]:
                color = (0, 200, 0)
                if endPos == (x, y):
                    color = (0, 150, 0)
                pygame.draw.rect(screen, color, rect, 5)


def main():
    global running
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Pathing finding 1")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # render
        screen.fill((255, 255, 255))
        grid_draw(screen)
        if pathFound:
            drawPath(screen, endPos)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    t = threading.Thread(target=update)
    t.start()
    main()
    t.join()
