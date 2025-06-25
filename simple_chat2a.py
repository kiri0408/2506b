
"""
o3-miniを使って難しい数学の問題を解かせてみる試行。 
file_pathを'api_gpt4o.json' に切り替えた場合は正解できないことも確認する。 
ストリーミング出力に対応。
"""

import api_utils2  as api_utils  

#file_path ='api_gpt4o.json'                       # API接続情報のファイルパス
file_path ='api_o3_mini.json'
api_data = api_utils.load_api_data(file_path)     # API接続情報を取得
client, model = api_utils.create_client(api_data) # AIクライアント作成、モデル名を取得


content = """
一の位が0でない2けたの自然数nについて，「2乗して，求めた数の下2けたの値を答える」という操作を行います。
この操作を複数回行うときは，前の操作で求めた値に対して同じ操作を繰り返します。また，04のように操作後の十の位が0のときは，
次の操作では一の位を2乗して値を求めるものとします。（この場合は4^2=16）

例えば，n=54のとき，

1回操作を行うと，54^2=2916 よって，16
2回操作を行うと，16^2=256 よって，56
3回操作を行うと，56^2=3136 よって，36

このとき，次の問いについてステップバイステップでしっかり思考して答えなさい。

2018回操作を行って，96になるnの値をすべて求めなさい。
※ただし，何回か操作を行って96になるnで，初めて96になるまで6回以上操作を行うものは存在しないことがわかっている。

"""

# 正解    n = 42, 44, 56, 58, 92, 94
# 問題URL  https://www.sapix.co.jp/blog/8350/
# 正解URL  https://www.sapix.co.jp/wp/wp-content/uploads/2022/11/math201909-a.pdf

response_generator = api_utils.get_response(client, model, content, stream=True)  # ストリーミングでチャットを実行

for chunk in response_generator:
    print(chunk, end='', flush=True)
print()  # 最後に改行を入れる
