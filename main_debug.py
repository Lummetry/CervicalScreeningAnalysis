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

from bokeh.plotting import  output_file, show
from app.frontend import FrontEnd

from libraries_pub.logger import Logger

OUTPUT_FILE = 'debug.html'

l = Logger(
  lib_name='CXId',
  config_file='_config/config_debug.txt',
  TF_KERAS=False,
  use_colors=True,
  )

output_file(OUTPUT_FILE, title='CervixData [Debug]')
l.P("Using DEBUG version '{}'".format(OUTPUT_FILE))

eng = FrontEnd(log=l, debug=True)
app_layout = eng.get_layout()

show(app_layout)