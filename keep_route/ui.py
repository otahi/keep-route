import PySimpleGUI as sg
from psgtray import SystemTray

from route import RoutingTable
from route import RouteFactory
from route import Route
from util import Util
import config

import threading

# https://github.com/PySimpleGUI
# https://pysimplegui.readthedocs.io/en/latest/call%20reference/

ICON = Util.app_path('resources\\keep-route-128.png')

ICON_ENABLED = Util.app_path('resources\\keep-route.png')
ICON_DISABLED = Util.app_path('resources\\keep-route-disabled.png')


class UITray(object):

    _closed = False
    _enabled = True

    _routes = []

    @classmethod
    def closed(cls):
        return cls._closed

    @classmethod
    def enabled(cls):
        return cls._enabled

    @classmethod
    def routes(cls):
        return cls._routes

    @classmethod
    def show(cls):
        menu_disabled = ["NO_USE", ['Configure','!Enable', 'Disable', 'About', 'Exit']]
        menu_enabled  = ["NO_USE", ['Configure','Enable', '!Disable', 'About', 'Exit']]
        tooltip = 'keep-route menu'

        dummy = sg.Window('dummy', layout=[[], []], finalize=True, size=(10, 10))
        dummy.hide()

        tray = SystemTray(menu_disabled, icon = ICON_ENABLED, window = dummy, tooltip = tooltip)
        tray.show_message('Starting keep-route', '')

        menu_disabled_items = tray._convert_psg_menu_to_tray(menu_disabled)
        menu_enabled_items  = tray._convert_psg_menu_to_tray(menu_enabled)

        while True:
            event, values = dummy.read()
            print(f'event:{event}, values:{values}')

            if event == tray.key:
                event = values[0]

            if event in (sg.WIN_CLOSED, 'Exit'):
                break

            if event in ('Enable'):
                cls._enabled = True
                tray.tray_icon.menu._items = menu_disabled_items[0].submenu.items
                tray.tray_icon.update_menu()
                tray.change_icon(ICON_ENABLED)

            if event in ('Disable'):
                cls._enabled = True
                tray.tray_icon.menu._items = menu_enabled_items[0].submenu.items
                tray.tray_icon.update_menu()
                tray.change_icon(ICON_DISABLED)

            if event in ('Configure'):
                UIConfig.show()

            if event in ('About'):
                UIAbout.show()

        dummy.close()
        tray.close()

        cls._closed = True

    @classmethod
    def start(cls):
        sg.theme('SystemDefaultForReal')
        t = threading.Thread(target=cls.show)
        t.start()
        return t

class UIConfig(object):

    @staticmethod
    def _update_table(routes):
        routes_table = []
        for route in routes:
            routes_table.append(route.to_array())
        return routes_table

    @classmethod
    def show(cls):
        menu = sg.Menu([['&File', ['&About', 'E&xit']]])

        routing_table = sg.Table(
            RoutingTable.get(),
            headings =['Network', 'Nexthop', 'I/F Alias', 'I/F Index'],
            select_mode = sg.TABLE_SELECT_MODE_NONE,
            justification = 'left',
            auto_size_columns=False,
            col_widths= [20, 20, 20, 10],
        )

        routes_table = []
        routes = config.routes()
        for route in routes:
            routes_table.append(route.to_array())

        route_to_add = sg.Table(
            routes_table,
            headings =['Network', 'Nexthop', 'I/F Alias', 'I/F Index'],
            select_mode = sg.TABLE_SELECT_MODE_BROWSE,
            justification = 'left',
            auto_size_columns=False,
            selected_row_colors=("blue", "azure"),
            col_widths= [20, 20, 20, 10],
        )

        options = config.options()

        route_tab = sg.Tab('Route Table', [[routing_table]])
        route_config = sg.Tab('Route To Keep',
            [[sg.Button('Append'), sg.Button('Delete'), sg.Button('Modify')],
            [route_to_add]])
        option_config = sg.Tab('Option',
            [[
                sg.Text('Interval(sec)'),
                sg.InputText(options["interval_sec"], size=(5, 1), key="interval_sec")]])

        tabs = sg.TabGroup([[route_tab, route_config, option_config]])

        layout = [[menu], [tabs],[[],sg.Button('Save'),sg.Button('Cancel')]]

        window = sg.Window(
            'keep-route',
            layout,
            size=(800, 300),
            finalize=True,
            resizable=True,
            icon=ICON_ENABLED
        )

        while True:
            event, values = window.read()
            print(f'event:{event}, values:{values}')

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                break

            if event in ('Save'):
                config.save_routes(routes)
                config.save_options({ "interval_sec": values['interval_sec']})
                break

            if event in ('About'):
                UIAbout.show()
                break

            if event in ('Append'):
                result = UIRoute.edit()
                if result:
                    routes.append(Route(**result))

            if event in ('Modify'):
                selected = values[2][0]
                result = UIRoute.edit(routes[selected].to_dict())
                if result:
                    routes[selected] = Route(**result)

            if event in ('Delete'):
                selected = values[2][0]
                routes.pop(selected)

            routes_table = UIConfig._update_table(routes)
            route_to_add.update(routes_table)

        window.close()


class UIRoute(object):
    @classmethod
    def edit(cls, route = Route.template):
        layout = [
            [sg.Text('Network'), sg.InputText(route["net_addr"], size=(20, 1), key="net_addr")],
            [sg.Text('Nexthop'), sg.InputText(route["nexthop"], size=(20, 1), key="nexthop")],
            [sg.Text('Interface Alias'), sg.InputText(route["if_alias"], size=(20, 1), key="if_alias")],
            [sg.Text('Interface Index'), sg.InputText(route["if_index"], size=(20, 1), key="if_index"),
             sg.Text('(Optional)')],
            [sg.Button('OK'), sg.Button('Cancel')]
        ]

        window = sg.Window(
            'Route',
            layout,
            size=(400, 150),
            finalize=True,
            resizable=True,
            icon=ICON_ENABLED
        )

        result = None

        while True:
            event, values = window.read()
            print(f'event:{event}, values:{values}')

            if event in (sg.WIN_CLOSED, 'Cancel'):
                break

            if event in (sg.WIN_CLOSED, 'OK'):
                result = values
                break

        window.close()
        return result


class UIAbout(object):
    @classmethod
    def show(cls):
        layout = [
            [sg.Image(ICON, size=(128, 128))],
            [sg.Text('keep-route ' + Util.version())],
            [sg.Button('Help')],
            [sg.Button('Close')]
        ]

        window = sg.Window(
            'About',
            layout,
            size=(150, 240),
            finalize=True,
            resizable=True,
            icon=ICON_ENABLED
        )

        while True:
            event, values = window.read()

            if event in ('Help'):
                Util.open_home()

            if event in (sg.WIN_CLOSED, 'Close'):
                result = values
                break

        window.close()

# For debug
'''
from ui import UIDialog
UIDialog.show(f"text:{text}")
'''
class UIDialog(object):
    @classmethod
    def show(cls, text):
        layout = [
            [sg.Text(text)],
            [sg.Button('OK')]
        ]

        window = sg.Window('Dialog', layout, size=(1024, 1024), finalize=True, resizable=True, icon=ICON_ENABLED)
        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'OK'):
                break

if __name__ == '__main__':
    t = UITray.start()
    t.join()
