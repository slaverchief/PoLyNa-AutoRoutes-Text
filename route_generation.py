from graph_data import Vertexes, auditoriumsRusNames as rusnames
from direction_services import *
from selenium import webdriver
import selenium

chrome_options = selenium.webdriver.ChromeOptions()
chrome_options.add_argument('headless')
driver = selenium.webdriver.Chrome(options=chrome_options)

def get_route(from_point: str, to_point: str):

    driver.get('https://mospolynavigation.github.io/nav2/')
    command = f'return graph.getShortestWayFromTo("{from_point}","{to_point}")'
    res = driver.execute_script(command)
    return res['way']

def is_more_than_2_turns(l):
    count = 0
    for m in l:
        if m == 'tr' or m == 'tl':
            count+=1
            if count > 1:
                return True
    return False


def generate_str(route_list):
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
            if is_more_than_2_turns(route_list[i:]):
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

def tell_route(from_p_rus: str, to_p_rus: str):
    try:
        from_p, to_p = get_eng_name(from_p_rus), get_eng_name(to_p_rus)
    except Exception as ex:
        return f"Error: {ex}"
    way = get_route(from_p, to_p)
    if not way:
        return False
    cur_pos = way[0]
    x1, x2, y1, y2 = Vertexes[way[0]]['x'], Vertexes[way[1]]['x'], Vertexes[way[0]]['y'], Vertexes[way[1]]['y']
    t = Turtle(cur_pos, x2, y2)
    route_list = []
    for node in way[1:]:
        res = t.set_transition(node)
        hallways_neighbor_amount = count_neighbour_hallways(Vertexes[node])
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


    return generate_str(route_list)

def get_eng_name(p_rus):
    for pair in rusnames:
        if pair[1] == p_rus:
            return pair[0]
    raise Exception(f"There is no auditorium with name {p_rus}")