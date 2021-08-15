
import json
from io import TextIOWrapper
from json import JSONDecodeError

from threading import Lock

from util import Util

class Route(object):
    template = {
        "net_addr" : '',
        "nexthop"  : '',
        "if_alias" : '',
        "if_index" : ''
    }

    WIN_HEADER =   ["DestinationPrefix", "NextHop", "InterfaceAlias", "InterfaceIndex"]
    ROUTE_HEADER = ["net_addr",          "nexthop", "if_alias",       "if_index"      ]

    @property
    def net_addr(self):
        return self._net_addr

    @property
    def nexthop(self):
        return self._nexthop

    @property
    def if_alias(self):
        return self._if_alias

    @property
    def if_index(self):
        return self._if_index

    def __str__(s):
        return f"net_addr:{s._net_addr}, nexthop:{s._nexthop}, if_alias:{s._if_alias}, if_index:{s._if_index}"

    def __repr__(s):
        return f"Route(net_addr={s._net_addr}, nexthop={s._nexthop}, if_alias={s._if_alias}, if_index={s._if_index})"

    def to_dict(self):
        return {
            "net_addr": self._net_addr,
            "nexthop" : self._nexthop,
            "if_alias": self._if_alias,
            "if_index": self._if_index,
        }

    def to_array(self):
        return [ self._net_addr, self._nexthop, self._if_alias, self._if_index ]

    def __init__(self, net_addr, nexthop, if_alias, if_index = -1):
        self._net_addr = net_addr
        self._nexthop = nexthop
        self._if_alias = if_alias
        self._if_index = if_index

    @classmethod
    def is_diff(cls, route_a, route_b):
        try:
            return not (
                route_a.net_addr == route_b.net_addr and
                route_a.nexthop == route_b.nexthop and
                (route_a.if_alias == route_b.if_alias or route_a.if_index == route_b.if_index))
        except KeyError:
            return True
        except:
            return False

class RoutingTable(object):
    routing_table = []
    lock = Lock()

    @classmethod
    def update(cls):

        _routing_table = Util.run_ps_command(f'Get-NetRoute -PolicyStore All | ConvertTo-Json')

        cls.lock.acquire()
        cls.routing_table = RouteFactory.create(
            Util.dict_filter(
                _routing_table,
                Route.WIN_HEADER,
                Route.ROUTE_HEADER))
        cls.lock.release()

    @classmethod
    def get(cls):
        routing_table = []

        cls.update()

        for route in cls.routing_table:
            routing_table.append(route.to_array())

        return routing_table

class RouteFactory(object):
    @classmethod
    def create(cls, routes):

        _routes = []

        if isinstance(routes, Route):
            pass
        elif isinstance(routes, TextIOWrapper):
            try:
                routes = json.load(routes)
            except JSONDecodeError as e:
                pass

        for route in routes:
            if "if_index" in route:
                _routes.append(Route(route["net_addr"], route["nexthop"], route["if_alias"], route["if_index"]))
            else:
                _routes.append(Route(route["net_addr"], route["nexthop"], route["if_alias"]))

        return _routes