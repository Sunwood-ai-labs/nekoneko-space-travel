"""
ねこねこスペーストラベルカンパニー
Streamlitウェブアプリケーション

主な機能:
- 宇宙旅行パッケージの閲覧と予約
- カスタマーサポート
- 安全情報の提供
- 予約状況の管理
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from nekoneko.agents.booking_agent import booking_agent, calculate_price
from nekoneko.agents.safety_agent import safety_agent, monitor_space_weather
from nekoneko.agents.customer_service_agent import customer_service_agent
from nekoneko.agents.team_agent import team_agent

# ページ設定
st.set_page_config(
    page_title="ねこねこスペーストラベル",
    page_icon="🚀",
    layout="wide"
)

# ページヘッダー
st.title("🐱 ねこねこスペーストラベル 🚀")
st.markdown("### 〜 宇宙への冒険をご一緒に 〜")

# サイドバー - メニュー選択
menu = st.sidebar.selectbox(
    "メニュー",
    ["ホーム", "旅行パッケージ", "予約", "安全情報", "お問い合わせ"]
)

if menu == "ホーム":
    # メインページ
    st.markdown("""
    ## にゃーようこそ！宇宙への扉へ 🌟
    
    ねこねこスペーストラベルは、夢のような宇宙旅行体験を提供する
    宇宙旅行代理店です。最新の技術と安全性、そして快適さを組み合わせた
    特別な宇宙の旅をご用意しています。
    
    ### 🎯 特徴
    - 🛸 最新の宇宙船で快適な旅を
    - 🏥 徹底した安全管理
    - 🌍 地球を見下ろす感動体験
    - 🎓 充実した事前トレーニング
    - 😺 フレンドリーなねこスタッフ
    """)
    
    # 宇宙天気情報の表示
    st.subheader("🌠 本日の宇宙天気")
    weather = monitor_space_weather()
    st.info(f"""
    - 太陽活動: {weather.solar_activity}
    - 放射線レベル: {weather.radiation_level}
    - 隕石リスク: {weather.meteoroid_risk}
    
    {weather.recommendation}
    """)

elif menu == "旅行パッケージ":
    st.header("🎫 宇宙旅行パッケージ")
    
    # パッケージ一覧の表示
    packages = {
        "月周遊コース": {
            "description": "地球の衛星、月の周りをクルージング",
            "duration": "3日間",
            "price": "1,000,000円〜",
            "highlights": ["地球の出の観賞", "月面クレーターの観察", "無重力体験"]
        },
        "火星探検コース": {
            "description": "赤い惑星、火星への冒険の旅",
            "duration": "30日間",
            "price": "5,000,000円〜",
            "highlights": ["火星地表散策", "火星基地滞在", "科学実験体験"]
        },
        "宇宙ステーション滞在": {
            "description": "国際宇宙ステーションでの生活体験",
            "duration": "5日間",
            "price": "800,000円〜",
            "highlights": ["宇宙飛行士との交流", "地球観測", "宇宙実験参加"]
        }
    }
    
    for name, details in packages.items():
        with st.expander(f"📦 {name}"):
            st.markdown(f"""
            ### {details['description']}
            - ⏱️ 期間: {details['duration']}
            - 💰 料金: {details['price']}
            
            #### ✨ ハイライト
            {"".join([f'- {h}\\n' for h in details['highlights']])}
            """)
            if st.button(f"{name}を予約する", key=name):
                st.session_state['selected_package'] = name
                st.session_state['menu'] = "予約"
                st.experimental_rerun()

elif menu == "予約":
    st.header("✍️ ご予約")
    
    # 予約フォーム
    with st.form("booking_form"):
        selected_package = st.selectbox(
            "パッケージ選択",
            ["月周遊コース", "火星探検コース", "宇宙ステーション滞在"],
            index=0 if 'selected_package' not in st.session_state 
                  else list(packages.keys()).index(st.session_state['selected_package'])
        )
        
        col1, col2 = st.columns(2)
        with col1:
            departure_date = st.date_input(
                "出発日",
                min_value=datetime.now().date() + timedelta(days=30),
                max_value=datetime.now().date() + timedelta(days=365)
            )
        with col2:
            passengers = st.number_input("乗客数", min_value=1, max_value=4, value=1)
            
        package_type = st.selectbox("クラス", ["エコノミー", "ビジネス", "ファースト"])
        
        special_requests = st.text_area("特別なご要望")
        
        submitted = st.form_submit_button("料金を計算する")
        
        if submitted:
            # 料金計算
            days = {
                "月周遊コース": 3,
                "火星探検コース": 30,
                "宇宙ステーション滞在": 5
            }[selected_package]
            
            total_price = calculate_price(
                selected_package.replace("コース", "").replace("滞在", ""),
                days,
                package_type,
                passengers
            )
            
            st.success(f"""
            ### お見積り結果
            - パッケージ: {selected_package}
            - 出発日: {departure_date}
            - 乗客数: {passengers}名
            - クラス: {package_type}
            
            **合計金額: ¥{total_price:,}**
            """)
            
            if st.button("予約を確定する"):
                # 予約エージェントに処理を依頼
                booking_response = booking_agent.run(f"""
                以下の予約を処理してください：
                - パッケージ: {selected_package}
                - 出発日: {departure_date}
                - 乗客数: {passengers}名
                - クラス: {package_type}
                - 特別要望: {special_requests}
                """)
                st.write(booking_response)

elif menu == "安全情報":
    st.header("🛡️ 安全情報")
    
    # タブで安全情報を分類
    tab1, tab2, tab3 = st.tabs(["健康要件", "訓練プログラム", "緊急時対応"])
    
    with tab1:
        st.subheader("🏥 健康要件")
        health_info = safety_agent.run("""
        宇宙旅行に必要な健康要件について説明してください。
        特に以下の点について詳しく説明をお願いします：
        1. 必須の健康診断項目
        2. 年齢制限
        3. 持病がある場合の注意点
        """)
        st.write(health_info)
        
    with tab2:
        st.subheader("🎓 訓練プログラム")
        training_info = safety_agent.run("""
        宇宙旅行前の訓練プログラムについて説明してください。
        以下の内容を含めてください：
        1. 訓練の種類と内容
        2. 所要時間
        3. 達成基準
        """)
        st.write(training_info)
        
    with tab3:
        st.subheader("🚨 緊急時対応")
        emergency_info = safety_agent.run("""
        宇宙旅行中の緊急時対応について説明してください。
        以下の状況別の対応手順を含めてください：
        1. 医療緊急事態
        2. 技術的トラブル
        3. 自然災害（宇宙天気等）
        """)
        st.write(emergency_info)

elif menu == "お問い合わせ":
    st.header("💌 お問い合わせ")
    
    # お問い合わせフォーム
    with st.form("contact_form"):
        inquiry_type = st.selectbox(
            "お問い合わせ種類",
            ["一般的な質問", "予約に関して", "安全性について", "キャンセル・変更", "その他"]
        )
        
        name = st.text_input("お名前")
        email = st.text_input("メールアドレス")
        message = st.text_area("メッセージ")
        
        if st.form_submit_button("送信"):
            # カスタマーサービスエージェントに問い合わせを転送
            response = customer_service_agent.run(f"""
            以下のお問い合わせに対応してください：
            種類: {inquiry_type}
            名前: {name}
            メール: {email}
            内容: {message}
            """)
            st.write(response)

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🐱 ねこねこスペーストラベル 🚀<br>
    夢と冒険の宇宙旅行代理店</p>
</div>
""", unsafe_allow_html=True)
