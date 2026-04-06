import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

class WaterDataScraper:
    def __init__(self):
        # 目标网站配置
        self.domain = "http://xxfb.mwr.gov.cn" 
        self.target_url = "http://xxfb.mwr.gov.cn/sq_djdh.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        # --- 整合的核心映射表 (针对 tqF18oRs6s 版本) ---
        self.font_map = {
            # 数字还原 (规律: Unicode码 = 真实数字*2 + 14516)
            '㢴': '0', '㢶': '1', '㢸': '2', '㢺': '3', '㢼': '4',
            '㢾': '5', '㣀': '6', '㣂': '7', '㣄': '8', '㣆': '9',
            # 常见汉字还原 (基于源码样本)
            '㶰': '长', '㵀': '江', '㧸': '北', '㵰': '汉', '㲎': '寸', 
            '㮎': '滩', '㤸': '宜', '㴲': '昌', '㿬': '站', '㮜': '沙',
            '㷜': '市', '㰮': '监', '䀌': '利', '㫸': '湖', '㯒': '南',
            '㰰': '岳', '䄼': '阳', '㴔': '松', '䂰': '枝', '㮊': '城',
            '㽂': '洞', '㴖': '庭', '䅰': '鹿', '䅬': '角', '㮚': '溪',
            '㾚': '武', '㫀': '湖', '㾰': '汉', '㺎': '九', '㪒': '江',
            '㷔': '段', '䆠': '鄱', '㩄': '庐', '㪖': '山', '㳄': '湖',
            '㱆': '汉', '㦊': '口', '䆜': '黄', '㵖': '石', '䅞': '淮',
            '㩂': '王', '㯪': '家', '㴰': '太', '㩄': '望', '㨚': '亭',
            '㳨': '嘉', '㺢': '夹', '䅨': '浦', '㫴': '珠', '㪲': '海',
            '㶴': '西', '㴆': '河', '㵌': '博', '㻔': '罗', '㭂': '湾',
            '㤴': '二', '㤒': '赤', '㴚': '壁', '㴦': '嘉', '䂄': '石',
            '㪎': '鼓', '㧤': '浙', '㼶': '兰', '㽚': '溪', '㭶': '浦'
        }

    def clean_text(self, text):
        """核心解密函数：遍历字符串，将乱码字符替换为真实字符"""
        if not text: return ""
        # 去除空白字符并逐个字符查找映射表
        return "".join([self.font_map.get(char, char) for char in text.strip()])

    def run(self):
        print(f"正在访问: {self.target_url}")
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8' # 强制指定编码防止乱码
            
            if response.status_code != 200:
                print("网页请求失败")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 找到包含数据的表格行 (根据源码中的 tr class="td-show-1")
            rows = soup.find_all('tr', class_='td-show-1')
            print(f"共发现 {len(rows)} 条数据行，开始解码...\n")

            all_data = []
            for row in rows:
                tds = row.find_all('td')
                if len(tds) < 7: continue
                
                # 按照表格顺序解析并实时解码
                item = {
                    "流域": self.clean_text(tds[0].text),
                    "行政区划": self.clean_text(tds[1].text),
                    "河名": self.clean_text(tds[2].text),
                    "站名": self.clean_text(tds[3].text),
                    "监测时间": tds[4].text.strip(),
                    "水位(m)": self.clean_text(tds[5].text),
                    "状态": tds[6].text.strip()
                }
                all_data.append(item)

            # 输出结果（转换为 DataFrame 方便查看或保存）
            df = pd.DataFrame(all_data)
            print(df.to_string(index=False))
            
            # 如果需要保存到 Excel
            # df.to_excel("水情数据.xlsx", index=False)
            # print("\n数据已保存至 '水情数据.xlsx'")

        except Exception as e:
            print(f"程序运行出错: {e}")

if __name__ == "__main__":
    scraper = WaterDataScraper()
    scraper.run()
