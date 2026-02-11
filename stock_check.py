import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

# 从 GitHub Secrets 读取配置
# 在本地测试时，可以临时手动填写，但提交代码前请改回 os.environ.get
WATCH_LIST = ["605305"] # 你的关注列表
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")

def get_research_data():
    try:
        df = ak.stock_jgdy_tj_em()
        return df
    except Exception as e:
        print(f"获取数据出错: {e}")
        return None

def send_wechat(content):
    if not PUSHPLUS_TOKEN:
        print("未配置 PushPlus Token，跳过发送")
        return
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": f"📈 股票调研提醒 - {datetime.now().strftime('%Y-%m-%d')}",
        "content": content,
        "template": "html"
    }
    requests.post(url, data=data)

def main():
    df = get_research_data()
    if df is None or df.empty:
        print("暂无数据")
        return

    # 过滤关注股票
    target_df = df[df['代码'].isin(WATCH_LIST)]

    if target_df.empty:
        msg = "今日关注股票暂无机构调研记录。"
    else:
        html_table = "<h3>关注股票调研汇总：</h3><table border='1'><tr><th>名称</th><th>调研机构数</th><th>公告日期</th></tr>"
        for _, row in target_df.iterrows():
            html_table += f"<tr><td>{row['名称']}</td><td><b>{row['接待机构数量']}</b></td><td>{row['公告日期']}</td></tr>"
        html_table += "</table>"
        msg = html_table

    send_wechat(msg)

if __name__ == "__main__":
    main()
