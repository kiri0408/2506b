import json
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI  

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


# def create_client2(api_data) :
#     """提供されたAPI情報を使ってAzureOpenAIクライアントを作成する関数"""
#     return AzureChatOpenAI(
#          deployment_name=api_data["model"], 
#          openai_api_version=api_data["api_version"], 
#          openai_api_key=api_data["api_key"],
#          azure_endpoint=api_data["azure_endpoint"],
#          temperature=0
#     )

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

#     return response.choices[0].message.content

# def get_image_description(client, model, image_path):
#     """
#     画像ファイルをAzureOpenAIに渡し、説明文を取得する関数

#     Args:
#         client: AzureOpenAIクライアントインスタンス
#         model: 使用するモデル名（文字列）
#         image_path: 画像ファイルのパス（文字列）

#     Returns:
#         str: 画像の説明文
#     """
#     with open(image_path, "rb") as image_file:
#         image_data = image_file.read()

#     # 画像をバイナリとしてmessagesに含める形式はOpenAIのVision API仕様に準拠
#     # ここでは画像をbase64エンコードしてテキストとして送る例を示す
#     import base64
#     encoded_image = base64.b64encode(image_data).decode("utf-8")

#     system_message = {
#         "role": "system",
#         "content": "あなたは優秀なアシスタントです。画像の内容を説明してください。"
#     }
#     user_message = {
#         "role": "user",
#         "content": f"以下の画像を説明してください。\ndata:image/jpeg;base64,{encoded_image}"
#     }

#     response = client.chat.completions.create(
#         messages=[system_message, user_message],
#         #max_completion_tokens=1000,
#         model=model
#     )

#     return response.choices[0].message.content
