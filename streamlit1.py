import streamlit as st
import api_utils

#file_path ='api_gpt4o.json'                       # API接続情報のファイルパス
file_path ='api_o3_mini.json'                       # API接続情報のファイルパス
api_data = api_utils.load_api_data(file_path)     # API接続情報を取得
client, model = api_utils.create_client(api_data) # AIクライアント作成、モデル名を取得


# Streamlitの設定
st.title("AIチャットアプリ")

# セッションステートの初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# メッセージ履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザーからの入力を受け取る
if prompt := st.chat_input("メッセージを入力してください"):
    # ユーザーのメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # チャットメッセージとして表示
    with st.chat_message("user"):
        st.markdown(prompt)
    print(prompt)

    # AIからの応答をストリーミングで生成
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "あなたは優秀なアシスタントです。"},
            *st.session_state.messages,
        ],
        model=model,
        stream=True,
        reasoning_effort="medium"   # low, medium, high  
    )

    # ストリーミングされた応答を表示
    response_content = ""
    message_container = st.empty()  # コンテナを作成
    for chunk in response:
        if len(chunk.choices) > 0:
            message = chunk.choices[0].delta.content
            try:
                response_content += message
            except :
                response_content +='\n'
            message_container.markdown( response_content )  # コンテナ内のテキストを更新

    # AIのメッセージを履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": response_content})

