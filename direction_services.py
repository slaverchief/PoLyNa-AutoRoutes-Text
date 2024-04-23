from graph_data import Vertexes


class Turtle:
    def __init__(self, init_pos: str, x2, y2, vertexes):
        self.__stair_passed_flag = False
        self.__pos_name = init_pos
        self.__vertexes = vertexes
        for v in self.__vertexes:
            if v['id'] == init_pos:
                self.__curpos = v
                break
        self.__dir = self.__find_direction(self.__curpos['x'], x2, self.__curpos['y'], y2)


    def __reverse_direction(self):
        if self.__dir == 'w':
            self.__dir = 'e'
        elif self.__dir == 'n':
            self.__dir = 's'
        elif self.__dir == 'e':
            self.__dir = 'w'
        else:
            self.__dir = 'n'

    def __vert_get(self, vid: str):
        for v in self.__vertexes:
            if v['id'] == vid:
                return v

    def set_transition(self, pos_name):
        pos = self.__vert_get(pos_name)
        new_direction = None
        if not self.__stair_passed_flag:
            x1, x2, y1, y2 = self.__curpos['x'], pos['x'], self.__curpos['y'], pos['y']
            new_direction = self.__find_direction(x1,x2,y1,y2)
        else:
            self.__reverse_direction()
        res = 'f'
        if pos['type'] == 'stair':
            res = 'uds_' + (pos_name.split('-')[1])
            if not self.__stair_passed_flag:
                self.__stair_passed_flag = True
            else:
                self.__stair_passed_flag = False
        if self.__dir != new_direction and new_direction != None:
            if pos['type'] != 'stair':
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


