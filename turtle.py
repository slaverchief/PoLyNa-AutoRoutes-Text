class Turtle:

    def __init__(self, init_pos, x1, x2, y1, y2):
        self.curpos = init_pos
        self.dir = self.find_direction(x1, x2, y1, y2)

    def find_direction(self, x1, x2, y1, y2):
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