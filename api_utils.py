import json
from openai import AzureOpenAI

def load_api_data(file_path) :
    """API接続情報をJSONファイルから読み込む関数"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_client(api_data) :
    """提供されたAPI情報を使ってAzureOpenAIクライアントを作成する関数"""
    return AzureOpenAI(
        azure_endpoint=api_data["azure_endpoint"],
        api_key=api_data["api_key"],
        api_version=api_data["api_version"],
    ),  api_data["model"]

def get_response(client, model, content) :
    """
    チャットを実行し、レスポンスのメッセージコンテンツを返す関数

    Args:
        client: AzureOpenAIクライアントインスタンス
        model: 使用するモデル名（文字列）
        content: ユーザーからのメッセージ内容（文字列）

    Returns:
        str: チャットの応答メッセージ内容
    """
    system_message = {
        "role": "system",
        "content": "あなたは優秀なアシスタントです。"
    }
    user_message = {
        "role": "user",
        "content": content
    }

    response = client.chat.completions.create(
        messages=[system_message, user_message],
        max_completion_tokens=1000,
        model=model
    )

    return response.choices[0].message.content

