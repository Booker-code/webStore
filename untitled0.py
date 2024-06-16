# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 13:48:28 2024

@author: xpuaz
"""

import sqlite3
import pymysql

# 连接到 SQLite 数据库
sqlite_conn = sqlite3.connect('C:/Users/xpuaz/project/site.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接到 MySQL 数据库
mysql_conn = pymysql.connect(host='localhost', user='root', password='1234567890', database='project')
mysql_cursor = mysql_conn.cursor()

# 获取所有表
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

for table in tables:
    table_name = table[0]

    # 获取表结构
    sqlite_cursor.execute(f"PRAGMA table_info([{table_name}])")
    columns = sqlite_cursor.fetchall()
    column_definitions = ', '.join([f"`{col[1]}` {col[2]}" for col in columns])

    # 创建表
    create_table_sql = f"CREATE TABLE `{table_name}` ({column_definitions})"
    mysql_cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")  # 如果表已存在则先删除
    mysql_cursor.execute(create_table_sql)

    # 获取数据
    sqlite_cursor.execute(f"SELECT * FROM [{table_name}]")
    rows = sqlite_cursor.fetchall()
    for row in rows:
        placeholders = ', '.join(['%s'] * len(row))
        mysql_cursor.execute(f"INSERT INTO `{table_name}` VALUES ({placeholders})", row)

# 提交更改并关闭连接
mysql_conn.commit()
mysql_cursor.close()
mysql_conn.close()
sqlite_cursor.close()
sqlite_conn.close()
