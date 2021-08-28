#!/usr/bin/env python

import time

from util import Util
from route import Route
from route import RouteFactory
from ui import UITray
import config
import logging
import logging.config

def main():

    UITray.start()

    while not UITray.closed():
        try:
            if UITray.enabled():

                routes = config.routes()
                options = config.options()

                for route in routes:
                    # https://docs.microsoft.com/en-us/powershell/module/nettcpip/get-netroute
                    before = Util.run_ps_command(f'Get-NetRoute "{route.net_addr}" -PolicyStore All | ConvertTo-Json')
                    current_route = RouteFactory.create(
                        Util.dict_filter(before, Route.WIN_HEADER, Route.ROUTE_HEADER))
                    needs_exec = Route.is_diff(route, current_route[0])
                    logger.debug(f'current: {current_route}')
                    logger.debug(f'needs_exec: {needs_exec}')

                    if needs_exec:
                        # https://docs.microsoft.com/en-us/powershell/module/nettcpip/remove-netroute
                        Util.run_ps_command(f'Remove-NetRoute "{route.net_addr}" -Confirm:$false')

                        # https://docs.microsoft.com/en-us/powershell/module/nettcpip/new-netroute
                        Util.run_ps_command(f'New-NetRoute "{route.net_addr}" -NextHop "{route.nexthop}" -InterfaceAlias "{route.if_alias}" -RouteMetric 0 -PolicyStore ActiveStore -Confirm:$false  | ConvertTo-Json')

                        # https://docs.microsoft.com/en-us/powershell/module/nettcpip/get-netroute
                        after = Util.run_ps_command(f'Get-NetRoute "{route.net_addr}" | ConvertTo-Json')
                        current_route = Util.dict_filter(after, Route.WIN_HEADER, Route.ROUTE_HEADER)
                        logger.debug(f'current: {current_route}')

        except:
            logger.info('error')
        finally:
            time.sleep(int(options["interval_sec"]))

if __name__ == "__main__":

    logger = logging.getLogger('keepRoute')
    logger.debug(f"Starting keep-route ver.{Util.version}")

    try:
        main()
    except:
        import traceback
        logger.error(traceback.extract_stack())