import pandas as pd
import os

# 设置文件路径
adult_excel_path = "c:\\Users\\kerben\\Desktop\\重新修改\\data\\输入和输出示例_成年人评价标准(1).xlsx"
elderly_excel_path = "c:\\Users\\kerben\\Desktop\\重新修改\\data\\输入和输出示例_老年人评价标准(1).xlsx"

# 检查文件是否存在
if os.path.exists(adult_excel_path):
    print("===== 成年人评价标准文件 ======")
    try:
        # 读取Excel文件
        df_adult = pd.read_excel(adult_excel_path)
        # 显示表头
        print("表头信息:", list(df_adult.columns))
        # 显示前5行数据
        print("前5行数据:")
        print(df_adult.head())
        print("\n数据类型信息:")
        print(df_adult.dtypes)
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
else:
    print("成年人评价标准文件不存在")

print("\n" + "="*50 + "\n")

if os.path.exists(elderly_excel_path):
    print("===== 老年人评价标准文件 ======")
    try:
        # 读取Excel文件
        df_elderly = pd.read_excel(elderly_excel_path)
        # 显示表头
        print("表头信息:", list(df_elderly.columns))
        # 显示前5行数据
        print("前5行数据:")
        print(df_elderly.head())
        print("\n数据类型信息:")
        print(df_elderly.dtypes)
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
else:
    print("老年人评价标准文件不存在")