
def printSheet(sit, last, cur):
    peicesB = {0:'车', 1:'马', 2:'象', 3:'士', 4:'将', 5:'砲', 6:'卒'}
    peicesR = {0:'车', 1:'马', 2:'相', 3:'仕', 4:'帅', 5:'炮', 6:'兵'}
    rb = {0:'黑', 1:'红'}
    fbt = {-1:'退', 0:'平', 1:'进'}
    start = last
    end = cur
    rorb = sit.getThinker()
    stone = sit.get(last)[1]
    if rorb == 0:#black
        if end[1] == start[1]:
            step = abs(end[0] - start[0])
        else:
            step = end[1] + 1
        line = start[1] + 1
        if end[0] > start[0]:
            forbt = 1
        elif end[0] ==  start[0]:
            forbt = 0
        else:
            forbt = -1
    else:
        if end[1] == start[1]:
            step = abs(end[0] - start[0])
        else:
            step = 9 - end[1]
        line = 9 - start[1]
        if end[0] > start[0]:
            forbt = -1
        elif end[0] ==  start[0]:
            forbt = 0
        else:
            forbt = 1
    if rorb == 0:
        print ('%s: %s %d %s %d' % (rb[rorb],
            peicesB[stone],
            line,
            fbt[forbt],
            step
            ))
    else:
        print ('%s: %s %d %s %d' % (rb[rorb],
            peicesR[stone],
            line,
            fbt[forbt],
            step
            ))
