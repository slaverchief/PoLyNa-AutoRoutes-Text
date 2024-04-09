class Turtle:

    def __init__(self, init_pos, x2, y2):
        self.__curpos = init_pos
        self.__dir = find_direction(self.__curpos['x'], x2, self.__curpos['y'], y2)

    def set_transition(self, pos):
        x1, x2, y1, y2 = self.__curpos['x'], pos['x'], self.__curpos['y'], pos['y']
        new_direction = find_direction(x1,x2,y1,y2)
        res = 'f'
        if self.__dir != new_direction:
            if is_3_14dor(self.__dir, new_direction):
                res = 'l'
            else:
                res = 'r'
            self.__dir = new_direction
        self.__curpos = pos
        return res

def find_direction(x1, x2, y1, y2):
    direction = None

    if x1 != x2:
        if x1 > x2:
            direction = 'w'
        else:
            direction = 'e'
    else:
        if y1 > y2:
            direction = 's'
        else:
            direction = 'n'
    return direction

def is_3_14dor(dir1, dir2):
    if dir1 == 'n':
        if dir2 == 'e':
            return True
        else:
            return False
    if dir1 == 'e':
        if dir2 == 's':
            return True
        else:
            return False
    if dir1 == 'w':
        if dir2 == 'n':
            return True
        else:
            return False
    if dir1 == 's':
        if dir2 == 'w':
            return True
        else:
            return False
