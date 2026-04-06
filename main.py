import time
import pandas as pd
from playwright.sync_api import sync_playwright

def crawl_water_data():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        # 模拟真实浏览器环境
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = "http://xxfb.mwr.cn/sq_djdh.html"
        print(f"正在访问: {url}")

        try:
            # 1. 导航到页面，等待网络空闲
            page.goto(url, wait_until="networkidle", timeout=60000)

            # 2. 【关键步骤】等待表格数据渲染完成
            # 我们等待包含具体水情数据的 td 标签出现，最多等 20 秒
            print("等待数据加载...")
            page.wait_for_selector("table td", timeout=20000)
            
            # 给一点额外的缓冲时间确保 JavaScript 脚本执行完毕
            time.sleep(2)

            # 3. 获取表格内容
            # 这里的选择器需要根据实际网页结构调整，通常数据在 ID 为 'cont' 或类似的容器内
            rows = page.query_selector_all("tr")
            
            data = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) > 0:
                    # 提取每行中所有单元格的文本
                    row_data = [col.inner_text().strip() for col in cols]
                    data.append(row_data)

            if not data:
                raise Exception("未捕获到任何数据行")

            # 4. 保存数据到 CSV
            # 根据你的截图，表头分别是：流域、行政区划、河名、站名、时间、水位、超警戒水位
            df = pd.DataFrame(data)
            # 如果抓取到了多余的空行或非数据行，可以在这里进行清洗
            df.to_csv("water_data.csv", index=False, encoding="utf-8-sig")
            print(f"成功抓取 {len(data)} 条数据，已保存至 water_data.csv")

        except Exception as e:
            print(f"抓取失败: {e}")
            # 发生错误时保存截图，方便在 GitHub Actions 中排查
            page.screenshot(path="error_debug.png", full_page=True)
            print("已保存错误截图 error_debug.png")
            # 抛出异常让 Action 知道任务失败（可选）
            # raise e 

        finally:
            browser.close()

if __name__ == "__main__":
    crawl_water_data()
