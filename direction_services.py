from graph_data import Vertexes


class Turtle:
    def __init__(self, init_pos: str, x2, y2, vertexes):
        self.__pos_name = init_pos
        self.__curpos = Vertexes[init_pos]
        self.__dir = self.__find_direction(self.__curpos['x'], x2, self.__curpos['y'], y2)
        self.__vertexes = vertexes

    def set_transition(self, pos_name):
        pos = self.__vertexes[pos_name]
        x1, x2, y1, y2 = self.__curpos['x'], pos['x'], self.__curpos['y'], pos['y']
        new_direction = self.__find_direction(x1,x2,y1,y2)
        res = 'f'
        if pos['type'] == 'stair':
            res = 'uds_' + (pos_name.split('-')[1])
        elif self.__dir != new_direction:
            if self.__is_3_14dor(self.__dir, new_direction):
                res = 'l'
            else:
                res = 'r'
            self.__dir = new_direction
        self.__curpos = pos
        self.__pos_name = pos_name
        return res

    def __find_direction(self, x1, x2, y1, y2):
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

    def __is_3_14dor(self, dir1, dir2):
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


