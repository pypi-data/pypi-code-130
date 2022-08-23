# -*- coding: utf-8 -*-


def get_colsInfo_df(df, cols=None):
    '''
    根据pd.DataFrame中的列cols识别对应列在MySQL中的字段类别
    参考：
        https://blog.csdn.net/tonydz0523/article/details/82529941
    '''

    if not cols is None:
        df = df.reindex(columns=cols)
    cols = df.columns.tolist()

    types = df.dtypes
    colsInfo, colsType = [], []
    for col in cols:
        if 'int' in str(types[col]):
            char = col + ' INT'
            char_ = '%s'
        elif 'float' in str(types[col]):
            char = col + ' FLOAT'
            char_ = '%s'
        elif 'object' in str(types[col]):
            char = col + ' VARCHAR(255)'
            char_ = '%s'
        elif 'datetime' in str(types[col]):
            char = col + ' DATETIME'
            char_ = '%s'
        colsInfo.append(char)
        colsType.append(char_)
    colsInfo, colsType = ','.join(colsInfo), ','.join(colsType)

    return colsInfo, colsType


def df_to_sql_pymysql(df, conn, db_name, tb_name, loc='new',
                      cols=None):
    '''
    pd.DataFrame存入MySQL数据库中
    loc:
        若为'new'，则新建表；
        若为'tail'，则插入表的尾部；
        若为'update'，则将已存在的数据更新；
        若为'head'，则插入表的前部
    参考：
        https://blog.csdn.net/tonydz0523/article/details/82529941
    '''

    if not cols is None:
        df = df.reindex(columns=cols)
    else:
        cols = df.columns.tolist()

    cur = conn.cursor()

    # 若数据库不存在，则新建
    cur.execute('CREATE DATABASE IF NOT EXISTS {};'.format(db_name))
    # cur.execute('USE {};'.format(db_name))
    conn.select_db(db_name)

    colsInfo, colsType = get_colsInfo_df(df, cols=cols)

    # 表不存在或强制建新表
    if loc == 'new':
        # 创建table
        cur.execute('DROP TABLE IF EXISTS {};'.format(tb_name))
        cur.execute('CREATE TABLE {a}({b});'.format(a=tb_name, b=colsInfo))
    cur.execute('CREATE TABLE IF NOT EXISTS {a}({b});'.format(
                                                    a=tb_name, b=colsInfo))

    # 数据更新
    if loc in ['new', 'tail']:
        # 批量插入新数据
        values = df.values.tolist()
        values = [tuple(x) for x in values]
        cur.executemany('INSERT INTO {a} ({b}) VALUES ({c});'.format(
                        a=tb_name, b=','.join(cols), c=colsType),
                        values)
    elif loc == 'update':
        pass
    elif loc == 'head':
        pass

    cur.close()
    conn.commit()
