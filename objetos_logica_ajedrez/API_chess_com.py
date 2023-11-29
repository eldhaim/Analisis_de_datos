import io
import numpy as np
import pandas as pd
import requests as rq
import json
from objetos_logica_ajedrez import env_chess as env
from http import HTTPStatus
from typing import List, Optional, Union
from chess import pgn, SQUARE_NAMES


# Función para manejar valores None
def handle_none(value):
    return np.nan if value is None else value


# Función para manejar la excpecion KeyError
def mapping_control(list_in, search_value):
    try:
        return list_in[search_value]
    except KeyError:
        return None


class ChessCom:
    def __init__(self, username: str = None, year: int = None, month: int = None):
        self.__username: str = username
        self.__year: int = year
        self.__month: int = month
        self.__response: rq = None
        self.__pgn: List[pgn] = []
        self.__json_response: json = None
        self.__games_list: List = []
        self.__games: List = self.__get_monthly_games()
        self.__pgn_info_tags: List = []
        self.__pgn_info_tags_columns: List = []
        self.__pgn_info_moves: List = []
        self.__data_frames_games: Optional[pd.DataFrame] = self.__get_data_frame_dict()
        self.__data_frames_moves_games: Optional[pd.DataFrame] = pd.DataFrame(
            self.__pgn_info_moves,
            columns=[
                env.URL, env.FROM, env.PIECE, env.TO, env.CAPTURED
            ]
        )

    def __get_monthly_games(self) -> List:
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

    def __get_data_frame_dict(self) -> pd.DataFrame:
        try:
            if len(self.__games) == 0:
                raise Exception('Juegos no encontrados')
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
            print(f'__get_data_frame_list -> ERROR: \n{e}')
            raise e

    def __create_data_structure(self, game):
        try:
            # print(f'__create_data_structure -> MAPPING: \n{game}')
            # Dividir en matrices
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
            except KeyError as e:
                # print(f'__create_data_structure -> KeyError:{e}')
                pass
            except Exception as e:
                # print(f'__create_data_structure -> Exception:{e}')
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
            print(f'__create_data_structure -> ERROR: \n{e}')
            raise e

    def __get_pgn_data_frame(self, pgn_in, url):
        _pgn_tags = {}
        _pgn_game = pgn.read_game(io.StringIO(pgn_in))
        _board = _pgn_game.board()
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
                self.__pgn_info_moves.append([url, uci_move[:-2], piece.symbol(), to_square, str(_captured_piece)])
            else:
                self.__pgn_info_moves.append([url, uci_move[:-2], None, to_square, str(_captured_piece)])
            _board.push(move)
        matches = env.TAG_PATTERN.findall(pgn_in)
        for match in matches:
            key, value = match
            _pgn_tags[key] = value
        if len(_pgn_tags.keys()) > len(self.__pgn_info_tags_columns):
            self.__pgn_info_tags_columns = list(_pgn_tags.keys())
        self.__pgn_info_tags = list(_pgn_tags.values())

    @property
    def get_data_frames_games(self):
        return self.__data_frames_games

    @property
    def get_data_frames_moves_games(self):
        return self.__data_frames_moves_games



