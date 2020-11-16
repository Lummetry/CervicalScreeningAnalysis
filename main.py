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

import numpy as np
import pandas as pd
from bokeh.io import curdoc
from app.frontend import get_layout

from libraries_pub.logger import Logger

l = Logger(
  lib_name='CXI',
  base_folder='.',
  app_folder='_local_cache',
  TF_KERAS=False,
  )

app_layout, ds = get_layout(l)

curdoc().add_root(app_layout)
curdoc().title = "CervixData"