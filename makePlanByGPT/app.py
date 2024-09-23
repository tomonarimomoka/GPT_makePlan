#####IMPORT###################################################
import os
import streamlit as st
import requests
import csv
import json
from dotenv import load_dotenv
from openai import OpenAI

#####DEF###################################################
def makePrompt(requiredEvent,recommendEvent,detailText):
    prompt = f'''
    ## 手順１
    以下のデータセットの中から、「{requiredEvent}」に関連するイベントの情報のみを取得してください。
    {getDataSet()}
    ## 手順２
    取得したデータを以下の様に表示してください。取得したイベントは以下でｃ必須イベントと呼びます。
    ## 参加イベント
    |詳細項目|情報|
    | ---- | ---- |
    |イベント名|○○○○|
    |  場所 | ○○駅 |
    |  日付 | ○月○日 |
    | 時間 | hh:mm-hh:mm |

    ## 手順３
   以下の条件をもとに 一日のスケジュールスケジュールを考えてください。
   ・{requiredEvent}には必ず参加してください
   ・時間に空きがあれば{recommendEvent}の中から選んで、時間を潰して下さい
    {detailText}
    ## 手順４
    一日のスケジュールを以下のように時間とやることを分かりやすく表示してください。please think by step by step.
    hh:mm～hh:mm　予定１
    hh:mm～hh:mm　予定２
    ## 注意事項
    ・マークダウンで出力してください。
    ・なるべく具体的に答えて下さい
    '''
    print("prompt = ",prompt)
    
    return prompt

def getDataSet():
    data='''場所：東京都港区六本木6丁目10−1(六本木ヒルズ森タワー15F)
日付：9/21
時間：09:45-17:30
## GDSC Japan Summer Hackathon
場所：東京都渋谷区渋谷３丁目２１−３ 渋谷ストリーム
日付：9/14~22
時間：終日
## 「ChatGptとGodotサウンドはじめ」サウンドミニハッカソン# 32
場所：東京都中央区日本橋馬喰町2丁目7-15 ザ・パークレックス日本橋馬喰町5F
日付：9/21~9/22
時間：12:55-18:00
## Kamakura Mok Mok Hack 195 - 鎌倉もくもく会
場所：神奈川県鎌倉市御成町4-10
日付：9/21~9/22
時間：11:00-14:00
## 初めての電子工作ワークショップ(基礎編)
場所：東京都秋葉原駅徒歩5分 秋葉原ハッカースペース
日付：9/23
時間:9:00-13:00
## はじめての3Dプリンターワークショップ
場所：東京都秋葉原駅徒歩5分 秋葉原ハッカースペース
日付：9/23
時間：13:00-16:30
## AI Engineering Decoded #3
場所：東京都港区虎ノ門3-1-1 虎ノ門三丁目ビルディング 2F
日付：9/24
時間：17:00-19:00
## ラズパイでラズベリーパイ（お菓子）を焼く会
場所：東京都秋葉原駅徒歩5分 秋葉原ハッカースペース
日付：9/28
時間:9:00-11:45
## #Vonage ハッカソン2024
場所：東京都港区南青山2-26-1 D-LIFEPLACE南青山10階
日付：9/28
時間：12:00-17:00
## AWS IoT入門ワークショップ（ESP32とAWS IoTでデータの送受信をしよう）
場所：東京都秋葉原駅徒歩5分 秋葉原ハッカースペース
日付：9/28
時間：13:00-16:30
'''
    return data

def sendApi(requiredEvent,recommendEvent,detailText):   
    load_dotenv()
    api_key=os.getenv("OPENAI_API_KEY")
    endpoint=os.getenv("ENDPOINT")
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    # Payload for the request
    role='''あなたは優秀なツアープランナーです。
1~2時間くらいの隙間時間も楽しい旅程を作成できます。'''
    payload = {
    "messages": [
        {
        "role": "system","content": [{"type": "text", "text": role}]
        },
        {
        "role": "user","content": [{"type": "text", "text": makePrompt(requiredEvent,recommendEvent,detailText)}]
        },
    ],
    "temperature": 0.65,
    "top_p": 0.95,
    "max_tokens": 800
    }

    # Send request
    try:            
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        print(response)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}") from e

    return response.json()['choices'][0]['message']['content']

def getDesireCondition(text):
    returnText=""
    if(text != ""):
        returnText = f'・プラン作成時には、「{text}」という要望も考慮してください。'
    return returnText

def recommendPlaceByAVA():
    #　固定値でなく、AVAからおすすめの場所を取得したかった。
    return "スターバックスコーヒー、本屋、タリーズコーヒー、ドラックストア、映画館"
    # with open("./postman.json",encoding='utf-8') as fp:
    #     return json.load(fp)


#####MAIN###################################################
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.set_page_config(layout="wide")

data_template = """
## 生成AI系のハッカソン
場所：{place}
日付：{date}
開始時間：{start_time}
終了時間：{end_time}
要望：{desire}
"""
event_name = ""
place_input = ""
date_input = ""
start_date = ""
start_time = ""
end_date = ""
end_time = ""
desire = ""
items = ["買い物を楽しめる", "雨の日でも楽しめる", "アクティビティがある", "グルメを楽しむ", "街並みが綺麗"]
selected_items = []

with st.container():
    st.header("必ず参加したいイベント")
    
    with st.container():
        event_name = st.text_input('イベント名')
    
    with st.container():
        cols = st.columns(5)
        with cols[0]:
            place_input = st.text_input('場所')
        with cols[1]:
            start_date_input = st.date_input('開始日')
        with cols[2]:
            start_time_input = st.time_input('開始時間')
        with cols[3]:
            end_date_input = st.date_input('終了日時')
        with cols[4]:
            end_time_input = st.time_input('終了時間')


st.header("出来たらやりたいこと")

with st.container():
    desire_input = st.text_area('要望をフリーテキストで入力できます。')

st.markdown("***希望を教えてください***")
    
for item in items:
    if st.checkbox(item):
        selected_items.append(item)


if st.button("旅行プランを考える"):
    result=sendApi(event_name,recommendPlaceByAVA(),getDesireCondition(desire_input))
    st.markdown(result)