import requests
import re
from urllib.parse import unquote
import hashlib
import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的变量

USERNAME = os.getenv("USERNAME")
PASS = os.getenv("PASSWORD")
def get_md5(password):
    """模拟前端 md5.js 的加密行为"""
    return hashlib.md5(password.encode('utf-8')).hexdigest()

# 配置信息
LOGIN_URL = "https://sso.hnuit.edu.cn/cas/login?service=https%3A%2F%2Feportal.hnuit.edu.cn%2Fehall%2Flogin"
#USERNAME = "your_username"
#PASS = "your_password"
# 注意：如果日志里的密码是加密后的，这里也要填加密后的字符串
PASSWORD = get_md5(PASS) 

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
})

def get_campus_cookie():
    try:
        # 1. 访问登录页获取动态的 execution 参数
        print(f"[*] 正在请求登录页面: {LOGIN_URL}")
        res_init = session.get(LOGIN_URL, timeout=10)
        
        # CAS 通常在 HTML 里有一个隐藏域 <input name="execution" value="xxx" />
        execution_match = re.search(r'name="execution" value="(.+?)"', res_init.text)
        if not execution_match:
            print("[-] 错误：无法从页面提取 execution 参数，请检查网络或 URL")
            return None
        
        execution_val = execution_match.group(1)
        print(f"[+] 提取到 execution: {execution_val[:20]}...")

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
        
        print("[*] 正在提交登录凭据...")
        # allow_redirects=True 让 requests 自动处理后续的 302 跳转
        # 这样它会自动走完：Ticket验证 -> 设置 Cookie -> 进入主页
        res_login = session.post(LOGIN_URL, data=payload, allow_redirects=True, timeout=10)
        
        print(f"[*] 最终响应状态码: {res_login.status_code}")
        print(f"[*] 最终 URL: {res_login.url}")

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
            print(f"\n[!] 成功获取 campus_user_hnxx!")
            return campus_user
        else:
            print("\n[-] 未能提取到 campus_user_hnxx。可能原因：密码错误、需要验证码或 execution 过期。")
            # 打印当前所有 Cookie 供排查
            print(f"[*] 当前 Session 中的 Cookies: {session.cookies.get_dict()}")
            return None

    except Exception as e:
        print(f"[-] 运行异常: {e}")
        return None

if __name__ == "__main__":
    cookie_val = get_campus_cookie()
    if cookie_val:
        # 只有不为 None 时才进行解码
        print("-" * 30)
        print("解密后的 Cookie 值:")
        print(unquote(cookie_val))
        print("-" * 30)
    else:
        print("\n[提示] 脚本未能在响应中找到目标字段，请检查上方打印的调试信息。")