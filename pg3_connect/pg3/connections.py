import os
from functools import lru_cache
from typing import Type, Any, Optional, Callable, Awaitable, Dict

import psycopg as pg
import psycopg_pool
from config_reader import get_config
from psycopg import Cursor, AsyncConnection
from psycopg.abc import AdaptContext
from psycopg.rows import Row, RowFactory
from psycopg_pool import ConnectionPool, AsyncConnectionPool
from psycopg_pool.base import BasePool

assert (base_node := os.getenv('PG_NODE')), 'PG_NODE must be present in project.env'
pass


@lru_cache()
def get_pool(**kwargs):
    return ConnectionPool(
        get_config(f'{base_node}.connection_pool', conf_string_delimiter=' ', **kwargs)
    )


@lru_cache()
def get_async_pool(
        *,
        open_: bool = True,
        connection_class: Type[AsyncConnection[Any]] = AsyncConnection,
        configure: Optional[Callable[[AsyncConnection[Any]], Awaitable[None]]] = None,
        reset: Optional[Callable[[AsyncConnection[Any]], Awaitable[None]]] = None,
        min_size: int = 4,
        max_size: Optional[int] = None,
        name: Optional[str] = None,
        timeout: float = 30.0,
        max_waiting: int = 0,
        max_lifetime: float = 60 * 60.0,
        max_idle: float = 10 * 60.0,
        reconnect_timeout: float = 5 * 60.0,
        reconnect_failed: Optional[
            Callable[[BasePool[AsyncConnection[Any]]], None]
        ] = None,
        num_workers: int = 3,
        **kwargs: Optional[Dict[str, Any]]) -> psycopg_pool.AsyncConnectionPool:
    return AsyncConnectionPool(
        get_config(f'{base_node}.connection_pool', conf_string_delimiter=' ', **kwargs),
        open=open_,
        connection_class=connection_class,
        configure=configure,
        reset=reset,
        min_size=min_size,
        max_size=max_size,
        name=name,
        timeout=timeout,
        max_waiting=max_waiting,
        max_lifetime=max_lifetime,
        max_idle=max_idle,
        reconnect_timeout=reconnect_timeout,
        reconnect_failed=reconnect_failed,
        num_workers=num_workers
    )


@lru_cache()
def connect(
        *,
        autocommit: bool = False,
        prepare_threshold: int | None = 5,
        row_factory: RowFactory[Row] | None = None,
        cursor_factory: Type[Cursor[Row]] | None = None,
        context: AdaptContext | None = None,
        **kwargs: Any
) -> pg.Connection:
    return pg.connect(
        get_config(f'{base_node}.connection', conf_string_delimiter=' ', **kwargs),
        autocommit=autocommit,
        prepare_threshold=prepare_threshold,
        row_factory=row_factory,
        cursor_factory=cursor_factory,
        context=context
    )
