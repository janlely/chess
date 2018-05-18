
def alphaBeta(situation, depth, alpha, beta):
    if(depth == 0):
    for i in range(10):
        val = -alphaBeta(situation, depth - 1, -beta, -alpha)
        if val >= beta:
            return beta
        if val > alpha:
            alpha = val
    return alpha


