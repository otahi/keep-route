#!/usr/bin/env python

import PyInstaller.__main__

PyInstaller.__main__.run([
    'keep_route.spec',
    '--onefile',
    '--noconfirm',
    '--clean',
])
