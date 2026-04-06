import asyncio
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import json

def run():
    with sync_playwright() as p:
        # 启动无头浏览器
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"🚀 正在启动浏览器访问页面...")
        
        # 准备捕获 API 响应数据
        final_data = []

        def handle_response(response):
            # 这里的 URL 是我们之前 404 的那个接口
            if "getPagedSq.do" in response.url:
                try:
                    json_data = response.json()
                    if 'result' in json_data:
                        final_data.extend(json_data['result'])
                        print(f"✅ 已拦截到数据接口，获取到 {len(json_data['result'])} 条记录")
                except Exception as e:
                    print(f"⚠️ 解析响应失败: {e}")

        # 监听所有网络响应
        page.on("response", handle_response)

        # 访问主页，触发后台 API 请求
        try:
            page.goto("http://xxfb.mwr.cn/sq_djdh.html", wait_until="networkidle", timeout=60000)
            # 给页面一点时间加载完数据
            page.wait_for_timeout(5000) 
        except Exception as e:
            print(f"❌ 页面加载超时或出错: {e}")

        if final_data:
            df = pd.DataFrame(final_data)
            # 这里的字段名需要根据实际拦截到的 JSON 修改，通常是 rvNm, stNm 等
            df.to_csv(f"water_data_{datetime.now().strftime('%Y%m%d_%H')}.csv", index=False, encoding='utf-8-sig')
            print(f"✨ 数据抓取成功，已保存至 CSV")
        else:
            print("❌ 未能拦截到目标数据，请检查页面结构是否变化")

        browser.close()

if __name__ == "__main__":
    run()
