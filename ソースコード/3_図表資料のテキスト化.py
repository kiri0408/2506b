from api_utils import load_api_data, create_client
import fitz  # PyMuPDF
import base64
import os

def encode_image(image_path):
    """
    画像ファイルをBase64エンコードする関数

    Args:
        image_path (str): エンコードする画像ファイルのパス

    Returns:
        str: Base64エンコードされた文字列
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_pdf_to_text(pdf_path, output_folder, dpi=200):
    """
    PDFをページごとにJPEG変換し、画像をAIに渡して内容を取得しテキストとして保存する関数

    Args:
        pdf_path (str): 処理対象のPDFファイルパス
        output_folder (str): 画像およびテキストの出力先フォルダ
        dpi (int, optional): 画像変換時の解像度。デフォルトは200。

    処理の流れ:
        1. API接続情報を読み込み、AzureOpenAIクライアントを作成
        2. PDFファイルを開き、ページ数を表示
        3. 各ページをJPEG画像に変換し、指定フォルダに保存
        4. 画像をBase64エンコードし、AIに送信して内容を取得
        5. 取得した内容を連結し、テキストファイルとして保存
        6. 処理完了メッセージを表示
    """
    # API接続情報の読み込み
    api_data = load_api_data("api_gpt4o.json")

    # AzureOpenAIクライアントとモデル名の作成
    client, model = create_client(api_data)

    # プロンプトの定義
    str_system = "あなたは画像について説明する賢いアシスタントです。"
    str_user = """
以下の画像に含まれる内容を読み取ってください。
- 文章についてはそのままの文字を読み取ること（つまり、要約などの変換は不要）。
- 表についてはそのままの内容をMarkdownで出力すること。 
- 図については読み取れる内容を詳細にMarkdownで出力すること。
- 全体的に、数値の間違いは無いようにしっかりと確認すること。
- 読み取った内容のみを出力すること。（ つまり、"以下に画像の内容を読み取った結果を示します。" のようなコメントは不要）  
"""

    # 出力フォルダがなければ作成
    os.makedirs(output_folder, exist_ok=True)

    # PDFファイルを開く
    doc = fitz.open(pdf_path)
    print(f'ページ数: {doc.page_count}')

    contents_all = ""

    for page_number in range(doc.page_count):
        print(f'処理中：{page_number + 1}/{doc.page_count}')
        page = doc.load_page(page_number)

        # PDF → JPEG 変換
        pix = page.get_pixmap(dpi=dpi)

        # JPEGとして保存
        image_path = os.path.join(output_folder, f'{page_number}.jpg')
        pix.save(image_path)

        # JPEG → base64 変換
        base64_image = encode_image(image_path)

        # base64 を AIで読み取る
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": str_system},
                {"role": "user", "content": [
                    {"type": "text", "text": str_user},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},

                ]}
            ]
        )

        print(response.choices[0].message.content)
        contents_all += response.choices[0].message.content + "\n"

    # PDFファイルを閉じる
    doc.close()

    # 抽出したテキストを保存する
    output_txt = '3_図表資料サンプルPDFをテキスト化.txt'
    with open(output_txt, mode='w', encoding='utf-8') as f:
        f.write(contents_all)

    print("処理完了")

if __name__ == "__main__":
    pdf_path = r"3_図表資料サンプル.pdf"
    output_folder = "./3_図表関連"
    process_pdf_to_text(pdf_path, output_folder)
