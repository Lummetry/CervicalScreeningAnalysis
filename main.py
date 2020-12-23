# -*- coding: utf-8 -*-
"""
Copyright 2019 Lummetry.AI (Knowledge Investment Group SRL). All Rights Reserved.


* NOTICE:  All information contained herein is, and remains
* the property of Knowledge Investment Group SRL.  
* The intellectual and technical concepts contained
* herein are proprietary to Knowledge Investment Group SRL
* and may be covered by Romanian and Foreign Patents,
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Knowledge Investment Group SRL.


@copyright: Lummetry.AI
@author: Lummetry.AI - Andrei
@project: 
@description: 

"""
import os
from bokeh.io import curdoc
from app.frontend import FrontEnd
from app.frontend import __VER__ as version
from libraries_pub.logger import Logger

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_PATH)

l = Logger(
  lib_name='CXI',
  config_file='_config/config.txt',
  lib_ver=version,
  TF_KERAS=False,
  use_colors=False,
  )

eng = FrontEnd(log=l, debug=False)
app_layout = eng.create_layout()

curdoc().add_root(app_layout)
curdoc().title = "CervixData"