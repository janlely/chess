
def movable(sit, last, cur):
    if sit.get(last)[1] == 0:
        return juMovable(sit, last, cur)
    elif sit.get(last)[1] == 1:
        return maMovable(sit, last, cur)
    elif sit.get(last)[1] == 2:
        return xiangMovable(sit, last, cur)
    elif sit.get(last)[1] == 3:
        return shiMovable(sit, last, cur)
    elif sit.get(last)[1] == 4:
        return jsMovable(sit, last, cur)
    elif sit.get(last)[1] == 5:
        return paoMovable(sit, last, cur)
    else:
        return bzMovable(sit, last, cur)

def juMovable(sit, last, cur):
    start = last
    end = cur
    if start[0] != end[0] and start[1] != end[1]:
        return False
    if start[0] == end[0] and start[1] == end[1]:
        return False
    if start[0] == end[0]:
        row = start[0]
        coll = min(start[1], end[1])
        colr = max(start[1], end[1])
        for i in range(coll+1, colr):
            if sit.get((row,i))[1] != -1:
                return False
    else:
        col = start[1]
        rowl = min(start[0], end[0])
        rowr = max(start[0], end[0])
        for i in range(rowl+1, rowr):
            if sit.get((i, col))[1] != -1:
                return False
    return True

def maMovable(sit, last, cur):
    start = last
    end = cur
    if end[0] - start[0] == -1 and start[1] - end[1] == 2:#up1
        if sit.get((start[0], start[1] - 1))[1] != -1:
            return False
        return True
    elif end[0] - start[0] == -2 and start[1] - end[1] == 1:#up2
        if sit.get((start[0]-1, start[1]))[1] != -1:
            return False
        return True
    elif end[0] - start[0] == -2 and end[1] - start[1] == 1:#up3
        if sit.get((start[0]-1, start[1]))[1] != -1:
            return False
        return True
    elif end[0] - start[0] == -1 and end[1] - start[1] == 2:#up4
        if sit.get((start[0], start[1] + 1))[1] != -1:
            return False
        return True
    elif start[0] - end[0] == -1 and start[1] - end[1] == 2:#down1
        if sit.get((start[0], start[1] - 1))[1] != -1:
            return False
        return True
    elif start[0] - end[0] == -2 and start[1] - end[1] == 1:#down2
        if sit.get((start[0]+1,start[1]))[1] != -1:
            return False
        return True
    elif start[0] - end[0] == -2 and start[1] - end[1] == -1:#down3
        if sit.get((start[0]+1,start[1]))[1] != -1:
            return False
        return True
    elif start[0] - end[0] == -1 and start[1] - end[1] == -2:#down4
        if sit.get((start[0], start[1]+1))[1] != -1:
            return False
        return True
    else:
        return False


def xiangMovable(sit, last, cur):
    start = last
    end = cur
    if sit.getThinker() == 0 and end[0] > 4:
        return False
    if sit.getThinker() == 1 and end[0] < 5:
        return False

    if end[0] - start[0] == -2 and end[1] - start[1] == -2:#left top
        if sit.get((start[0]-1, start[1]-1))[1] != -1:
            return False
        return True
    if end[0] - start[0] == -2 and end[1] - start[1] == 2:#right top
        if sit.get((start[0]-1,start[1]+1))[1] != -1:
            return False
        return True
    if end[0] - start[0] == 2 and end[1] - start[1] == -2:#left bot
        if sit.get((start[0]+1, start[1]-1))[1] != -1:
            return False
        return True
    if end[0] - start[0] == 2 and end[1] - start[1] == 2:#right bot
        if sit.get((start[0]+1, start[1]+1))[1] != -1:
            return False
        return True
    return False

def shiMovable(sit, last, cur):
    start = last
    end = cur
    if sit.getThinker() == 0 and (end[0] > 2 or end[1] < 3 or end[1] > 5 ):
        return False
    if sit.getThinker() == 1 and (end[0] < 7 or end[1] < 3 or end[1] > 5 ):
        return False
    if end[0] - start[0] == -1 and end[1] - start[1] == -1:#left top
        return True
    if end[0] - start[0] == -1 and end[1] - start[1] == 1:#right top
        return True
    if end[0] - start[0] == 1 and end[1] - start[1] == -1:#left bot
        return True
    if end[0] - start[0] == 1 and end[1] - start[1] == 1:#right bot
        return True
    return False

def jsMovable(sit, last, cur):
    start = last
    end = cur
    if sit.getThinker() == 0 and (end[0] > 2 or end[1] < 3 or end[1] > 5 ):
        return False
    if sit.getThinker() == 1 and (end[0] < 7 or end[1] < 3 or end[1] > 5 ):
        return False
    if end[0] - start[0] == -1 and end[1] == start[1]:#top
        return True
    if end[0] == start[0] and end[1] - start[1] == -1:#left
        if sit.getThinker() == 0:
            for i in range(start[0]+1, 10):
                if sit.get((i,end[1]))[1] == 4:
                    return False
                else:
                    return True
            if sit.getThinker() == 1:
                for i in range(start[0]-1, -1, -1):
                    if sit.get((i,end[1]))[1] == 4:
                        return False
                    else:
                        return True
            return True
    if end[0] - start[0] == 1 and end[1] == start[1]:#bot
        return True
    if end[0] == start[0] and end[1] - start[1] == 1:#right
        if sit.getThinker() == 0:
            for i in range(start[0]+1, 10):
                if sit.get((i,end[1]))[1] == 4:
                    return False
                else:
                    return True
        if sit.getThinker() == 1:
            for i in range(start[0]-1, -1, -1):
                if sit.get((i,end[1]))[1] == 4:
                    return False
                else:
                    return True
        return True
    return False


def paoMovable(sit, last, cur):
    start = last
    end = cur
    if start[0] != end[0] and start[1] != end[1]:
        return False
    if start[0] == end[0] and start[1] == end[1]:
        return False
    if start[0] == end[0]:
        row = start[0]
        coll = min(start[1], end[1])
        colr = max(start[1], end[1])
        if sit.get(end)[1] == -1:
            for i in range(coll+1, colr):
                if sit.get((row,i))[1] != -1:
                    return False
        else:
            count = 0
            for i in range(coll+1, colr):
                if sit.get((row,i))[1] != -1:
                    count+=1
            if count != 1:
                return False

    else:
        col = start[1]
        rowl = min(start[0], end[0])
        rowr = max(start[0], end[0])
        if sit.get(end)[1] == -1:
            for i in range(rowl+1, rowr):
                if sit.get((i, col))[1] != -1:
                    return False
        else:
            count = 0
            for i in range(rowl+1, rowr):
                if sit.get((i,col))[1] != -1:
                    count+=1
            if count != 1:
                return False

    return True

def bzMovable(sit, last, cur):
    start = last
    end = cur
    if start[0] != end[0] and start[1] != end[1]:
        return False
    if start[0] == end[0] and start[1] == end[1]:
        return False
    if abs(start[0] - end[0]) > 1 or abs(start[1] - end[1]) > 1:
        return False
    if sit.getThinker() == 0 and end[0] <= 4 and start[1] != end[1]:
        return False
    if sit.getThinker() == 0 and start[0] > end[0]:
        return False
    if sit.getThinker() == 1 and end[0] >= 5 and  start[1] != end[1]:
        return False
    if sit.getThinker() == 1 and start[0] < end[0]:
        return False

    return True
