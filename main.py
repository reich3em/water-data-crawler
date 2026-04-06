import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import datetime
import os

async def run():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        # 模拟真实浏览器环境
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()
        
        # 目标 URL
        url = "http://xxfb.mwr.cn/sq_djdh.html"
        
        data_captured = []

        # 核心逻辑：拦截响应请求
        # 水利部数据通常通过接口传输，直接抓取 Response 效率最高
        async def handle_response(response):
            if "getRealData.asp" in response.url or "sq_djdh" in response.url:
                try:
                    # 尝试解析 JSON 数据
                    if response.status == 200:
                        json_data = await response.json()
                        if 'data' in json_data:
                            data_captured.extend(json_data['data'])
                            print(f"✅ 成功拦截到数据接口: {len(json_data['data'])} 条记录")
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            print(f"🚀 正在访问: {url}")
            # 增加等待时间，防止网络波动
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 额外等待页面渲染（如果拦截没触发，则尝试等待表格显示）
            try:
                await page.wait_for_selector(".table_list", timeout=30000)
                print("📡 页面表格已渲染")
            except:
                print("⚠️ 未探测到 .table_list 元素，尝试通过接口数据保存...")

            # 如果抓到了数据，保存为 CSV
            if data_captured:
                df = pd.DataFrame(data_captured)
                filename = f"water_data_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"💾 数据已保存
