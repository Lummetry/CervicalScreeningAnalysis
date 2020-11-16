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
import pandas as pd
from base64 import b64decode
import io

from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, FileInput, Div, DataTable


def get_layout(log):
  DS = ColumnDataSource()
  data_table = DataTable(source=DS, width=800)
  
  
  file_inp_label = Div(text='Load screening data:')
  file_inp = FileInput(accept=".csv")
  
  def upload_data(attr, old, new):
    log.P("Loaded {:.1f} KB data.".format(len(file_inp.value) / 1024))
    decoded = b64decode(file_inp.value)
    f = io.BytesIO(decoded)          
    df = pd.read_csv(f)
    DS.data = df
    
  file_inp.on_change('value', upload_data)
  
  def update_ds():
    DS.data = dict(
      )
  
  
  app_layout = layout([
      [file_inp_label, file_inp],
      [data_table],
  ], sizing_mode="scale_both")
  
  return app_layout, DS
  