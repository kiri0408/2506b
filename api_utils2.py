
"""
API接続情報の読み込み、AzureOpenAIクライアントの作成、
およびチャット応答取得のためのユーティリティ関数群を提供します。

v2 : get_response関数について stream=Trueの場合はストリーミングで応答を返すようにした。

"""

import json
from openai import AzureOpenAI

def load_api_data(file_path) :
    """API接続情報をJSONファイルから読み込む関数

    Args:
        file_path (str): JSONファイルのパス

    Returns:
        dict: JSONファイルから読み込んだAPI接続情報の辞書
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_client(api_data) :
    """提供されたAPI情報を使ってAzureOpenAIクライアントを作成する関数

    Args:
        api_data (dict): API接続情報を含む辞書。キーは
            - azure_endpoint (str): AzureのエンドポイントURL
            - api_key (str): APIキー
            - api_version (str): APIのバージョン
            - model (str): 使用するモデル名

    Returns:
        tuple: (AzureOpenAIクライアントインスタンス, モデル名)
    """
    return AzureOpenAI(
        azure_endpoint=api_data["azure_endpoint"],
        api_key=api_data["api_key"],
        api_version=api_data["api_version"],
    ),  api_data["model"]

def get_response(client, model, content, stream=False):
    """
    チャットを実行し、レスポンスのメッセージコンテンツを返す関数。
    stream=Trueの場合はストリーミングで応答を返すジェネレータを返す。

    Args:
        client (AzureOpenAI): AzureOpenAIクライアントインスタンス
        model (str): 使用するモデル名
        content (str): ユーザーからのメッセージ内容
        stream (bool, optional): ストリーミングモードの有無。デフォルトはFalse。

    Returns:
        str or generator: stream=Falseなら応答メッセージ文字列、Trueならチャンクを逐次返すジェネレータ
    """
    system_message = {
        "role": "system",
        "content": "あなたは優秀なアシスタントです。"
    }
    user_message = {
        "role": "user",
        "content": content
    }

    if not stream:
        # ストリーミングモードでない場合は、一度に全ての応答を取得して返す
        response = client.chat.completions.create(
            messages=[system_message, user_message],
            model=model
        )
        return response.choices[0].message.content
    else:
        # ストリーミングモードの場合は、応答をチャンク単位で逐次取得し、ジェネレータで返す
        response = client.chat.completions.create(
            messages=[system_message, user_message],
            model=model,
            stream=True
        )
        for chunk in response:
            if len(chunk.choices) > 0:
                message = chunk.choices[0].delta.content
                if message != None:
                    yield message
