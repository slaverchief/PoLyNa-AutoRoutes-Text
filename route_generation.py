from graph_data_BS.graph_data import *
from direction_services import *
from selenium import webdriver
import selenium


class RouteMaker:

    def __init__(self, building_name):
        chrome_options = selenium.webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        self.__driver = selenium.webdriver.Chrome(options=chrome_options)
        self.__driver.get('https://mospolynavigation.github.io/clientNavigation/')
        # self.__rusnames = auditoriumsRusNames
        if building_name == 'BS':
            self.__vertexes = BS_Vertexes
            self.__rusnames = BS_RusNames

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

    @staticmethod
    def format_route(l):
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

        try:
            command = f'return graph.getShortestWayFromTo("{from_point}","{to_point}")'
            res = self.__driver.execute_script(command)
            return RouteMaker.format_route(res['way'])
        except:
            raise Exception('во время запроса маршрута, возможно вы указали некорректное название начальной и конечной точки')

    @staticmethod
    def waiting_for_the_turn(l):
        count = 0
        for m in l:
            if m == 'gfs':
                return False
            elif m == 'tr' or m == 'tl':
                count += 1
                if count > 1:
                    return True
            elif m.split('_') and m.split('_')[0] == 'st':
                return False
        return False

    @staticmethod
    def generate_str(route_list, to_p_rus):
        string = ''
        stages_history = []
        to_p = BS_RusNames[to_p_rus]

        def count_skip_turn(nodes):
            count = 1
            tagged_gfs = []
            if nodes[0] in ('tl', 'tr') or (nodes[0].split('_') and nodes[0].split('_')[0] == 'st'):
                return 0
            for j in range(0, len(nodes)):
                node = nodes[j]
                if node in ('tl', 'tr') or (node.split('_') and node.split('_')[0] == 'st'):
                    return count, tagged_gfs
                elif node == 'gfs':
                    tagged_gfs.append(j)
                    count += 1

        for i in range(len(route_list)):
            move = route_list[i]
            if move == 'tl':
                if i == len(route_list) - 1:
                    string += f'аудитория {to_p.split('-')[1]} будет слева'
                else:
                    string += 'поверните налево, '
            elif move == 'tr':
                if i == len(route_list) - 1:
                    string += f'аудитория {to_p} будет справа'
                else:
                    string += 'поверните направо, '
            elif move == 'gf' and route_list[i-1] not in ('gf', 'gfs'):
                string += 'идите прямо, '
                if RouteMaker.waiting_for_the_turn(route_list[i:]):
                    string += 'до следующего поворота, '
            elif move == 'gfs':
                res = count_skip_turn(route_list[i+1:])
                if res and res[0]:
                    string += f'пропустите {res[0]} поворот(а)(ов), '
                    for index in res[1]:
                        route_list[index+i+1] = 'gfs_ach'
            elif move == 'crs': 
                string += 'перейдите на другой корпус, '
            elif move != 'gf' and move != 'gfs_ach':
                spl = move.split('_')
                if not stages_history or len(stages_history)%2 == 0:
                    if spl[0] == 'st':
                        if route_list[-1] not in ('gf', 'gfs'):
                            string += 'идите до лестницы и '
                        else:
                            string += 'до лестницы и '
                stages_history.append(int(spl[1]))
                if len(stages_history) > 1 and len(stages_history)%2 == 0:
                    if stages_history[-1] > stages_history[-2]:
                        string += f'поднимитесь на {stages_history[-1]} этаж, '
                    else:
                        string += f'спуститесь на {stages_history[-1]} этаж, '

        return string

    def __generate_route_list(self, from_p_rus: str, to_p_rus: str):
        from_p, to_p = self.__rusnames[from_p_rus], self.__rusnames[to_p_rus]

        way = self.__get_route(from_p, to_p)
        if not way:
            return False
        cur_pos = way[0]
        x1, x2, y1, y2 = self.__vert_get(way[0])['x'], self.__vert_get(way[1])['x'], self.__vert_get(way[0])['y'], self.__vert_get(way[1])['y']
        t = Turtle(cur_pos, x2, y2, self.__vertexes)
        route_list = []
        is_from_aud = self.__vert_get(way[0]).get('type') == 'entrancesToAu'
        for i in range(1, len(way)):
            node = way[i]
            nodespl = node.split('-')
            if len(nodespl) == 4 and nodespl[2] == 'crossing':
                route_list.append('crs')
                return route_list + self.__generate_route_list(way[i+1], to_p)
            res = t.set_transition(node)
            hallways_neighbor_amount = self.__count_neighbour_hallways(self.__vert_get(node))
            if is_from_aud and i == 1:
                continue
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
        return route_list

    def tell_route(self, from_p_rus: str, to_p_rus: str):
        try:
            return RouteMaker.generate_str(self.__generate_route_list(from_p_rus, to_p_rus), to_p_rus)
        except Exception as ex:
            return f"Возникла ошибка: проверьте корректность ввода данных."



