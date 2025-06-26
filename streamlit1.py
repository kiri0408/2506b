import streamlit as st
import api_utils
from typing import List, Dict, Any, Tuple


def load_api_client(file_path: str) -> Tuple[Any, str]:
    """
    API接続情報を読み込み、AIクライアントとモデル名を作成する。

    Args:
        file_path (str): API接続情報のファイルパス

    Returns:
        client: AIクライアントオブジェクト
        model (str): モデル名
    """
    api_data = api_utils.load_api_data(file_path)
    client, model = api_utils.create_client(api_data)
    return client, model


def display_messages(messages: List[Dict[str, str]]) -> None:
    """
    セッションステートのメッセージ履歴をStreamlitのチャットメッセージとして表示する。

    Args:
        messages (List[Dict[str, str]]): メッセージ履歴
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def stream_ai_response(client: Any, model: str, messages: List[Dict[str, str]]) -> str:
    """
    AIからの応答をストリーミングで取得し、表示する。

    Args:
        client: AIクライアントオブジェクト
        model (str): モデル名
        messages (List[Dict[str, str]]): チャットメッセージ履歴

    Returns:
        str: AIの応答内容
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "あなたは優秀なアシスタントです。"},
            *messages,
        ],
        model=model,
        stream=True,
        reasoning_effort="medium"  # low, medium, high
    )

    response_content = ""
    message_container = st.empty()
    for chunk in response:
        if len(chunk.choices) > 0:
            message = chunk.choices[0].delta.content
            try:
                response_content += message
            except Exception:
                response_content += '\n'
            message_container.markdown(response_content)
    return response_content


def main():
    st.title("AIチャットアプリ")

    # API接続情報ファイルパス（必要に応じて変更してください）
    file_path = 'api_o3_mini.json'

    client, model = load_api_client(file_path)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_messages(st.session_state.messages)

    if prompt := st.chat_input("メッセージを入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        response_content = stream_ai_response(client, model, st.session_state.messages)

        st.session_state.messages.append({"role": "assistant", "content": response_content})


if __name__ == "__main__":
    main()
