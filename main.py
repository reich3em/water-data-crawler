import requests
import pandas as pd
from datetime import datetime

def scrape():
    # 1. 找到水利部真正的隐藏数据接口
    # 这个 URL 是该网页请求数据的真实后台地址
    api_url = "http://xxfb.mwr.cn/getPagedSq.do"
    
    # 2. 模拟浏览器请求头，防止被拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "http://xxfb.mwr.cn/sq_djdh.html"
    }
    
    # 3. 构造请求参数（对应“大江大河”表格）
    payload = {
        "pageIndex": 1,
        "pageSize": 100, # 爬取前100条数据
        "stName": "",
        "rvName": "",
        "date": datetime.now().strftime('%Y-%m-%d')
    }

    print(f"正在尝试从接口获取数据: {datetime.now()}")

    try:
        # 发送请求
        response = requests.post(api_url, data=payload, headers=headers)
        response.raise_for_status() # 检查请求是否成功
        
        # 解析返回的 JSON 数据
        data = response.json()
        
        # 提取表格核心内容（在 result 字段下）
        if 'result' in data and data['result']:
            df = pd.DataFrame(data['result'])
            
            # 中文列名映射（让 CSV 更好看）
            column_map = {
                'rvNm': '流域/水系',
                'stNm': '站名',
                'tm': '时间',
                'z': '水位(米)',
                'q': '流量(立方米/秒)',
                'wptn': '水势'
            }
            df = df.rename(columns=column_map)
            
            # 只要我们关心的列
            available_cols = [c for c in column_map.values() if c in df.columns]
            df = df[available_cols]

            # 保存文件
            filename = f"water_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ 抓取成功！已保存 {len(df)} 行数据到 {filename}")
        else:
            print("❌ 接口返回了空数据，可能是参数或日期问题。")
            
    except Exception as e:
        print(f"❌ 抓取发生错误: {e}")

if __name__ == "__main__":
    scrape()
