import pandas as pd
import numpy as np

##########           white          #################
df_w = pd.read_excel(r'C:/Users/Mihuier/Desktop/white.xlsx')
df_w_test=df_w.iloc[:118,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_w_test.to_excel(r'C:/Users/Mihuier/Desktop/white_test.xlsx',index=False)

df_w_train=df_w.iloc[119:236,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_w_train.to_excel(r'C:/Users/Mihuier/Desktop/white_train.xlsx',index=False)

df_w_val=df_w.iloc[237:1183,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_w_val.to_excel(r'C:/Users/Mihuier/Desktop/white_val.xlsx',index=False)

##########           pink           ##################
df_p = pd.read_excel(r'C:/Users/Mihuier/Desktop/pink.xlsx')
df_p_test=df_p.iloc[:20,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_p_test.to_excel(r'C:/Users/Mihuier/Desktop/pink_test.xlsx',index=False)

df_p_train=df_p.iloc[21:40,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_p_train.to_excel(r'C:/Users/Mihuier/Desktop/pink_train.xlsx',index=False)

df_p_val=df_p.iloc[41:196,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_p_val.to_excel(r'C:/Users/Mihuier/Desktop/pink_val.xlsx',index=False)

##########           yellow           ##################
df_y = pd.read_excel(r'C:/Users/Mihuier/Desktop/yellow.xlsx')
df_y_test=df_y.iloc[:50,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_y_test.to_excel(r'C:/Users/Mihuier/Desktop/yellow_test.xlsx',index=False)

df_y_train=df_p.iloc[51:100,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_y_train.to_excel(r'C:/Users/Mihuier/Desktop/yellow_train.xlsx',index=False)

df_y_val=df_p.iloc[101:507,:10] #冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
df_y_val.to_excel(r'C:/Users/Mihuier/Desktop/yellow_val.xlsx',index=False)

