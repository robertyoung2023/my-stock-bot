import akshare as ak
import pandas as pd
import requests
import os
from datetime import datetime

# ================= 配置区 =================
# 你的关注列表
WATCH_LIST = ["605305"] 
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# =========================================

def get_market_summary():
    """获取全市场大宗交易统计概况"""
    try:
        df = ak.stock_dzjy_mrtj_em()
        if df is None or df.empty: return "<h4>全市场大宗交易：今日无数据</h4>"
        
        total_stocks = df['证券代码'].nunique()
        total_amount = df['成交总额'].sum() / 10000  # 亿元
        premium_df = df[df['折溢率'] > 0]
        
        html = f"""
        <div style='background-color:#fdfaf0; padding:10px; border-radius:5px;'>
            <h3 style='color:#d35400;'>🌍 全市场大宗风向标</h3>
            <p><b>总计：</b>{total_stocks} 只个股上榜，成交额 <b>{total_amount:.2f} 亿</b></p>
            <p><b>情绪：</b>溢价 {len(premium_df)} 只 / 折价 {len(df[df['折溢率'] < 0])} 只</p>
        </div>
        """
        
        # 市场 Top 3 金额
        top_3 = df.nlargest(3, '成交总额')
        html += "<b>💰 成交额前三：</b><br>"
        for _, row in top_3.iterrows():
            html += f"• {row['证券名称']} ({row['成交总额']/10000:.2f}亿, {row['折溢率']:.2f}%)<br>"
        return html
    except Exception as e:
        return f"<p>全市场统计获取失败: {e}</p>"

def get_watchlist_detail():
    """获取关注列表的调研、龙虎榜、大宗交易明细"""
    sections = []
    
    # 1. 机构调研
    try:
        df_res = ak.stock_jgdy_tj_em()
        target = df_res[df_res['代码'].isin(WATCH_LIST)]
        if not target.empty:
            html = "<h4>🔍 关注股-机构调研</h4><table border='1' style='width:100%;border-collapse:collapse;font-size:12px;'>"
            html += "<tr><th>股票</th><th>机构数</th><th>日期</th></tr>"
            for _, row in target.iterrows():
                html += f"<tr><td>{row['名称']}</td><td><b>{row['接待机构数量']}</b></td><td>{row['公告日期']}</td></tr>"
            sections.append(html + "</table>")
    except: pass

    # 2. 龙虎榜
    try:
        df_lhb = ak.stock_lhb_ggtj_em()
        target = df_lhb[df_lhb['代码'].isin(WATCH_LIST)]
        if not target.empty:
            html = "<h4>🔥 关注股-龙虎榜</h4><table border='1' style='width:100%;border-collapse:collapse;font-size:12px;'>"
            html += "<tr><th>股票</th><th>净买(万)</th><th>原因</th></tr>"
            for _, row in target.iterrows():
                html += f"<tr><td>{row['名称']}</td><td>{row['累积净买入额']}</td><td>{row['解说']}</td></tr>"
            sections.append(html + "</table>")
    except: pass

    # 3. 大宗交易明细
    try:
        df_dz = ak.stock_dzjy_mrtj_em()
        target = df_dz[df_dz['证券代码'].isin(WATCH_LIST)]
        if not target.empty:
            html = "<h4>🤝 关注股-大宗交易</h4><table border='1' style='width:100%;border-collapse:collapse;font-size:12px;'>"
            html += "<tr><th>股票</th><th>金额(万)</th><th>折溢率</th></tr>"
            for _, row in target.iterrows():
                color = "red" if row['折溢率'] > 0 else "green"
                html += f"<tr><td>{row['证券名称']}</td><td>{row['成交总额']}</td><td style='color:{color}'>{row['折溢率']}%</td></tr>"
            sections.append(html + "</table>")
    except: pass

    return "".join(sections) if sections else "<p>💡 今日关注股票无重大异动。</p>"

def main():
    # 获取两部分数据
    market_html = get_market_summary()
    watchlist_html = get_watchlist_detail()
    
    # 组合最终消息
    final_html = f"""
    {market_html}
    <hr>
    <h3 style='color:#2980b9;'>📌 关注列表动态</h3>
    {watchlist_html}
    <p style='font-size:10px; color:gray; text-align:right;'>数据更新于: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    """
    
    # 发送推送
    if PUSHPLUS_TOKEN:
        url = "http://www.pushplus.plus/send"
        payload = {
            "token": PUSHPLUS_TOKEN,
            "title": f"今日投研汇总 - {datetime.now().strftime('%m/%d')}",
            "content": final_html,
            "template": "html"
        }
        res = requests.post(url, data=payload)
        print(f"推送结果: {res.text}")
    else:
        print("未检测到 Token，内容预览：\n", final_html)

if __name__ == "__main__":
    main()
