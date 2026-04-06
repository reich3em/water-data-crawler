import requests
import pandas as pd
from datetime import datetime
import json

def scrape():
    # 这里的 URL 我们换成主页试试，有时直接请求接口会被拦截
    url = "http://xxfb.mwr.cn/getPagedSq.do"
    
    # 模拟一个非常真实的 Chrome 浏览器
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "xxfb.mwr.cn",
        "Origin": "http://xxfb.mwr.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://xxfb.mwr.cn/sq_djdh.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # 严格按照网页发送的参数格式
    payload = {
        "pageIndex": "1",
        "pageSize": "100",
        "stName": "",
        "rvName": "",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "sortNm": "z",
        "sortOrder": "desc"
    }

    print(f"🚀 开始尝试通过伪装请求获取数据: {datetime.now()}")

    try:
        # 使用 Session 保持连接特征
        session = requests.Session()
        response = session.post(url, data=payload, headers=headers, timeout=15)
        
        # 打印一下状态码，方便我们调试
        print(f"📡 服务器返回状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and data['result']:
                df = pd.DataFrame(data['result'])
                
                # 只要主要数据列
                cols = {
                    'rvNm': '流域',
                    'stNm': '站名',
                    'tm': '时间',
                    'z': '水位',
                    'q': '流量'
                }
                df = df.rename(columns=cols)[list(cols.values())]
                
                filename = f"water_data_{datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"✨ 成功！抓取到 {len(df)} 条记录，已保存。")
            else:
                print("⚠️ 成功连接但没拿到数据，可能是这会儿服务器没更新。")
        else:
            print(f"❌ 请求失败，错误代码: {response.status_code}")
            
    except Exception as e:
        print(f"🔥 发生了意外错误: {e}")

if __name__ == "__main__":
    scrape()
