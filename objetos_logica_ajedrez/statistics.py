import concurrent.futures
from functools import partial
from typing import List, Optional, Dict
from objetos_logica_ajedrez import env_chess as env
from objetos_logica_ajedrez.API_chess_com import ChessCom


class Statistics:
    def __init__(self, opponents: List, year: int = None, month: int = None):
        self.__year: int = year
        self.__month: int = month
        self.__opponents_data: List = []
        if len(opponents) == 0:
            raise ValueError(f'Sin datos en el parametro "opponents"')
        self.__opponents: List = opponents

    # Ejecucion asincronica (No se usa por el momento por error http de muchas peticiones a los endpoint)
    # def opponent_statistics(self):
    #     parcial_function = partial(ChessCom, year=self.__year, month=self.__month, opponent=True)
    #
    #     with concurrent.futures.ThreadPoolExecutor() as executor:
    #         # Aplicar la función a la lista en paralelo
    #         self.__opponents_data = list(executor.map(parcial_function, self.__opponents))

    def opponent_statistics_2(self):
        for opponent in self.__opponents:
            self.__opponents_data.append(ChessCom(opponent, self.__year, self.__month, opponent=True))


    @property
    def opponents_data(self):
        return self.__opponents_data


if __name__ == '__main__':
    chess_com = ChessCom("DanielNaroditsky", 2023, 11)
    # print(chess_com.opponents)
    print(chess_com.opponents["opponents_number"])
    # stat = Statistics(chess_com.opponents["opponents"], 2023, 11)
    # stat.opponent_statistics()
    # print(stat.opponents_data)
