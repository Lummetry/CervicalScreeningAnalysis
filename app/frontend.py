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
from sklearn.linear_model import LogisticRegression

__VER__ = '0.0.2.0'

from bokeh.layouts import column, row, layout
from bokeh.plotting import figure
from bokeh.models import (
  ColumnDataSource, FileInput, Div, DataTable, TableColumn, FactorRange,
  Tabs, Panel, LabelSet, Range1d
  )
from bokeh.palettes import (
  Spectral11, Spectral4, Accent4, Pastel1_9, Pastel2_8
  )
from bokeh.transform import factor_cmap
import bokeh as bb

class FrontEnd:
  
  def __init__(self, log, debug=False, width=1000):
    self.log = log
    self.W = width
    self.debug = debug
    config = self.log.load_json(self.log.config_data['COLUMNS'])
    self.config = config
    self.col_config = config['COLUMNS']
    
    self.log.P("Using Bokeh v{}".format(bb.__version__))
    self.setup_tabs()
    self.setup_table_columns()
    self.setup_ds()
    
    return
  
  
  def setup_tabs(self):
    self.tabs = {
      'Incarcare si analiza' : self.get_layout_data,
      'Analiza inferentiala' : self.get_layout_infer,
      'Teste de inferenta'   : self.get_layout_tests
      }
    return

  def create_layout(self):
    tabs = []
    for name, factory in self.tabs.items():
      tabs.append(Panel(title=name, child=factory()))
    if self.debug:
      self.preprocess_data()
    return Tabs(tabs=tabs)

  
  
  def setup_ds(self):    
    dct_empty={x:[] for x in self.columns}
    self.DS = ColumnDataSource(data=dct_empty)
    self.importance = {
      'DS' : ColumnDataSource(data={'variables':[], 'importance':[]})
      }
    
    # now prepare counts dataset
    targets = 0
    self.counts_data = []    
    self.features = []
    for dct_field in self.col_config:
      if dct_field.get('FEATURE', 0) == 1:
        self.features.append(dct_field['FIELD'])
      if dct_field.get('CALCOUNT',0) == 1 or dct_field.get('TARGET', 0) == 1:
        dct_counts = {
          'DS' : ColumnDataSource(data={'value':[], 'count':[]}),
          }     
        for _k,_v in dct_field.items():
          dct_counts[_k] = _v
        if dct_field.get('TARGET_ANALYSIS', 0) == 1:
          dct_counts['DS_TARGET'] = ColumnDataSource(data={'value':[], 'count':[]})
        if dct_field.get('TARGET', 0) == 1:
          self.target_data = dct_counts
          self.target_field = dct_counts['FIELD']
          targets += 1
        else:
          self.counts_data.append(dct_counts)
    if targets == 0 or targets > 1:
      raise ValueError('TARGET fields defined in config {} out of required 1'.format(targets))
      
    self.target_positive = self.config['TARGET_VALUE'].upper()
    return
    
    
  def upload_data(self, attr, old, new):
    self.log.P("Loaded {:.1f} KB data.".format(len(new) / 1024))
    decoded = b64decode(new)
    f = io.BytesIO(decoded)          
    self.df = pd.read_csv(f)
    self.log.P("Received:\n{}".format(self.df.iloc[:5,:5]))
    self.preprocess_data()
    return
  
  def get_load_distrib(self):
    if self.config['DATE_FIELD'] not in list(self.df.columns):
      self.P("")
  
  
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
  
  def show_info(self, msg):
    self.div_status.text = msg
    self.log.P("MSG: {}".format(msg), color='y')
    return
    
  def get_values_and_counts(self, field, target_field=None, target_value=None):
    if target_field is not None:
      df_result = self.df[self.df[target_field] == target_value]
    else:
      df_result = self.df

    ser = df_result.groupby(field)[field].count()
    dtype = type(df_result[field].iloc[0])
    self.log.P("Calculating count data for '{}'[{}] on df {}".format(
        field, dtype, 
        'filterd with {}={}'.format(target_field, target_value) if target_field is not None else "unfiltered"))
    dct_data ={
        'value' : list(ser.index),
        'count' : list(ser.values)
        }
    return dct_data
  
  
  def calc_model(self):
    df_feats = self.df[self.features]
    df_x = pd.get_dummies(df_feats, columns=self.features)
    y_raw = self.df[self.target_data['FIELD']]
    y = y_raw.apply(lambda x: 1 if x == self.target_positive else 0)
    x = df_x.values
    model = LogisticRegression()
    model.fit(x,y)
    coefs = model.coef_
    fields = list(df_x.columns)
    self.log.P("Setting variables importance values")
    self.importance['DS'].data = {      
      'variables' : fields,
      'importance' : coefs.ravel(),
      }
    if 'FIGURE' in self.importance:
      self.importance['FIGURE'].x_range.factors = fields
    return
    
  
  def preprocess_data(self):
    self.log.P("Preprocessing df...")
    for dct_col in self.col_config:
      col = dct_col['FIELD']
      if dct_col['TYPE'] == 'STR' and col in self.columns:
        self.log.P("Transforming '{}'...".format(col))
        self.df[col] = self.df[col].apply(str.upper)
    self.log.P("Transfering df {} to cds".format(list(self.df.columns)))
    # check for autocalc CNP
    for dct_col in self.col_config:
      field_name = dct_col['FIELD']      
      found = False
      if field_name not in list(self.df.columns):        
        if 'AUTOCALC' in dct_col and dct_col['AUTOCALC'] in list(self.df.columns):
          found = True
      else:
        found = True
      if not found:
        self.show_info("Campul '{}' nu a fost gasit in coloanele incarcate {}".format(
          field_name, list(self.df.columns),
          ))
        return
      if dct_col.get('AUTOCALC', "") == 'CNP':
        self.df[field_name] = self.df['CNP'].apply(self.cnp_to_age)
    self.DS.data = self.df
    self.df_pos = self.df[self.df[self.target_data['FIELD']] == self.target_positive]
    self.show_info("Datele din fisierul sursa au fost incarcare cu succes. Total {} observatii din care {} pozitive.".format(
      self.df.shape[0],self.df_pos.shape[0]))
    # now calculate counts
    for dct_count_data in self.counts_data:      
      fld = dct_count_data['FIELD']
      dct_data = self.get_values_and_counts(
        field=fld,
        target_field=None, target_value=None
        )
      dct_count_data['DS'].data = dct_data
      if dct_count_data.get('TARGET_ANALYSIS', 0) == 1:
        dct_data_by_target = self.get_values_and_counts(
          field=fld,
          target_field=self.target_field, target_value=self.target_positive
        )        
        dct_count_data['DS_TARGET'].data = dct_data_by_target    
      self.set_figure_range(fld)
    
    # calculate for target
    tfld = self.target_data['FIELD']
    ser = self.df.groupby(tfld)[tfld].count()
    dtype = self.target_data['TYPE'].upper()
    self.log.P("Setting count data for '{}'[{}]".format(tfld, dtype))
    dct_data ={
        'value' : list(ser.index),
        'count' : list(ser.values)
        }
    self.target_data['DS'].data = dct_data
    
    self.set_figure_range(tfld)    
    
    self.calc_model()    
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
    
  
  
  def set_figure_range(self, field_name):
    dct_found = None
    is_target = False
    if field_name == self.target_data['FIELD']:
      dct_found = self.target_data
      is_target = True
    for dct_cnt in self.counts_data:
      if field_name == dct_cnt['FIELD']:
        dct_found = dct_cnt
    if dct_found is not None:
      unique_values = dct_found['DS'].data['value']
      if 'FIGURE' in dct_found and len(unique_values) > 0 and type(unique_values[0]) == str:
        self.log.P("Setting '{}' factors to x-range: {}".format(field_name, unique_values))
        dct_found['FIGURE'].x_range.factors = unique_values 
        if len(unique_values) <= 8:
          fill_color = factor_cmap(
            field_name='value', 
            palette=('green', 'purple','red') if is_target else Pastel2_8, 
            factors=unique_values
            )
          dct_found['PLOT'].glyph.fill_color = fill_color
          
        if 'FIGURE_TARGET' in dct_found:
          unique_values_target = dct_found['DS_TARGET'].data['value']
          self.log.P("Setting target figure '{}' factors to x-range: {}".format(field_name, unique_values_target))
          dct_found['FIGURE_TARGET'].x_range.factors = unique_values_target 
          if len(unique_values_target) <= 8:
            fill_color = factor_cmap(
              field_name='value', 
              palette=('green', 'purple','red') if is_target else Pastel2_8, 
              factors=unique_values_target
              )
            dct_found['PLOT_TARGET'].glyph.fill_color = fill_color
          
    return
  
  
  def get_per_label_stats(self):
    tfld = self.target_data['FIELD']
    tvals = self.df[tfld].unique()
    self.value_counts_by_target = {}
    for target in tvals:
      self.value_counts_by_target[target] = {}
      for dct_count_data in self.counts_data: 
        fld = dct_count_data['FIELD']
        dct_data = self.get_values_and_counts(
          field=fld,
          target_field=tfld, target_value=tvals,
          )
        self.value_counts_by_target[target][fld] = dct_data
    return
        
      
  
  def get_layout_data(self):
    H_LINE_1 = 20
    H_LINE_2 = 40
    H_GRAPH  = 220 
    W_INFO_LABEL = 100
    W_INFO_SIZE = 400
    W_BOX1 = W_INFO_LABEL + W_INFO_SIZE
    H_PLOT = 380
    TOOLS = 'save,hover'
    data_table = DataTable(
      source=self.DS, 
      columns=self.table_columns,
      width=W_INFO_LABEL + W_INFO_SIZE, 
      height=H_LINE_1 + H_LINE_2 + H_GRAPH,
      sizing_mode="stretch_width",
      )
    self.div_status = Div(text='', width=W_INFO_SIZE, height=H_LINE_2, background='lightyellow')
    div_status_label = Div(text='Informatii:', width=W_INFO_LABEL)
    info_row = row(div_status_label, self.div_status)
    
    inputs_and_status = []
    if self.debug:
      FN = self.log.config_data['DATA']
      self.df = self.log.load_dataframe(FN, folder='output')
      self.log.P("Loaded data from '{}':\n{}".format(FN, self.df.iloc[:5,:10]))
      inputs_and_status = [
          row(
            Div(text='Datele incarcate:', width=W_INFO_LABEL),
            Div(text=FN, width=W_INFO_SIZE, height=H_LINE_1, background="lightyellow")
            )            
        ]
    else:
      file_inp = FileInput(accept=".csv", width=W_INFO_SIZE,height=H_LINE_1)
      file_inp.on_change('value', self.upload_data)
      inputs_and_status = [row(
        Div(text='Incarcati fisierul:', width=W_INFO_LABEL),
        file_inp
        )]
      
    bar_list = self.config['BARS']
    all_bar_lines = []
    bars = []    
    width = W_BOX1 #self.W // len(bar_list)
    self.log.P("Plot width: {}".format(width))
    for dct_count_data in self.counts_data:
      bar = dct_count_data['FIELD']
      new_line = dct_count_data.get('NEWLINE', 0)      
      is_progress = dct_count_data.get('PROGRESS', 0)
      if new_line:
        if len(bars) == 0:
          raise ValueError('Cannot change bar line with no graphs before')
        all_bar_lines.append(row(bars))
        bars = []
      if bar in bar_list:
        bar_name = dct_count_data['TITLE']
        data_type = dct_count_data['TYPE'].upper()
        title = 'Analiza {} dupa '.format(
          "evolutiei procesului de screening" if is_progress else "distributiei totale" 
          ) + bar_name
        options = dict(
          title=title,
          sizing_mode='stretch_width',
          tools=TOOLS,
          width=width, 
          height=H_PLOT, 
          )
        if data_type in ["STR", "DATE"]:
          p = figure(
            x_range=['one','two', '...'],
            **options,
            ) 
          p.xaxis.major_label_orientation = np.pi/3
          p_labels = LabelSet(
            x='value', y='count', 
            text='count', level='glyph',
            x_offset=-13.5, y_offset=0, 
            source=dct_count_data['DS'], 
            render_mode='canvas'
            )   
          p.add_layout(p_labels)
        else:
          p = figure(
            **options
            ) 
        plot = p.vbar(x='value', top='count', source=dct_count_data['DS'], width=0.9)
        p.y_range.start = 0
        p.y_range.range_padding = 0.2
        p.xgrid.grid_line_color = None

        dct_count_data['FIGURE'] = p
        dct_count_data['PLOT'] = plot
        
        self.set_figure_range(bar)
        bars.append(p)
  
    all_bar_lines.append(row(bars))
    bars = []

    for dct_count_data in self.counts_data:
      bar = dct_count_data['FIELD']
      is_analysis_by_target = dct_count_data.get('TARGET_ANALYSIS', 0)
      if not is_analysis_by_target:
        continue
      new_line = dct_count_data.get('NEWLINE', 0)      
      is_progress = dct_count_data.get('PROGRESS', 0)
      if new_line:
        if len(bars) == 0:
          raise ValueError('Cannot change bar line with no graphs before')
        all_bar_lines.append(row(bars))
        bars = []
      if bar in bar_list:
        bar_name = dct_count_data['TITLE']
        data_type = dct_count_data['TYPE'].upper()
        title = 'Analiza {} dupa '.format(
          "evolutiei procesului de screening" if is_progress else "distributiei cazurilor {}".format(self.target_positive)
          ) + bar_name
        options = dict(
          title=title,
          sizing_mode='stretch_width',
          tools=TOOLS,
          width=width, 
          height=H_PLOT, 
          )
        if data_type in ["STR", "DATE"]:
          p = figure(
            x_range=['one','two', '...'],
            **options,
            ) 
          p.xaxis.major_label_orientation = np.pi/3
          p_labels = LabelSet(
            x='value', y='count', 
            text='count', level='glyph',
            x_offset=-13.5, y_offset=0, 
            source=dct_count_data['DS_TARGET'], 
            render_mode='canvas'
            )   
          p.add_layout(p_labels)
        else:
          p = figure(
            **options
            ) 
        plot = p.vbar(x='value', top='count', source=dct_count_data['DS_TARGET'], width=0.9)
        p.y_range.start = 0
        p.y_range.range_padding = 0.2
        p.xgrid.grid_line_color = None

        dct_count_data['FIGURE_TARGET'] = p
        dct_count_data['PLOT_TARGET'] = plot
        
        self.set_figure_range(bar)
        bars.append(p)
    
    all_bar_lines.append(row(bars))

        
    p_target = figure(
      title=self.target_data['TITLE'],
      x_range=['one','two', '...'],
      width=W_INFO_SIZE,
      height=H_GRAPH,
      tools=TOOLS
      )
    
    p_target.y_range.start = 0
    p_target.y_range.range_padding = 0.3
    plot_target = p_target.vbar(
      x='value', 
      top='count', 
      source=self.target_data['DS'], 
      width=0.9)

    labels = LabelSet(
      x='value', y='count', 
      text='count', level='glyph',
      x_offset=-13.5, y_offset=0, 
      source=self.target_data['DS'], 
      render_mode='canvas'
      )   
    p_target.add_layout(labels)
    self.target_data['FIGURE'] = p_target
    self.target_data['PLOT'] = plot_target
    target_row = row(
      Div(text='Distributia rezultatelor:',width=100),
      p_target
      )
    self.set_figure_range(self.target_data['FIELD'])
    
    inputs_and_status += [info_row, target_row]
    ctrl_input = column(inputs_and_status)
    bar_plots = column(all_bar_lines)
    data_ctrls = row(ctrl_input, data_table, sizing_mode="stretch_width")
    this_layout = column(data_ctrls, bar_plots, sizing_mode="stretch_width")
    
    # app_layout = layout(
    #   [
    #     [ctrl_input]
    #     [data_table],
    #   ], 
    #   # sizing_mode="scale_both"
    #   )
    
    return this_layout
  
  
  def get_layout_infer(self):
    descr = Div(text='In aceasta sectiune se pot observa rezultatele analizei inferentiale pe variabilele participantilor la screening')
    options = dict(
          title="Analiza importantei variabilelor analizate in determinarea incidentei ",
          sizing_mode='stretch_width',
          tools="save",
          width=self.W, 
          height=500, 
          )
    p = figure(
            x_range=['one','two', '...'],
            **options,
        ) 
    p.xaxis.major_label_orientation = np.pi/3

    plot = p.vbar(
      x='variables', 
      top='importance', 
      source=self.importance['DS'], 
      width=0.9
      )

    self.importance['FIGURE'] = p
    self.importance['PLOT'] = plot
    this_layout = column(descr, p, sizing_mode='stretch_width')
    
    return this_layout
  
  
  def get_layout_tests(self):
    descr = Div(text='In aceasta sectiune se pot testa ipoteze')
    this_layout = descr
    return this_layout
              