import asyncio
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import json

def run():
    with sync_playwright() as p:
        # 1. 使用 launch 的时候增加一些参数，规避自动化检测
        browser = p.chromium.launch(headless=True)
        
        # 2. 模拟真实的浏览器上下文
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 隐藏自动化指纹
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        print(f"🚀 正在启动加强版浏览器访问...")
        
        final_data = []

        # 修改拦截逻辑：只要包含关键词就打印，方便调试
        def handle_response(response):
            if "getPagedSq.do" in response.url or "sq_djdh" in response.url:
                print(f"📡 探测到请求: {response.url[:60]}... 状态码: {response.status}")
                try:
                    if response.status == 200:
                        json_data = response.json()
                        if 'result' in json_data:
                            final_data.extend(json_data['result'])
                            print(f"✅ 拦截成功！获取到 {len(json_data['result'])} 条数据")
                except Exception as e:
                    pass 

        page.on("response", handle_response)

        try:
            # 3. 访问页面并模拟一点“真人”滚动
            page.goto("http://xxfb.mwr.cn/sq_djdh.html", wait_until="domcontentloaded", timeout=60000)
            
            # 等待表格或特定元素加载出来
            page.wait_for_selector(".table_list", timeout=20000) 
            
            # 模拟向下滚动，触发某些懒加载逻辑
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(5000) 
            
        except Exception as e:
            print(f"⚠️ 页面处理中出现提示（可能是非致命错误）: {e}")

        if final_data:
            # 去重处理（防止多次拦截到相同数据）
            df = pd.DataFrame(final_data).drop_duplicates()
            filename = f"water_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✨ 最终保存成功: {filename}，共 {len(df)} 行")
        else:
            print("❌ 依然未能拦截到数据。建议：手动在本地浏览器打开 F12 查看接口 URL 是否有变。")

        browser.close()

if __name__ == "__main__":
    run()
