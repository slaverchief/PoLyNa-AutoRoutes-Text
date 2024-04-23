
from direction_services import *
from selenium import webdriver
import selenium



class RouteMaker:

    def __init__(self):
        chrome_options = selenium.webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        self.__driver = selenium.webdriver.Chrome(options=chrome_options)
        self.__driver.get('https://mospolynavigation.github.io/clientNavigation/')
        # self.__rusnames = auditoriumsRusNames
        self.__vertexes = Vertexes

    def __del__(self):
        self.__driver.quit()

    def __vert_get(self, id: str):
        for v in self.__vertexes:
            if v['id'] == id:
                return v

    def __count_neighbour_hallways(self, node):
        count = 0
        for n in map(lambda x: self.__vert_get(x[0]), node['neighborData']):
            if n['type'] == 'hallway':
                count += 1
        return count


    def __format_route(self, l):
        is_cross_staging = False
        i = 0
        while i != len(l):
            spl1 = l[i].split('-')
            if len(spl1) == 4 and spl1[2] == 'stair':
                if not is_cross_staging:
                    is_cross_staging = True
                else:
                    spl2 = l[i+1].split('-')
                    if len(spl2) == 4 and spl2[2] == 'stair':
                        del l[i]
                        continue
                    else:
                        is_cross_staging = False
            i += 1
        return l


    def __get_route(self, from_point: str, to_point: str):

        command = f'return graph.getShortestWayFromTo("{from_point}","{to_point}")'
        res = self.__driver.execute_script(command)
        return self.__format_route(res['way'])

    def __waiting_for_the_turn(self, l):
        count = 0
        for m in l:
            if m == 'gfs':
                return False
            if m == 'tr' or m == 'tl':
                count+=1
                if count > 1:
                    return True
        return False


    def __generate_str(self, route_list, to_p):
        string = ''
        stages_history = []

        def skip_a_turn(node):
            if (node in ('tl', 'tr') or (node.split('_') and  node.split('_')[0] == 'st')):
                return False
            return True
        for i in range(len(route_list)):
            move = route_list[i]
            if move == 'tl':
                if i == len(route_list) - 1:
                    string += f'аудитория {to_p.split('-')[1]} будет слева'
                else:
                    string += 'поверните налево, '
            elif move == 'tr':
                if i == len(route_list) - 1:
                    string += f'аудитория {to_p.split('-')[1]} будет справа'
                else:
                    string += 'поверните направо, '
            elif move == 'gf' and route_list[i-1] != 'gf':
                string += 'идите прямо, '
                if self.__waiting_for_the_turn(route_list[i:]):
                    string += 'до следующего поворота, '
            elif move == 'gfs':
                if skip_a_turn(route_list[i+1]):
                    string += 'пропустите поворот, '
            elif move != 'gf':
                spl = move.split('_')
                if not stages_history or len(stages_history)%2 == 0:
                    if spl[0] == 'st':
                        string += 'до лестницы и'
                stages_history.append(int(spl[1]))
                if len(stages_history) > 1 and len(stages_history)%2 == 0:
                    if stages_history[-1] > stages_history[-2]:
                        string += f'поднимитесь на {stages_history[-1]} этаж, '
                    else:
                        string += f'спуститесь на {stages_history[-1]} этаж, '

        return string

    def tell_route(self, from_p_rus: str, to_p_rus: str):
        try:
            # from_p, to_p = self.__get_eng_name(from_p_rus), self.__get_eng_name(to_p_rus)
            from_p, to_p = from_p_rus, to_p_rus
        except Exception as ex:
            return f"Error: {ex}"
        way = self.__get_route(from_p, to_p)
        if not way:
            return False
        cur_pos = way[0]
        x1, x2, y1, y2 = self.__vert_get(way[0])['x'], self.__vert_get(way[1])['x'], self.__vert_get(way[0])['y'], self.__vert_get(way[1])['y']
        t = Turtle(cur_pos, x2, y2, self.__vertexes)
        route_list = []
        for i in range(1, len(way)):
            node = way[i]
            res = t.set_transition(node)
            hallways_neighbor_amount = self.__count_neighbour_hallways(self.__vert_get(node))
            if res == 'l':
                route_list.append('tl')
            elif res == 'r':
                route_list.append('tr')
            elif res == 'f':
                if hallways_neighbor_amount >= 3:
                    route_list.append('gfs')
                else:
                    route_list.append('gf')
            else:
                spl = res.split('_')
                if spl[0] == 'uds':
                    route_list.append(f'st_{spl[1]}')


        return self.__generate_str(route_list, to_p)

    # def __get_eng_name(self, p_rus):
    #     for pair in self.__rusnames:
    #         if pair[1] == p_rus:
    #             return pair[0]
    #     raise Exception(f"There is no auditorium with name {p_rus}")


