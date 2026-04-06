import pandas as pd
import requests
from datetime import datetime

def scrape():
    # 目标网址：全国水情信息 - 大江大河
    url = "http://xxfb.mwr.cn/sq_djdh.html"
    
    # 注意：该网站通常通过异步接口获取数据，直接抓取HTML可能为空。
    # 这里演示的是针对该类型网站的常用处理逻辑（模拟请求）
    print(f"正在尝试获取数据: {datetime.now()}")
    
    try:
        # 这里使用 pandas 尝试直接读取网页中的表格（如果是静态表格）
        # 如果该网页是动态加载，小白可以使用这种“暴力”尝试法
        df_list = pd.read_html(url)
        if df_list:
            df = df_list[0]
            # 保存为 CSV 文件
            filename = f"data_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"抓取成功！文件已保存为: {filename}")
        else:
            print("未在页面找到表格数据。")
    except Exception as e:
        print(f"抓取发生错误: {e}")

if __name__ == "__main__":
    scrape()
