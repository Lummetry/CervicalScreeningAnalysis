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
import numpy as np
from base64 import b64decode
import io
from datetime import datetime

from bokeh.layouts import column, row, layout
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FileInput, Div, DataTable, TableColumn
import bokeh as bb

class FrontEnd:
  
  def __init__(self, log, debug=False):
    self.log = log
    self.debug = debug
    config = self.log.load_json(self.log.config_data['COLUMNS'])
    self.config = config
    self.col_config = config['COLUMNS']
    
    self.log.P("Using Bokeh v{}".format(bb.__version__))
    self.setup_table_columns()
    self.setup_ds()
    return
  
  def setup_ds(self):    
    dct_empty={x:[] for x in self.columns}
    self.DS = ColumnDataSource(data=dct_empty)
    return
    
    
  def upload_data(self, attr, old, new):
    self.log.P("Loaded {:.1f} KB data.".format(len(new) / 1024))
    decoded = b64decode(new)
    f = io.BytesIO(decoded)          
    self.df = pd.read_csv(f)
    self.log.P("Received:\n{}".format(self.df.iloc[:5,:5]))
    self.preprocess_data()
    return
  
  def setup_table_columns(self):
    self.columns = [x['FIELD'] for x in self.col_config]
    tab_cols = []
    self.display_cols = []
    for i, col in enumerate(self.columns):
      dct_col = self.col_config[i]
      if dct_col['DISPLAY'] == 1:
        tab_cols.append(TableColumn(field=col, title=dct_col['TITLE']))
        self.display_cols.append(col)
    self.table_columns = tab_cols
    return
        
  def preprocess_data(self):
    self.log.P("Preprocessing df...")
    for col in list(self.df.columns):
      if type(self.df[col][0]) == str:
        self.df[col] = self.df[col].apply(str.upper)
    self.log.P("Transfering df {} to cds".format(list(self.df.columns)))
    # check for autocalc CNP
    for dct_col in self.col_config:
      if dct_col.get('AUTOCALC', "") == 'CNP':
        field_name = dct_col['FIELD']
        self.df[field_name] = self.df['CNP'].apply(self.cnp_to_age)
    self.DS.data = self.df
    return
    
    
  def cnp_to_age(self, cnp):
    scnp = str(cnp)
    year = datetime.now().year
    cyear = scnp[1:3]
    if scnp[0] == '2':
      cyear = '19' + cyear
    elif scnp[0] == '4':
      cyear = '18' + cyear
    elif scnp[0] == '6':
      cyear = '20' + cyear
    return year - int(cyear)
    
  
    
  def get_layout(self):
    data_table = DataTable(
      source=self.DS, 
      columns=self.table_columns,
      width=500, 
      height=200,
      )
    
    if self.debug:
      FN = self.log.config_data['DATA']
      self.df = self.log.load_dataframe(FN, folder='output')
      self.preprocess_data()
      self.log.P("Loaded '{}':\n{}".format(FN, self.df.iloc[:5,:10]))
      ctrl_input = column(
          Div(text='Loaded data:', width=500),
          Div(text=FN, width=500, background="aqua")
        )
    else:
      file_inp = FileInput(accept=".csv", width=250)
      file_inp.on_change('value', self.upload_data)
      ctrl_input = row([
        Div(text='Incarcati fisierul:', width=250),
        file_inp
        ])
      
    bar_list = self.config['BARS']
    bars = []
    for dct_field in self.col_config:
      bar = dct_field['FIELD']
      if bar in bar_list:
        bar_name = dct_field['TITLE']
        x_list = list(self.df[bar].unique())
        y_list = [self.df[self.df[bar] == x].shape[0] for x in x_list]
        p = figure(width=500)
        # if type(x_list[0]) == str:
        #   p = figure(title=bar_name, x_range=x_list, width=500, height=300, tools='') #x_range=x_list, y_range=y_list)
        #   p.xaxis.major_label_orientation = np.pi/3
        #   # p.xaxis.major_label_orientation = "vertical"
        # else:
        #   p = figure(title=bar_name, width=500, height=300, tools='') #x_range=x_list, y_range=y_list)
        p.vbar(x=bar, top='count', source=self.DS_CNTS, width=0.9)
        bars.append(p)
    
    bar_plots = row(bars)
    data_ctrls = row(ctrl_input, data_table)
    app_layout = column(data_ctrls, bar_plots)
    
    # app_layout = layout(
    #   [
    #     [ctrl_input]
    #     [data_table],
    #   ], 
    #   # sizing_mode="scale_both"
    #   )
    
    return app_layout
  