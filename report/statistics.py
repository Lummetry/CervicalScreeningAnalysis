import os
from libraries_pub.logger import Logger

__VER__ = "1.0.0.0"

def statistics_data_recoltarii(df):
  #data recoltarii
  df_grouped = df.groupby(['DATA_RECOL']).size().reset_index(name='counts')
  _min = df_grouped['counts'].min()
  argmax = df_grouped['counts'].argmax()
  _max = df_grouped.iloc[argmax]['counts']
  _max_date = df_grouped.iloc[argmax]['DATA_RECOL']
  _mean = df_grouped['counts'].mean()
  nr_days_with_1_recol = df_grouped[df_grouped['counts'] == 1].shape[0]
  nr_days_with_5_or_less_recol = df_grouped[df_grouped['counts'] <= 5].shape[0]
  nr_days_between_5_and_10 = df_grouped[(df_grouped['counts'] >= 5) & (df_grouped['counts'] < 10)].shape[0]
  nr_days_between_10_and_50 = df_grouped[(df_grouped['counts'] >= 50) & (df_grouped['counts'] < 100)].shape[0]
  nr_days_more_100 = df_grouped[df_grouped['counts'] >= 100].shape[0]
  
  l.p(file)
  l.p(' * ' + 'DATA_RECOL stats:')
  l.p(3 * ' ' + 'Numar minim de recoltari intr-o zi: {}'.format(_min), noprefix=True)
  l.p(3 * ' ' + 'Numar maxim de recoltari intr-o zi: {} (pe {})'.format(_max, _max_date), noprefix=True)
  l.p(3 * ' ' + 'Numar mediu intr-o zi: {:.2f}'.format(_mean), noprefix=True)
  l.p(3 * ' ' + 'Numar de zile cu o singura recoltare: {}'.format(nr_days_with_1_recol), noprefix=True)
  l.p(3 * ' ' + 'Numar de zile cu pana la 5 recoltari: {}'.format(nr_days_with_5_or_less_recol), noprefix=True)
  l.p(3 * ' ' + 'Numar de zile in care s-au facut intre 5 si 10 recoltari: {}'.format(nr_days_between_5_and_10), noprefix=True)
  l.p(3 * ' ' + 'Numar de zile in care s-au facut intre 10 si 50 recoltari: {}'.format(nr_days_between_10_and_50), noprefix=True)
  l.p(3 * ' ' + 'Numar de zile in care s-au facut peste 100 de recoltari: {}'.format(nr_days_more_100), noprefix=True)
  return
  

def statistics_judet(df, is_positive):
  df_grouped = df.groupby(['JUD']).size().reset_index(name='counts')
  argmin = df_grouped['counts'].argmin()  
  _min = df_grouped.iloc[argmin]['counts']
  _min_jud = df_grouped.iloc[argmin]['JUD']
  argmax = df_grouped['counts'].argmax()
  _max = df_grouped.iloc[argmax]['counts']
  _max_jud = df_grouped.iloc[argmax]['JUD']
  _mean = df_grouped['counts'].mean()  
    
  l.p(file)
  l.p(' * ' + 'JUD stats:')
  l.p(3 * ' ' + 'Numar minim de recoltari: {} (Judet: {})'.format(_min, _min_jud), noprefix=True)
  l.p(3 * ' ' + 'Numar maxim de recoltari: {} (Judet: {})'.format(_max, _max_jud), noprefix=True)
  l.p(3 * ' ' + 'Numar mediu de recoltari: {:.2f}'.format(_mean), noprefix=True)
  
  lbl = '' if not is_positive else ' cu rezultate pozitive'
  lst_range = list(range(0, 10000, 50))
  for i in list(range(len(lst_range)))[:-1]:
    _min = lst_range[i]
    _max = lst_range[i+1]
    df_range = df_grouped[(df_grouped['counts'] >= _min) & (df_grouped['counts'] < _max)]
    nr = df_range.shape[0]
    lst = df_range['JUD'].tolist()
    if nr > 0:
      l.p(3 * ' ' + 'Numar de judete in care s-au facut intre {} si {} recoltari{}: {} ({})'.format(_min, _max, lbl, nr, ', '.join(lst)), noprefix=True)
  return


def statistics_varsta(df):
  #varsta
  df_grouped = df.groupby(['VARSTA']).size().reset_index(name='counts')
  _min_age = df_grouped[df_grouped['VARSTA'] > 0]['VARSTA'].min()
  _max_age = df_grouped['VARSTA'].max()
  _mean = df_grouped['counts'].mean()
  
  l.p(file)
  l.p(' * ' + 'VARSTA stats:')
  l.p(3 * ' ' + 'Varsta minima: {}'.format(_min_age), noprefix=True)
  l.p(3 * ' ' + 'Varsta maxima: {}'.format(_max_age), noprefix=True)
  l.p(3 * ' ' + 'Varsta medie:  {:.2f}'.format(_mean), noprefix=True)
  
  lst_range = list(range(0, 101, 10))
  for i in list(range(len(lst_range)))[:-1]:
    _min = lst_range[i]
    _max = lst_range[i+1]
    df_range = df_grouped[(df_grouped['VARSTA'] >= _min) & (df_grouped['VARSTA'] < _max)]
    nr = df_range['counts'].sum()
    if nr > 0:
      l.p(3 * ' ' + 'Pacienti cu varsta intre {} si {}: {}'.format(_min, _max, nr), noprefix=True)
  return


if __name__ == '__main__':
  l = Logger(
    lib_name='CXId',
    lib_ver=__VER__,
    config_file='_config/config_debug.txt',
    TF_KERAS=False,
    use_colors=True,
    )
  
  path_data = os.path.join(l._get_cloud_base_folder('DROPBOX'), '_cerv_screening_data')
  
  CEDICROM1_HPV = 'cedicrom1_hpv.csv'
  CEDICROM1_PAP = 'cedicrom1_pap.csv'
  CEDICROM2_CAREHPV = 'cedicrom2_carehpv.csv'
  CEDICROM2_HPV = 'cedicrom2_hpv.csv'
  
  file = CEDICROM2_HPV
  df = l.load_dataframe(os.path.join(path_data, file))
  df['JUD'] = df['JUD'].str.upper()
  
  statistics_data_recoltarii(df)
  statistics_judet(df, is_positive=False)
  statistics_varsta(df)
  
  df = df[df['REZULTAT'] == 'pozitiv']
  statistics_judet(df, is_positive=True)
  statistics_varsta(df)
  
  
  
  