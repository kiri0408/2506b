
from api_utils import load_api_data, create_client
import base64

def encode_image(image_path):
    with open(image_path,"rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# API接続情報の読み込み
api_data = load_api_data("api_gpt4o.json")

# AzureOpenAIクライアントとモデル名の作成
client, model = create_client(api_data)

image_path =r'1_機器の画像サンプル.jpg'
base64_image = encode_image(image_path)

str_system ="あなたは画像について説明する賢いアシスタントです。"
str_user  = """
以下の画像に含まれる図についてそれぞれ説明してください。
- 読み取れる内容を全て詳細に説明すること。
- 数値の間違いは無いようにしっかりと確認すること。
- 抽出した結果はMarkdownで表形式で出力すること。
""" 

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role":"system","content":str_system},
        {"role":"user","content":[
            {"type":"text","text":str_user},
            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{base64_image}"}},
        ]}
    ]
)

print(response.choices[0].message.content)

