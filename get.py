# 方式1：从环境变量读取用户名和密码
from GET_campus_user_hnxx import GET_campus_user_hnxx
result = GET_campus_user_hnxx()

# 方式2：直接传入用户名和密码
#result = GET_campus_user_hnxx(username="your_username", password="your_password")

if result:
    print(f"获取成功: {result}")
else:
    print("获取失败")