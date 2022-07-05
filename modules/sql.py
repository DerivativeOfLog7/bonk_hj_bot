from __future__ import annotations
import sqlite3
import config.CONFIG
from typing import Union

_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS chats (
chat_id INT8 PRIMARY KEY,
allow_top_cmd BOOLEAN DEFAULT 1 NOT NULL,
show_help_msgs BOOLEAN DEFAULT 1 NOT NULL,
announce_top_user BOOLEAN DEFAULT 0 NOT NULL
);""",
    """CREATE TABLE IF NOT EXISTS bonks (
user_id INT8 NOT NULL,
chat_id INT8 NOT NULL,
message_id INT8 NOT NULL,
PRIMARY KEY (user_id, chat_id, message_id),
FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
);"""
)


_con = sqlite3.connect(config.CONFIG.PATH_TO_DB)
_con.isolation_level = None
_cur = _con.cursor()
_cur.execute("PRAGMA foreign_keys = ON")
for i in _SCHEMA:
    _cur.execute(i)


def run_query_s(query: Union[str, tuple[str, ...]], params: Union[tuple, tuple[tuple, ...]] = ()) -> Union[sqlite3.Cursor, list[sqlite3.Cursor], None]:
    """Run single or multiple queries
    If query is a tuple and params is a tuple of tuples of same length, it runs all couples of queries and tuples
    If query is a tuple and params a tuple of parameters, it runs all the queries with the same params
    If query is a string and params a tuple of parameters, it runs the single query with the parameters
    Returns a single or a list of cursors"""
    # Who wants some spaghetti with tuna sauce?

    if isinstance(params, tuple):
        # If multiple queries
        if isinstance(query, tuple):
            res = []
            # If params is empty, simply run all queries
            if len(params) == 0:
                for q in query:
                    res.append(_cur.execute(q))
            elif isinstance(params[0], tuple):
                # If params is tuple of tuples and same length as query, run each query and params couple
                if len(query) == len(params):
                    for q, p in query, params:
                        res.append(_cur.execute(q, p))
                else:
                    raise ValueError("query and params size mismatch")
            else:
                # If params is a single set of params, run all queries with that set of params
                for q in query:
                    res.append(_cur.execute(q, params))
        elif isinstance(query, str):
            if len(params) == 0:
                res = _cur.execute(query)
            elif isinstance(params[0], tuple):
                raise ValueError("params can't be a tuple of tuple if query is a string")
            else:
                res = _cur.execute(query, params)
        else:
            raise ValueError("Invalid type for query")

        return res
    else:
        raise TypeError("Invalid params type")


def fetchone(query: str, params: tuple = ()) -> Union[int, str, float, None]:
    """Run a single query with params and executes fetchone() on it
    If there's no result, it returns None
    If there's a single result, it returns that single result
    If there are multiple results, it returns a tuple of results"""
    res = _cur.execute(query, params).fetchone()
    if res is None:
        res = None
    elif len(res) == 1:
        res = res[0]

    return res
