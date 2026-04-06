import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import datetime
import os

async def run():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()
        url = "http://xxfb.mwr.cn/sq_djdh.html"
        
        data_captured = []

        # 拦截响应请求
        async def handle_response(response):
            if "getRealData.asp" in response.url or "sq_djdh" in response.url:
                try:
                    if response.status == 200:
                        json_data = await response.json()
                        if 'data' in json_data:
                            data_captured.extend(json_data['data'])
                            print(f"Captured {len(json_data['data'])} records from API")
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            print(f"Navigating to: {url}")
            # 设置较长的超时时间，水利部官网有时响应慢
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 等待数据加载
            await asyncio.sleep(5) 

            if data_captured:
                df = pd.DataFrame(data_captured)
                date_str = datetime.datetime.now().strftime('%Y%m%d')
                filename = f"water_data_{date_str}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"Success: Data saved to {filename}")
            else:
                print("Error: No data captured. Saving screenshot...")
                await page.screenshot(path="error_debug.png")

        except Exception as e:
            print(f"Runtime Error: {e}")
            await page.screenshot(path="error_debug.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
