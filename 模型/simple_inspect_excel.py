import pandas as pd
import os

# 设置文件路径
adult_excel_path = "c:\\Users\\kerben\\Desktop\\重新修改\\data\\输入和输出示例_成年人评价标准(1).xlsx"
elderly_excel_path = "c:\\Users\\kerben\\Desktop\\重新修改\\data\\输入和输出示例_老年人评价标准(1).xlsx"

# 读取并显示成年人评价标准
print("===== 成年人评价标准文件 ======")
try:
    # 读取第一个工作表
    xl = pd.ExcelFile(adult_excel_path)
    print(f"工作表名称: {xl.sheet_names}")
    
    # 读取第一个工作表的数据
    df = pd.read_excel(xl, sheet_name=xl.sheet_names[0], header=None)
    print("\n前10行数据:")
    for i in range(min(10, len(df))):
        print(f"行 {i+1}: {df.iloc[i].tolist()}")
except Exception as e:
    print(f"读取文件出错: {str(e)}")

print("\n" + "="*50 + "\n")

# 读取并显示老年人评价标准
print("===== 老年人评价标准文件 ======")
try:
    # 读取第一个工作表
    xl = pd.ExcelFile(elderly_excel_path)
    print(f"工作表名称: {xl.sheet_names}")
    
    # 读取第一个工作表的数据
    df = pd.read_excel(xl, sheet_name=xl.sheet_names[0], header=None)
    print("\n前10行数据:")
    for i in range(min(10, len(df))):
        print(f"行 {i+1}: {df.iloc[i].tolist()}")
except Exception as e:
    print(f"读取文件出错: {str(e)}")