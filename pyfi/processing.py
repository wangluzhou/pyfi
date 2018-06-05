def macro_adjust(yoy, cyoy):
    yoy = yoy[yoy.index.month != 1]
    for i in range(len(yoy)):
        if yoy.index[i].month == 2:
            yoy[i] = cyoy[i]
    return yoy
