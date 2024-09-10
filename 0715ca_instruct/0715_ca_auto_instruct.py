# %%
from vllm import SamplingParams, LLM
from tqdm import tqdm
from datasets import load_dataset, concatenate_datasets
from datasets import Dataset, concatenate_datasets
from datetime import datetime
import json
import os
from src.generator import inst_dict, prepare_records
from src.clean_utils import clean
import random
import glob
import pandas as pd
import time
import sys

#args = sys.argv
import time


# job idを取得
# job_id=os.environ['$SLURM_JOB_ID']
#job_id = args[1]
#flag_file_path = f"flags/{job_id}.txt"

import time
import random

def generate_random_seed():
    # 現在時刻を取得（秒単位の少数部分を含む）
    current_time = time.time()
   
    for i in range(3):
        continue
    # 現在時刻の少数部分を取得
    fractional_time = current_time - int(current_time)
    
    # ランダム値を生成
    random_value = random.random()
    
    # 現在時刻の少数部分とランダム値を組み合わせてシードを生成
    seed = int((fractional_time + random_value) * 10**8)  # 適宜倍率を調整
    
    return seed

# ランダムシードを生成
seed = generate_random_seed()
print(f'Generated random seed: {seed}')

# 生成したシードを使ってランダムシードを設定
random.seed(seed)


#with open(flag_file_path, "w") as f:
#    f.write("1")

"""
def load_flag():
    with open(flag_file_path, "r") as f:
        flag = f.read().strip()

    print("flag: ", flag)
    print("flag==1: ", flag == "1")

    return flag == "1"


print(load_flag())
"""
#wait_time = random.randint(1, 30)
#time.sleep(wait_time)

#####################
# 設定関連
n_records = 300
out_dir = "0715ca_auto_instruct"
####################

################
# メイン

os.system(f"mkdir -p {out_dir}")

current_time_no_symbols = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S").replace("-", "").replace(":", "").replace(" ", "")
out_path = f"{out_dir}/model_{current_time_no_symbols}.jsonl"


genres = """
指定されたトピックに関するエッセイを書く
特定のスタイルやトーンで文章を作成する
短編小説の続きを書く
指定された単語を含む詩を作成する
ニュース記事の要約を生成する
指定されたテキストから質問に答える
トリビアクイズに答える
ドキュメント内の特定情報を検索して答える
スポーツの試合結果について質問に答える
英文を日本語に翻訳する
日本語のニュース記事を英語に翻訳する
特定の専門用語を含む技術文書を翻訳する
文学作品の一部を翻訳する
映画の字幕を翻訳する
データセットから特定の統計情報を抽出する
グラフを生成してデータの可視化を行う
データのクレンジングと前処理を行う
機械学習モデルのトレーニングと評価を行う
データセットの特徴量エンジニアリングを行う
特定のアルゴリズムを実装する
バグのあるコードを修正する
指定された機能を持つプログラムを作成する
コードレビューを行う
テストケースを作成し、プログラムの動作を確認する
指定されたテーマに基づいてキャラクターデザインを行う
ストーリーボードを作成する
音楽の作曲や歌詞の作成
イラストのラフスケッチを描く
ビデオ編集のためのシナリオを作成する
顧客からの問い合わせに対して丁寧な対応をする
トラブルシューティングガイドを提供する
商品の使い方について説明する
返品ポリシーについて説明する
苦情に対して適切な対応をする
特定のトピックについて講義ノートを作成する
学生の質問に答える
課題や試験問題を作成する
教材をレビューして改善点を提案する
教育用ビデオのスクリプトを作成する
ビジネスプランを作成する
マーケティング戦略を提案する
競合分析を行う
財務レポートを分析する
プロジェクト管理計画を作成する
症状に基づいて適切な診断を提供する
健康的な食事プランを作成する
トレーニングプランを個別にカスタマイズする
医療研究の要約を作成する
病気予防のためのガイドラインを提供する
法律相談に対する適切なアドバイスを提供する
法的文書を作成する
倫理的なジレンマに対する解決策を提案する
事件の概要を分析して報告書を作成する
裁判の模擬シナリオを作成する
環境保護に関するレポートを作成する
持続可能なビジネスモデルを提案する
環境影響評価を行う
リサイクルプログラムの設計
エネルギー効率の改善策を提案する
文化的なイベントの企画を行う
異文化交流のためのガイドを作成する
社会問題に関するエッセイを書く
社会調査の結果を分析する
哲学的な論文を書く
宗教的なテキストの解釈を行う
倫理学のケーススタディを分析する
哲学者の理論を比較する
実験プロトコルを作成する
科学論文の要約を作成する
技術的なマニュアルを作成する
イノベーションの提案を行う
科学データの解析を行う
映画のレビューを作成する
ゲームのストーリーボードを作成する
演劇の脚本を書く
音楽アルバムのレビューを作成する
テレビ番組のプロットを作成する
コミュニケーションスキル向上のためのガイドを作成する
カウンセリングセッションのシナリオを作成する
心理学的理論の比較を行う
ストレス管理のためのプランを作成する
人間関係の問題解決策を提案する
投資戦略を提案する
予算計画を作成する
財務分析レポートを作成する
ポートフォリオの評価を行う
退職後の資金計画を作成する
旅行プランを作成する
観光地のガイドを作成する
旅行レビューを作成する
ローカル文化の紹介を行う
旅行予算を計画する
DIYプロジェクトの手順を作成する
クラフトのアイデアを提案する
家庭修理のガイドを作成する
ガーデニングプランを作成する
手芸作品の作り方を説明する
トレーニングプログラムを作成する
スポーツイベントのレポートを書く
運動の効果を分析する
チーム戦略を立てる
スポーツニュースの要約を作成する
文法訂正
翻訳
要約
情報抽出
自然言語推論
指定形式の出力タスク
テーブルの作成
リストの作成
フォーマットされたテキスト出力
特定のテンプレートに基づいた文の生成
スケジュールやカレンダーの作成
箇条書きリストの生成
タグ付け
辞書形式の出力
JSON形式のデータ生成
YAML形式のデータ生成
専門的なタスク
技術文書の作成
医学的アドバイスの提供
法律文書の解釈
科学的なデータ分析の説明
教育資料の作成
プログラミングコードの生成
論文の構造化
クリエイティブタスク
物語の創作
詩の生成
映画やゲームのプロット提案
キャラクタープロフィールの作成
シナリオライティング
インタラクティブタスク
チューリングテストの実施
仮想アシスタントとしての業務
カスタマーサポートのシミュレーション
ゲームのプレイアシスタント
特定の操作指示タスク
ファイルの操作（コピー、移動、削除）
データベースクエリの作成
コマンドライン操作の指示
ソフトウェアの設定変更手順の案内
データ処理タスク
データのクリーニング
データの統計解析
データの視覚化
予測モデルの構築
データセットのラベリング
複雑な指示追従タスク
長期プロジェクトの管理
多段階プロセスの指示
マルチステップ推論
複数人のスケジュール調整
テキスト生成および要約
質問応答
対話システム開発（チャットボットなど）
翻訳タスク（多言語対応）
感情分析および意見分類
コード補完およびデバッグ
データクリーニングおよび前処理
コンテンツモデレーションとフィルタリング
ナレッジグラフの構築と推論
自動ドキュメント生成
音声認識および音声合成
画像キャプション生成
機械翻訳およびローカリゼーション
フィンテックアプリケーション（詐欺検出など）
医療データ解析および診断支援
教育用コンテンツ生成およびカスタマイズ
環境モニタリングおよびレポート作成
顧客サービス自動化
法的文書解析およびレビュー
ニュース記事の自動生成および編集
文章生成タスク
物語の続きの執筆
ニュース記事の要約
製品レビューの作成
学術論文の要約
書籍の紹介文作成
ファッションコーディネートを提案する
美容ケアのガイドを作成する
トレンドレポートを作成する
メイクアップのチュートリアルを作成する
ファッションショーのレビューを書く
一般的な指示追従タスク
質問応答
会話の文脈保持
文法訂正
翻訳
要約
情報抽出
自然言語推論
指定形式の出力タスク
テーブルの作成
リストの作成
フォーマットされたテキスト出力
特定のテンプレートに基づいた文の生成
スケジュールやカレンダーの作成
箇条書きリストの生成
タグ付け
辞書形式の出力
JSON形式のデータ生成
YAML形式のデータ生成
専門的なタスク
技術文書の作成
医学的アドバイスの提供
法律文書の解釈
科学的なデータ分析の説明
教育資料の作成
プログラミングコードの生成
論文の構造化
クリエイティブタスク
物語の創作
詩の生成
映画やゲームのプロット提案
キャラクタープロフィールの作成
シナリオライティング
インタラクティブタスク
チューリングテストの実施
仮想アシスタントとしての業務
カスタマーサポートのシミュレーション
ゲームのプレイアシスタント
特定の操作指示タスク
ファイルの操作（コピー、移動、削除）
データベースクエリの作成
コマンドライン操作の指示
ソフトウェアの設定変更手順の案内
データ処理タスク
データのクリーニング
データの統計解析
データの視覚化
予測モデルの構築
データセットのラベリング
複雑な指示追従タスク
長期プロジェクトの管理
多段階プロセスの指示
マルチステップ推論
複数人のスケジュール調整
テキスト生成および要約
質問応答
対話システム開発（チャットボットなど）
翻訳タスク（多言語対応）
感情分析および意見分類
コード補完およびデバッグ
データクリーニングおよび前処理
コンテンツモデレーションとフィルタリング
ナレッジグラフの構築と推論
自動ドキュメント生成
音声認識および音声合成
画像キャプション生成
機械翻訳およびローカリゼーション
フィンテックアプリケーション（詐欺検出など）
医療データ解析および診断支援
教育用コンテンツ生成およびカスタマイズ
環境モニタリングおよびレポート作成
顧客サービス自動化
法的文書解析およびレビュー
ニュース記事の自動生成および編集
文章生成タスク
物語の続きの執筆
ニュース記事の要約
製品レビューの作成
学術論文の要約
書籍の紹介文作成

対話タスク

カスタマーサポートのシミュレーション
医療相談のシミュレーション
コーチングやカウンセリングの対話
言語学習者向けの会話パートナー
質問応答のエージェント

クリエイティブタスク

詩の作成
キャラクターの設定作成
映画やテレビ番組のプロット作成
広告コピーの作成
演劇の台本作成

情報提供タスク

製品の比較とレビュー
観光地のガイド
イベントの詳細情報提供
技術サポートガイドの提供
健康やフィットネスのアドバイス
データ処理タスク
データの分類
データのクリーニング
統計分析の結果解釈
データ可視化の説明
レポートの自動生成
最大値の取得
最小値の取得
平均値の取得
数のカウント
書き出しの変更
翻訳タスク
技術文書の翻訳
文化的なコンテキストを考慮した翻訳
言語学習者向けの翻訳
文学作品の翻訳
法律文書の翻訳
教育タスク
教材の作成
授業計画の作成
学生の質問への回答
試験問題の作成
学習の進捗管理
ビジネスタスク
プロジェクト計画の作成
市場調査の報告書作成
企業戦略の提案
業務プロセスの最適化
リスクマネジメントの計画作成

エンターテイメントタスク

ゲームのストーリーライン作成
スタンドアップコメディの台本作成
ミュージックビデオのコンセプト作成
パズルやクイズの作成
映画のレビュー作成

法律および規制タスク

法律相談のシミュレーション
契約書のレビュー
規制遵守ガイドの作成
法的リスクの分析
判例の解釈
スケジュールに従ってリマインダーを設定する
ユーザーの指定に基づいたアジェンダを作成する
指定されたフォーマットでメールを作成する
会議の議事録を自動的に作成する
特定のトピックに基づいた質問リストを作成する
指定された資料に基づいてプレゼンテーションスライドを作成する
チームメンバー間のタスクの割り当てを行う
プロジェクトの進捗状況を追跡する
特定のプロジェクトに関する週次レポートを作成する
ユーザーの要望に基づいたレポートをカスタマイズする
特定の形式で請求書を生成する
クライアントの要件に従って契約書を作成する
指定されたガイドラインに基づいてポリシードキュメントを作成する
特定のトピックに関するFAQを作成する
ユーザーマニュアルの更新作業を行う
カスタマーサポートの問い合わせに対して定型文を生成する
技術的な問い合わせに対して詳細な手順を提供する
製品のトラブルシューティングガイドを更新する
バグ報告書を作成し、対応状況を追跡する
ソフトウェアのインストールガイドを作成する
ユーザーの指示に従ってカスタムレポートを生成する
テストケースに基づいてテストレポートを作成する
指定された仕様に基づいてプログラムコードを生成する
コードのリファクタリングを行う
指定されたアルゴリズムを実装し、性能を評価する
APIドキュメントを作成する
ユーザーの入力に基づいてフォームを自動生成する
データベーススキーマを設計し、マイグレーションスクリプトを生成する
ユーザーのリクエストに基づいてカスタムダッシュボードを作成する
指定された要件に基づいてモバイルアプリケーションを開発する
テスト自動化スクリプトを作成する
指定されたフレームワークに従ってウェブサイトを構築する
ユーザーの要望に基づいてデザインテンプレートを作成する
SEOに最適化されたコンテンツを生成する
SNS用の投稿スケジュールを作成する
指定されたキーワードに基づいてブログ記事を作成する
マーケティングキャンペーンのプランを作成する
カスタマーサーベイを設計し、分析結果をレポートする
顧客データに基づいてパーソナライズドメッセージを生成する
指定されたデータセットから顧客セグメンテーションを行う
特定のビジネスニーズに基づいて財務モデルを作成する
競合分析レポートを作成する
指定されたリソースを用いてリサーチレポートを作成する
ユーザーのフィードバックに基づいて製品改善案を提案する
市場動向を分析し、レポートを作成する
投資ポートフォリオのパフォーマンスを評価する
予算計画書を作成し、提案する
指定された法律に基づいてコンプライアンスチェックリストを作成する
社内ポリシーのドラフトを作成する
法的文書のレビューを行い、修正点を提案する
指定された規制に基づいてビジネスプランを適応させる
リスク管理計画を作成し、実行する
指定された環境基準に基づいてエコプランを作成する
持続可能な開発目標に基づいてプロジェクトを計画する
エネルギー効率の改善策を提案する
環境影響評価レポートを作成する
リサイクルプログラムの設計と実施を行う
異文化交流イベントの企画を行う
社会問題に関するパネルディスカッションを企画する
哲学的論文のテーマを提案する
科学研究の実験プロトコルを作成する
技術的なマニュアルの更新作業を行う
新しいイノベーションアイデアを提案する
科学データの解析結果をレポートする
映画レビューを執筆する
演劇の脚本を作成する
コミュニケーションスキル向上のためのワークショップを企画する
カウンセリングセッションのシナリオを作成する
投資戦略のポートフォリオを提案する
退職後の資金計画を作成する
観光地の詳細ガイドを作成する
旅行プランをカスタマイズする
DIYプロジェクトの詳細手順を提供する
スポーツイベントのレポートを執筆する
ファッションコーディネートの提案を行う
美容ケアガイドを作成する
トレンドレポートを提供する
メイクアップのチュートリアルを作成する
会話の文脈を保持しながら複雑な質問に答える
古典文学の現代語訳を提供する
ゲームのストーリーラインを作成する
スタンドアップコメディの台本を執筆する
ミュージックビデオのコンセプトを作成する
パズルやクイズを作成する
映画のレビューを執筆する
法律相談のシミュレーションを行う
契約書のレビューを行う
法的リスクの分析を提供する
SNS投稿の作成を行う
マーケティングキャンペーンの計画を提供する
顧客ペルソナを作成する
技術サポートガイドを提供する
ソフトウェアのデバッグを行う
トラブルシューティングガイドを提供する
セキュリティ対策のアドバイスを提供する
マーケティングタスク

SNS投稿の作成
マーケティングキャンペーンの計画
顧客ペルソナの作成
ブログ記事の執筆
メールマーケティングのコンテンツ作成

テクニカルサポートタスク
ソフトウェアのデバッグ
トラブルシューティングガイドの作成
ユーザーガイドの作成
システムの最適化提案
セキュリティ対策のアドバイス
文体変換
公式文書をカジュアルな文体に変換
口語体を書き言葉に変換
子供向けの文章を大人向けに変換
科学論文を一般読者向けに変換
古典文学の現代語訳
ジャンル変換
小説を詩に変換
ニュース記事をブログ形式に変換
技術マニュアルをプレゼンテーションスライドに変換
漫画のストーリーボードを小説形式に変換
映画のシナリオを舞台劇の台本に変換
視点変換
一人称視点を三人称視点に変換
主人公の視点を別のキャラクターの視点に変換
現在形を過去形に変換
観察者の視点を参加者の視点に変換
第三者の視点を第一人者の視点に変換
情報抽出
テキスト抽出
学術論文から重要な結果や結論を抽出
ニュース記事から主要な出来事を抽出
長文からキーワードやフレーズを抽出
製品レビューから肯定的・否定的な意見を抽出
会議議事録から重要な決定事項を抽出
データ抽出
HTMLソースコードから特定のデータを抽出
CSVファイルから特定の列データを抽出
APIレスポンスから必要な情報を抽出
画像からテキストデータを抽出
センサーデータから異常値を抽出
アニメ
構造化情報抽出
テキストから名前、日付、場所を抽出
会話ログから発話者と発言内容を抽出
製品仕様書から技術スペックを抽出
論文から引用情報を抽出
医療記録から患者の診断情報を抽出

論理思考

論理パズル解決
数独やクロスワードパズルの解決
論理パズルの解決手順の説明
条件付き推論問題の解決
トリビア問題の解決
推理小説の犯人特定

論理的分析
データセットからの傾向分析
アルゴリズムの最適化
複雑なシステムの原因と結果の分析
統計的データの解釈
ビジネスプロセスの改善提案
ユーモア
皮肉
お笑い
推論と証明
数学的証明の手順説明
哲学的命題の論証
プログラムコードのバグ検出と修正
仮説の検証手順の作成
法的議論の構築
JSON
JSON
JSON
JSON
JSON
JSON
YAML
YAML
YAML
YAML
YAML
YAML
CSV
CSV
CSV
課題の分析
欠点の分析
"""
genre_list = genres.split("\n")
genre_list = [i for i in genre_list if i != ""]


def prepare_prompt():
    #random.seed(time.time())
    genre1 = random.choice(genre_list)
    genre2 = random.choice(genre_list)
    genre3 = random.choice(genre_list)
    genres=f"{genre1},{genre2},{genre3}"
    return f"""#指定したジャンルについて､大規模言語モデルの指示追従性を高めるための問題をランダムに一つ生成しなさい
- 問題文のみを出力し､他の内容は一切出力しないこと
- ジャンル: {genres}
""", genres


def prepare_records(
    n_records=300,
):

    records = []
    for _ in range(n_records):
        text, genre = prepare_prompt()
        text = f"""<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant"""

        records.append(
            {
                "genre": genre,
                "prompt": text,
            }
        )

    return records


print("init llm")
model_name = "cyberagent/calm3-22b-chat"
llm = LLM(model=model_name, trust_remote_code=True,
          max_model_len=4000,
          # max_model_len=7000,
          # gpu_memory_utilization=0.4,
          )
while True:

    # 質問生成
    records = prepare_records()

    prompts = [record["prompt"] for record in records]
    random_number = random.uniform(0.05, 0.99)
    outputs1 = llm.generate(
        prompts,
        sampling_params=SamplingParams(
            temperature=random_number,
            max_tokens=2048,
            repetition_penalty=1.05,
        )
    )

    # answer
    ask_prompts = []
    for output in outputs1:
        question = (output.outputs[0].text).strip()
        inst = ""
        prompt = f"""<|im_start|>user
{inst}{question}<|im_end|>
<|im_start|>assistant"""

        ask_prompts.append(prompt)
        # print(prompt)

    outputs2 = llm.generate(
        ask_prompts,
        sampling_params=SamplingParams(
            temperature=0.1,
            max_tokens=2048,
            repetition_penalty=1.05,
        )
    )

    for record, q, a in zip(records, outputs1, outputs2):
        q = (q.outputs[0].text).strip()
        a = (a.outputs[0].text).strip()

        q = clean(q, lang="ja")
        a = clean(a, lang="ja")

        if q == "":
            # print("rejected")
            # print(ja_output.outputs[0].text)
            continue
        if a == "":
            # print("rejected")
            # print(eng_output.outputs[0].text)
            continue

        record["instruction"] = q
        record["output"] = a
        record["text"]=f"user: {q}\nassistant: {a}"
        record.pop("prompt")

        # print("saving to "+out_path)
        with open(out_path, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

