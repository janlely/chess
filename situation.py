
class Situation:
    def __init__(self):
        self.thinker = 1 #红方先走
        self.end = False
        self.initSituation()

    def initSituation(self):
        self.sitMatrix = {}
        for i in range(10):
            for j in range(9):
                if i == 0:
                    self.sitMatrix[(i,j)] = [0, j if j < 5 else 8-j]
                elif i == 9:
                    self.sitMatrix[(i,j)] = [1, j if j < 5 else 8-j]
                elif i == 2 and j in [1,7]:
                    self.sitMatrix[(i,j)] = [0, 5]
                elif i == 7 and j in [1,7]:
                    self.sitMatrix[(i,j)] = [1, 5]
                elif i == 3 and j in [0,2,4,6,8]:
                    self.sitMatrix[(i,j)] = [0, 6]
                elif i == 6 and j in [0,2,4,6,8]:
                    self.sitMatrix[(i,j)] = [1, 6]
                else:
                    self.sitMatrix[(i,j)] = [-1, -1]

    def getThinker(self):
        return self.thinker


    def get(self, place):
        return self.sitMatrix[place]

    def isEnd(self):
        return self.end


    def change(self, lastPlace, curPlace):
        if self.sitMatrix[curPlace][1] == 4:
            self.end = True
            self.winner = self.thinker
        self.sitMatrix[curPlace] = self.sitMatrix[lastPlace]
        self.sitMatrix[lastPlace] = [-1,-1]
        self.thinker = 1 - self.thinker

    def getWinner(self):
        return self.winner
