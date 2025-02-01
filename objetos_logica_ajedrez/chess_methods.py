from objetos_logica_ajedrez import env_chess as env
import numpy as np


def handle_none(value):
    """
    Maneja valores None, convirtiéndolos en NaN.

    Args:
        value: Valor a ser manejado.

    **Returns**:
        np.nan or value: Retorna np.nan si el valor es None, de lo contrario, retorna el valor original.
    """
    return np.nan if value is None else value


def mapping_control(list_in, search_value):
    """
    Maneja la excepción KeyError al intentar acceder a un valor en un diccionario.

    Args:
        list_in: Diccionario o lista en el cual buscar el valor.
        search_value: Valor a buscar en el diccionario o lista.

    **Returns**:
        value or None: Retorna el valor correspondiente a la clave de búsqueda, o None si no se encuentra.
    """
    try:
        return list_in[search_value]
    except KeyError:
        return None
