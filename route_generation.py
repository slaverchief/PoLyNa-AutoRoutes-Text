from graph_data import Vertexes, auditoriumsRusNames
from direction_services import *
from selenium import webdriver
import selenium



class RouteMaker:
    def __del__(self, instance):
        self.__driver.quit()
    def __init__(self):
        chrome_options = selenium.webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        self.__driver = selenium.webdriver.Chrome(options=chrome_options)
        self.__rusnames = auditoriumsRusNames
        self.__vertexes = Vertexes

    def __count_neighbour_hallways(self, node):
        count = 0
        for n in map(lambda x: self.__vertexes[x[0]], node['neighborData']):
            if n['type'] == 'hallway':
                count += 1
        return count

    def __get_route(self, from_point: str, to_point: str):
        self.__driver.get('https://mospolynavigation.github.io/nav2/')
        command = f'return graph.getShortestWayFromTo("{from_point}","{to_point}")'
        res = self.__driver.execute_script(command)
        return res['way']

    def __is_more_than_2_turns(self, l):
        count = 0
        for m in l:
            if m == 'tr' or m == 'tl':
                count+=1
                if count > 1:
                    return True
        return False


    def __generate_str(self, route_list):
        string = ''
        stages_history = []
        for i in range(len(route_list)):
            move = route_list[i]
            if move == 'tl':
                if i == len(route_list) - 1:
                    string += 'аудитория будет слева'
                else:
                    string += 'поверните налево, '
            elif move == 'tr':
                if i == len(route_list) - 1:
                    string += 'аудитория будет справа'
                else:
                    string += 'поверните направо, '
            elif move == 'gf' and route_list[i-1] != 'gf':
                string += 'идите прямо, '
                if self.__is_more_than_2_turns(route_list[i:]):
                    string += 'до следующего поворота, '
            elif move == 'gfs':
                if not route_list[i+1] in ('tl', 'tr'):
                    string += 'пропустите поворот, '
            elif move != 'gf':
                spl = move.split('_')
                if not stages_history or len(stages_history)%2 == 0:
                    if spl[0] == 'st':
                        string += 'идите на лестницу и '
                stages_history.append(int(spl[1]))
                if len(stages_history) > 1 and len(stages_history)%2 == 0:
                    if stages_history[-1] > stages_history[-2]:
                        string += f'поднимитесь на {stages_history[-1]} этаж, '
                    else:
                        string += f'спуститесь на {stages_history[-1]} этаж, '

        return string

    def tell_route(self, from_p_rus: str, to_p_rus: str):
        try:
            from_p, to_p = self.__get_eng_name(from_p_rus), self.__get_eng_name(to_p_rus)
        except Exception as ex:
            return f"Error: {ex}"
        way = self.__get_route(from_p, to_p)
        if not way:
            return False
        cur_pos = way[0]
        x1, x2, y1, y2 = self.__vertexes[way[0]]['x'], self.__vertexes[way[1]]['x'], self.__vertexes[way[0]]['y'], self.__vertexes[way[1]]['y']
        t = Turtle(cur_pos, x2, y2, self.__vertexes)
        route_list = []
        for node in way[1:]:
            res = t.set_transition(node)
            hallways_neighbor_amount = self.__count_neighbour_hallways(self.__vertexes[node])
            if res == 'l':
                route_list.append('tl')
            elif res == 'r':
                route_list.append('tr')
            elif res == 'f' and route_list:
                if hallways_neighbor_amount >= 3:
                    route_list.append('gfs')
                else:
                    route_list.append('gf')
            elif res != 'f':
                spl = res.split('_')
                if spl[0] == 'uds':
                    route_list.append(f'st_{spl[1]}')


        return self.__generate_str(route_list)

    def __get_eng_name(self, p_rus):
        for pair in self.__rusnames:
            if pair[1] == p_rus:
                return pair[0]
        raise Exception(f"There is no auditorium with name {p_rus}")


