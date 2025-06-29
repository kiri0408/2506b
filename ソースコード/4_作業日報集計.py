
from api_utils import load_api_data, create_client
import base64
from pydantic import BaseModel, ValidationError
from typing import List
import os
import json
import polars as pl


def encode_image(image_path):
    """
    画像ファイルを読み込み、base64エンコードして文字列として返す
    """
    with open(image_path,"rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


class Item(BaseModel):
    """
    1つの品目の情報を表すモデル
    """
    hinmei : str    # 品名
    quantity: int   # 生産数
    start_time: str # 開始時刻
    end_time: str   # 終了時刻

class ImageDescription(BaseModel):
    """
    画像から抽出した情報全体を表すモデル
    """
    work_date: str # datetime.date  # 日付
    name : str # 氏名
    items: List[Item]


def process_image(image_path, client, model, str_system, str_user):
    """
    画像をbase64エンコードし、AIに送信してJSON形式の応答を受け取る。
    受け取ったJSONをパースし、pydanticでバリデーションを行い、
    polarsのDataFrameに変換して返す。
    """
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content":str_system},
            {"role":"user","content":[
                {"type":"text","text":str_user},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]
    )
    content = response.choices[0].message.content
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = content[start_idx:end_idx+1]
        try:
            data = json.loads(json_str)
            description = ImageDescription.model_validate(data)
            print(f"パース成功: {image_path}")
            print(f"作業日: {description.work_date}")
            print(f"氏名: {description.name}")
            for item in description.items:
                print(f"品名: {item.hinmei}, 数量: {item.quantity}, 開始時刻: {item.start_time}   終了時刻：{item.end_time} ")
            items_dicts = [item.model_dump() for item in description.items]
            df = pl.DataFrame(items_dicts)
            df = df.with_columns([
                pl.lit(description.work_date).alias("work_date"),
                pl.lit(description.name).alias("name")
            ])
            # start_time, end_time を時刻型に変換し別名で追加
            df = df.with_columns([
                pl.col("start_time").str.strptime(pl.Time, "%H:%M").alias("start_time_parsed"),
                pl.col("end_time").str.strptime(pl.Time, "%H:%M").alias("end_time_parsed")
            ])
            # 差分時間（分）を計算して追加
            df = df.with_columns([
                ((pl.col("end_time_parsed").cast(pl.Int64) - pl.col("start_time_parsed").cast(pl.Int64)) / 60_000_000_000).alias("duration_minutes")
            ])
            return df
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"JSONのパースまたはバリデーションに失敗しました: {image_path}")
            print(e)
            print("AIの返答全文:")
            print(content)
            return None
    else:
        print(f"JSON形式のデータが見つかりませんでした: {image_path}")
        print("AIの返答全文:")
        print(content)
        return None

def main():
    """
    メイン処理
    - API接続情報の読み込み
    - 画像フォルダ内のjpgファイルを順に処理
    - 各画像の解析結果をDataFrameに変換しリストに蓄積
    - 全てのDataFrameを結合し、詳細データと集計表をHTMLで出力
    """
    # API接続情報の読み込み
    api_data = load_api_data("api_gpt4o.json")
    #api_data = load_api_data("api_o3_mini.json")

    # AzureOpenAIクライアントとモデル名の作成
    client, model = create_client(api_data)

    str_system ="あなたは画像から情報を抽出する賢いアシスタントです。"
    str_user  = """
    以下の画像に含まれる表について、情報を説明してください。
    - 数値の間違いは無いようにしっかりと確認すること。
    - 抽出した結果はJSON形式で以下のフォーマットに従って出力してください。
    フォーマット例:
    {
      "work_date" : "2024/02/01",
      "name" : "鈴木一郎" ,  
      "items": [
        {
          "hinmei": "タイヤ",
          "quantity": 10,
          "start_time": "09:30",
          "end_time": "11:20"
        },
        ...
      ]
    }

    JSON出力時の値は以下のデータ型とする。
      - 日付(work_date)      : 文字列(YYYY/MM/DD)
      - 氏名(name)           : 文字列
      - 品名(hinmei)         : 文字列
      - 生産数(quantity)     : 整数(int)
      - 開始時刻(start_time) : 文字列(HH:MM)
      - 終了時刻(end_time)   : 文字列(HH:MM)

    """

    folder_path = "./4_作業日報"
    all_dfs = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".jpg"):
            image_path = os.path.join(folder_path, filename)
            df = process_image(image_path, client, model, str_system, str_user)
            if df is not None:
                all_dfs.append(df)

    if all_dfs:
        combined_df = pl.concat(all_dfs)
        print("全画像の結合DataFrame:")
        print(combined_df)

        # HTML表示用に必要な列を選択し、列名を日本語に変更
        display_df = combined_df.select([
            "work_date",
            "name",
            "hinmei",
            "quantity",
            "start_time",
            "end_time",
            "duration_minutes"
        ]).rename({
            "work_date": "作業日",
            "name": "氏名",
            "hinmei": "品名",
            "quantity": "生産数",
            "start_time": "開始時刻",
            "end_time": "終了時刻",
            "duration_minutes": "作業時間(分)"
        })

        # 集計表作成：品名ごとに生産数と作業時間の合計
        summary_df = combined_df.group_by("hinmei").agg([
            pl.col("quantity").sum().alias("生産数合計"),
            pl.col("duration_minutes").sum().alias("作業時間合計(分)")
        ]).sort("hinmei")

        # HTML生成
        html = f"""
        <html>
        <head>
        <style>
        table {{
            border-collapse: collapse;
            width: 80%;
            margin-bottom: 30px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        </style>
        </head>
        <body>
        <h2>詳細データ</h2>
        {display_df.to_pandas().to_html(index=False, escape=False)}
        <h2>品名ごとの集計</h2>
        {summary_df.to_pandas().to_html(index=False, escape=False)}
        </body>
        </html>
        """

        # HTMLファイルに保存
        with open("4_作業日報集計結果.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("4_作業日報集計結果.html に詳細データと集計表を出力しました。")
    else:
        print("有効なデータがありませんでした。")

if __name__ == "__main__":
    main()
