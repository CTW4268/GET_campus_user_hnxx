import requests
import re
from urllib.parse import unquote
import hashlib
import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的变量

def get_md5(password):
    """模拟前端 md5.js 的加密行为"""
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def GET_campus_user_hnxx(username=None, password=None):
    """
    获取 campus_user_hnxx cookie 值
    
    Args:
        username (str, optional): 用户名，如果不提供则从环境变量 USERNAME 中读取
        password (str, optional): 密码，如果不提供则从环境变量 PASSWORD 中读取
        
    Returns:
        str: 解码后的 campus_user_hnxx 值，如果失败则返回 None
    """
    # 使用传入的参数或从环境变量读取
    USERNAME = username or os.getenv("USERNAME")
    PASS = password or os.getenv("PASSWORD")
    
    if not USERNAME or not PASS:
        print("[-] 错误：未提供用户名和密码，也未在环境变量中找到")
        return None
    
    # 配置信息
    LOGIN_URL = "https://sso.hnuit.edu.cn/cas/login?service=https%3A%2F%2Feportal.hnuit.edu.cn%2Fehall%2Flogin"
    PASSWORD = get_md5(PASS) 

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    })

    try:
        # 1. 访问登录页获取动态的 execution 参数
        res_init = session.get(LOGIN_URL, timeout=10)
        
        # CAS 通常在 HTML 里有一个隐藏域 <input name="execution" value="xxx" />
        execution_match = re.search(r'name="execution" value="(.+?)"', res_init.text)
        if not execution_match:
            print("[-] 错误：无法从页面提取 execution 参数，请检查网络或 URL")
            return None
        
        execution_val = execution_match.group(1)

        # 2. 模拟 POST 登录
        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "execution": execution_val,
            "_eventId": "submit",
            "geolocation": "",
            "authType": "1",
            "captcha": ""
        }
        
        # allow_redirects=True 让 requests 自动处理后续的 302 跳转
        res_login = session.post(LOGIN_URL, data=payload, allow_redirects=True, timeout=10)

        # 3. 提取目标字段
        # 尝试从所有已访问域名中查找 cookie
        campus_user = session.cookies.get("campus_user_hnxx", domain="eportal.hnuit.edu.cn")
        
        if not campus_user:
            # 有时 requests 没匹配到 domain，尝试全局搜索
            for cookie in session.cookies:
                if cookie.name == "campus_user_hnxx":
                    campus_user = cookie.value
                    break

        if campus_user:
            # 返回解码后的值
            return unquote(campus_user)
        else:
            print("[-] 未能提取到 campus_user_hnxx。可能原因：密码错误、需要验证码或 execution 过期。")
            return None

    except Exception as e:
        print(f"[-] 运行异常: {e}")
        return None

if __name__ == "__main__":
    cookie_val = GET_campus_user_hnxx()
    if cookie_val:
        print(cookie_val)
    else:
        print("\n[提示] 脚本未能在响应中找到目标字段，请检查上方打印的调试信息。")