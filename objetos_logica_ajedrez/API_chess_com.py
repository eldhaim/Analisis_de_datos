import io
import pandas as pd
import requests as rq
import json
from datetime import datetime
from objetos_logica_ajedrez import env_chess as env
from http import HTTPStatus
from typing import List, Optional, Dict
from chess import pgn, SQUARE_NAMES

from objetos_logica_ajedrez.chess_methods import handle_none, mapping_control


class ChessCom:
    """
    Clase para interactuar con la API de chess.com y obtener información sobre partidas de ajedrez.

    Args:
        username (str): Nombre de usuario de chess.com.
        year (int): Año para filtrar partidas.
        month (int): Mes para filtrar partidas.

    Attributes:
        __username (str): Nombre de usuario de chess.com.
        __year (int): Año para filtrar partidas.
        __month (int): Mes para filtrar partidas.
        __response (requests.Response): Respuesta de la API de chess.com.
        __pgn (List[pgn]): Lista de objetos PGN de la biblioteca python-chess.
        __json_response (json): Respuesta en formato JSON de la API de chess.com.
        __games_list (List): Lista que almacena información de partidas.
        __games (List): Lista de partidas mensuales obtenidas de chess.com.
        __pgn_info_tags (List): Lista de etiquetas PGN encontradas en las partidas.
        __pgn_info_tags_columns (List): Lista de columnas derivadas de las etiquetas PGN.
        __pgn_info_moves (List): Lista de movimientos de las partidas en formato PGN.
        __data_frames_games (Optional[pd.DataFrame]): DataFrame que almacena información general de partidas.
        __data_frames_moves_games (Optional[pd.DataFrame]): DataFrame que almacena información de movimientos de partidas.
    """

    def __init__(self, username: str = None, year: int = None, month: int = None, opponent: bool = False):
        """
        Inicializa una instancia de ChessCom con los parámetros proporcionados.

        Args:
            username (str): Nombre de usuario de chess.com.
            year (int): Año para filtrar partidas.
            month (int): Mes para filtrar partidas.
            opponent (bool): Si este parametro es True la logica se modifica de tal forma que se obtienen los datos
                             del oponente pero no sobre la estadistica de sus juegos como jugadas y tiempos, unicamente
                             se va a generar el DF original con la estructura general, tampoco debe generarse el listado
                             de oponentes.
        """
        print(f'{username} -> {"usuario" if not opponent else "oponente"}')
        self.__username: str = username
        self.__year: int = year
        self.__month: int = month
        self.__opponent: bool = opponent
        self.__response: rq = None
        self.__pgn: List[pgn] = []
        self.__json_response: json = None
        self.__games_list: List = []
        self.__games: List = self.__get_monthly_games()
        self.__pgn_info_tags: List = []
        self.__pgn_info_tags_columns: List = []
        self.__pgn_info_moves: List = []
        self.__time_moves: List = []
        self.__opponents: Dict = {}
        self.__white_pieces_games_df: Optional[pd.DataFrame] = None
        self.__black_pieces_games_df: Optional[pd.DataFrame] = None
        self.__data_frames_games: Optional[pd.DataFrame] = self.__get_data_frame()
        self.__data_frames_moves_games: Optional[pd.DataFrame] = None
        if not self.__opponent:
            self.__data_frames_moves_games = pd.DataFrame(
                self.__pgn_info_moves,
                columns=[
                    env.URL, env.ORDER, env.FROM, env.PIECE, env.TO, env.CAPTURED
                ]
            )
            self.__data_frames_moves_games[env.TIME] = self.__time_moves
        self.__user_pieces()

    def __get_monthly_games(self) -> List:
        """
        Obtiene la lista de partidas mensuales del usuario desde chess.com.

        **Returns**:
            List: Lista de partidas mensuales en formato JSON.
        """
        try:
            self.__response = rq.get(env.PLAYER_GAMES_URL.format(self.__username, self.__year, self.__month),
                                     headers=env.HEADERS)
            if self.__response.status_code == HTTPStatus.OK:
                self.__json_response = self.__response.json()
                return self.__json_response[env.GAMES]
            else:
                raise Exception(f'{self.__response.status_code}{self.__response.text}')
        except Exception as e:
            print(f'__get_monthly_games -> ERROR: \n{e}')
            return []

    def __get_data_frame(self) -> pd.DataFrame:
        """
        Crea un DataFrame con información general de partidas.

        **Returns**:
            pd.DataFrame: DataFrame con información general de partidas.
        """
        try:
            if len(self.__games) == 0:
                raise Exception(f'Juegos no encontrados')
            for game in self.__games:
                self.__create_data_structure(game=game)
            _columns = [
                env.URL, env.FEN, env.START_TIME, env.END_TIME,
                env.TIME_CONTROL, env.RULES, env.ECO, env.TOURNAMENT,
                env.MATCH, env.WHITE_USERNAME, env.WHITE_RATING,
                env.WHITE_RESULT, env.WHITE_ID, env.BLACK_USERNAME,
                env.BLACK_RATING, env.BLACK_RESULT, env.BLACK_ID,
                env.ACCURACIES_WHITE, env.ACCURACIES_BLACK
            ]
            _columns = _columns + self.__pgn_info_tags_columns
            general_df = pd.DataFrame(
                self.__games_list,
                columns=_columns
            )
            return general_df
        except Exception as e:
            raise Exception(f'__get_data_frame -> ERROR: \n{e}')

    def __create_data_structure(self, game):
        """
        Crea la estructura de datos para una partida y la agrega a la lista de partidas.

        Args:
            game: Información de la partida en formato JSON.
        """
        try:
            if handle_none(mapping_control(game, env.RULES)) != 'bughouse':
                self.__get_pgn_data_frame(
                    handle_none(mapping_control(game, env.PGN)),
                    handle_none(mapping_control(game, env.URL))
                )
                _general = [
                    handle_none(mapping_control(game, env.URL)),
                    handle_none(mapping_control(game, env.FEN)),
                    handle_none(mapping_control(game, env.START_TIME)),
                    handle_none(mapping_control(game, env.END_TIME)),
                    handle_none(mapping_control(game, env.TIME_CONTROL)),
                    handle_none(mapping_control(game, env.RULES)),
                    handle_none(mapping_control(game, env.ECO)),
                    handle_none(mapping_control(game, env.TOURNAMENT)),
                    handle_none(mapping_control(game, env.MATCH))
                ]
                white = {}
                black = {}
                accuracies = {}
                try:
                    white = game[env.WHITE]
                    black = game[env.BLACK]
                    accuracies = game[env.ACCURACIES]
                except KeyError:
                    pass

                _white = [
                    handle_none(mapping_control(white, env.USERNAME)),
                    handle_none(mapping_control(white, env.RATING)),
                    handle_none(mapping_control(white, env.RESULT)),
                    handle_none(mapping_control(white, env.ID))
                ]
                _black = [
                    handle_none(mapping_control(black, env.USERNAME)),
                    handle_none(mapping_control(black, env.RATING)),
                    handle_none(mapping_control(black, env.RESULT)),
                    handle_none(mapping_control(black, env.ID))
                ]
                _accuracies = [
                    handle_none(mapping_control(accuracies, env.USERNAME)),
                    handle_none(mapping_control(accuracies, env.RATING))
                ]
                self.__games_list.append(_general + _white + _black + _accuracies + self.__pgn_info_tags)
        except Exception as e:
            raise Exception(f'__create_data_structure -> ERROR: \n{e}')

    def __get_pgn_data_frame(self, pgn_in, url):
        """
        Analiza el PGN de una partida y agrega la información de movimientos a la lista.

        Args:
            pgn_in (str): PGN de la partida.
            url (str): URL de la partida.
        """
        try:
            _pgn_tags = {}
            _pgn_game = pgn.read_game(io.StringIO(pgn_in))
            _board = _pgn_game.board()
            _time_matches = env.TIME_PATTERN.findall(pgn_in)
            if not self.__opponent:
                def map_time(time):
                    try:
                        tiempo = datetime.strptime(time, "%H:%M:%S.%f")
                    except ValueError:
                        tiempo = datetime.strptime(time, "%H:%M:%S")
                    return tiempo.strftime("%H:%M:%S.%f")[:-3] + ".0"

                [self.__time_moves.append(map_time(i)) for i in _time_matches]
                _counter: int = 1
                for move in _pgn_game.mainline_moves():
                    uci_move = move.uci()
                    from_square = uci_move[:2]
                    to_square = uci_move[2:]
                    _captured_piece = None
                    if _board.piece_at(SQUARE_NAMES.index(from_square)) is not None:
                        piece = _board.piece_at(SQUARE_NAMES.index(from_square))
                        if _board.is_capture(move):
                            if len(to_square) == 3 and to_square[2].lower() in env.TO_SQUARE:
                                _captured_piece = to_square[2].lower()
                                to_square = to_square[:2]
                            if to_square in SQUARE_NAMES:
                                _captured_piece = _board.piece_at(SQUARE_NAMES.index(to_square))
                        self.__pgn_info_moves.append(
                            [
                                url, _counter, uci_move[:-2], piece.symbol(), to_square, str(_captured_piece)
                            ]
                        )
                    else:
                        self.__pgn_info_moves.append(
                            [
                                url, _counter, uci_move[:-2], None, to_square, str(_captured_piece)
                            ]
                        )
                    _counter += 1
                    _board.push(move)
            _matches = env.TAG_PATTERN.findall(pgn_in)
            for match in _matches:
                key, value = match
                _pgn_tags[key] = value
            if env.TOURNAMENT.capitalize() in _pgn_tags:
                del _pgn_tags[env.TOURNAMENT.capitalize()]
            if len(_pgn_tags.keys()) > len(self.__pgn_info_tags_columns):
                self.__pgn_info_tags_columns = list(_pgn_tags.keys())
            self.__pgn_info_tags = list(_pgn_tags.values())
        except Exception as e:
            raise Exception(f'__get_pgn_data_frame -> ERROR: \n{e}\n{pgn_in} - {self.__username}')

    def __user_pieces(self):
        """
        Filtra y organiza las partidas del usuario en dos DataFrames separados por color de piezas.

        1. Elimina columnas innecesarias.
        2. Convierte los nombres de usuario a mayúsculas.
        3. Crea un DataFrame con las partidas donde el usuario manejó las piezas blancas.
        4. Organiza este DataFrame por resultado y Elo blanco.
        5. Crea un DataFrame con las partidas donde el usuario manejó las piezas negras.
        6. Organiza este DataFrame por resultado y Elo negro.
        7. Genera el listado de los oponentes solo si es instanciado como no oponente (usuario).

        **Returns**:
            None
        """
        try:
            for column in [env.START_TIME, env.ECO, env.MATCH, env.RULES, env.LINK, env.TIME_CONTROL]:
                try:
                    self.__data_frames_games = self.__data_frames_games.drop(columns=[column])
                except KeyError:
                    pass
            self.__data_frames_games[env.WHITE_USERNAME] = self.__data_frames_games[env.WHITE_USERNAME].str.upper()
            self.__data_frames_games[env.BLACK_USERNAME] = self.__data_frames_games[env.BLACK_USERNAME].str.upper()
            self.__white_pieces_games_df = self.__data_frames_games[
                self.__data_frames_games[env.WHITE_USERNAME] == self.__username.upper()
                ]
            self.__white_pieces_games_df = self.__white_pieces_games_df.groupby([env.WHITE_RESULT]) \
                .apply(lambda x: x.sort_values([env.WHITE_ELO])) \
                .reset_index(drop=True)
            self.__black_pieces_games_df = self.__data_frames_games[
                self.__data_frames_games[env.BLACK_USERNAME] == self.__username.upper()
                ]
            self.__black_pieces_games_df = self.__black_pieces_games_df.groupby([env.BLACK_RESULT]) \
                .apply(lambda x: x.sort_values([env.BLACK_ELO])) \
                .reset_index(drop=True)
            if not self.__opponent:
                self.__get_opponents()
        except Exception as e:
            raise Exception(f'__user_pieces -> ERROR: \n{e}')

    def __get_opponents(self):
        """
        Obtiene y almacena los nombres de los oponentes con los que el jugador ha jugado en sus partidas.

        Itera sobre las partidas en las que el jugador ha manejado las piezas blancas (__white_pieces_games_df)
        y las partidas en las que ha manejado las piezas negras (__black_pieces_games_df). Los nombres de los oponentes
        se almacenan en una lista llamada __opponents.

        Acciones:
        1. Iteración sobre Partidas:
            - Itera simultáneamente sobre las listas de oponentes correspondientes a las partidas en las que
              el jugador manejó las piezas blancas y las partidas en las que manejó las piezas negras.

        2. Almacenamiento de Oponentes:
            - Verifica si el nombre del oponente (jugador que manejó las piezas blancas o negras en una partida)
              ya está presente en la lista de oponentes (__opponents).
            - Si el nombre no está presente, se agrega a la lista __opponents.

        Uso:
        - Este método se utiliza internamente en la lógica de la clase para construir la lista de oponentes del jugador.
        """
        _opponents: List = []
        for white, black in zip(
                self.__white_pieces_games_df[env.BLACK_USERNAME].tolist(),
                self.__black_pieces_games_df[env.WHITE_USERNAME].tolist()
        ):
            if white not in _opponents:
                _opponents.append(white)
            if black not in _opponents:
                _opponents.append(black)
        self.__opponents[env.OPPONENTS] = _opponents
        self.__opponents[env.OPPONENTS_NUMBER] = len(_opponents)

    def set_opponents_new_info(self, key, value):
        """
        Propiedad que se ocupa de llenar desde instancias externas al objeto el diccionario
        *self.__opponents* usando *key* y *value* como clave y valor nuevos.

        **Excepciones**:
            Si la clave ya se encuentra en el diccionario, el proceso levantará una excepcion
            indicando que no puede cambiarse el contenido de dicha clave

        **Returns**:
            None
        """
        if key in self.__opponents:
            raise Exception(f'La clave {key} ya se encuentra en el diccionario')
        self.__opponents[key] = value

    @property
    def white_pieces_games_df(self):
        """
        Propiedad que devuelve el DataFrame con información general de partidas
        en las que el usuario juega con piezas blancas.

        **Returns**:
            pd.DataFrame: DataFrame con información general de partidas.
        """
        return self.__white_pieces_games_df

    @property
    def black_pieces_games_df(self):
        """
        Propiedad que devuelve el DataFrame con información general de partidas
        en las que el usuario juega con piezas negras.

        **Returns**:
            pd.DataFrame: DataFrame con información general de partidas.
        """
        return self.__black_pieces_games_df

    @property
    def data_frames_moves_games(self):
        """
        Propiedad que devuelve el DataFrame con información de movimientos de partidas.

        **Returns**:
            pd.DataFrame: DataFrame con información de movimientos de partidas.
        """
        return self.__data_frames_moves_games

    @property
    def opponents(self):
        """
        Propiedad que devuelve un diccionario con la informacion de los oponentes del jugador.

        **Returns**:
            Dict: Listado de oponentes.
        """
        return self.__opponents
