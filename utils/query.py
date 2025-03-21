from DBUtils.PooledDB import PooledDB
import pymysql

# 创建数据库连接池
pool = PooledDB(
    creator=pymysql,  # 使用 pymysql
    host='localhost',
    user='root',
    password='123456',
    database='steamdata',
    port=3306,
    maxconnections=10,
)

def querys(sql, params, type='no_select'):
    # 从连接池中获取连接
    conn = pool.connection()
    params = tuple(params)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    if type != 'no_select':
        data_list = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()  # 在获取数据后立即关闭连接
        return data_list
    else:
        conn.commit()
        cursor.close()
        conn.close()  # 在执行非查询语句后立即关闭连接
        return '数据库语句执行成功!'






# from pymysql import *
#
# conn = connect(host='localhost', user='root', password='123456', database='dbmovie', port=3306)
# cursor = conn.cursor()
#
#
#
# def querys(sql, params, type='no_select'):
#     params = tuple(params)
#     cursor.execute(sql, params)
#     if type != 'no_select':
#         data_list = cursor.fetchall()
#         conn.commit()
#         return data_list
#     else:
#         conn.commit()
#         return '数据库语句执行成功!'


# users = querys('select * from user', [], 'select')
# print(users)
# def filter_fn(item):
#     return '123@qq.com' in item


# a = (1, '123@qq.com', '1')
# if '123@qq.com' in a:
#     print(a)
#     print(1)
#
# users = querys('select * from user', [], 'select')
# print(users[0], 123)
# filter_list = list(filter(filter_fn, users))
# print(filter_list)
# a = ((1, '1453641651@qq.com', '1'))
# b = [(1, '1453641651@qq.com', '1')]
# for i in b:
#     print(b[0][1],123)
#     print(i)
