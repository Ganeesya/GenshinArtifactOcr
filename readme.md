# Genshin Artifact OCR - 使い方

このREADMEでは、Genshin Artifact OCRを使用するための手順を説明します。

## 1. 必要なファイルの準備

-   `annotation_tool.py`: 認識範囲を設定するためのツール
-   `main.py`: スクリーンショットを撮ってOCRを実行するスクリプト
-   `artifactNameToPositonMap.json`: 聖遺物の名前と位置のマッピングデータ
-   `ocrSetting/ocr1.json`: OCR設定ファイル（annotation\_toolで生成）
-   `requirements.txt`: 必要なPythonパッケージのリスト

## 2. 仮想環境の構築

まず、仮想環境を構築し、必要なパッケージをインストールします。

```bash
python -m venv venv
call venv\\Scripts\\activate
pip install -r requirements.txt
```

## 3. 認識範囲の設定

`annotation_tool.py`を実行して、原神のウィンドウサイズに合わせた認識範囲を設定します。

```bash
call venv\\Scripts\\activate
python annotation_tool.py
```

1.  `Load Image`ボタンをクリックして、原神の聖遺物詳細画面のスクリーンショットを読み込みます。
2.  各項目（Artifact Name, Main Type, Main Value, Sub Stats, Level, Position）に対して、画面上で対応する領域をドラッグして選択します。
3.  `Save Configuration`ボタンをクリックして、設定を`ocrSetting/ocr1.json`に保存します。

## 4. スクリーンショット撮影とOCR実行

`main.py`を実行して、スクリーンショットを撮影し、OCRを実行します。

```bash
call venv\\Scripts\\activate
python main.py
```

`main.py`は、以下の処理を行います。

1.  原神のウィンドウをキャプチャします。
2.  `ocrSetting/ocr1.json`に保存された設定に基づいて、聖遺物の各項目のOCRを実行します。
3.  OCRの結果をコンソールに出力します。

## 5. 注意事項

-   原神のウィンドウサイズが変更された場合は、`annotation_tool.py`で認識範囲を再設定する必要があります。
-   OCRの精度は、スクリーンショットの品質やOCRエンジンの設定に依存します。
-   `artifactNameToPositonMap.json`は、聖遺物の名前と位置のマッピングデータです。必要に応じて編集してください。

## 6. その他のスクリプト

-   `run_main.bat`: `main.py`を実行するためのバッチファイル
-   `run_annotation_tool.bat`: `annotation_tool.py`を実行するためのバッチファイル
-   `setup_venv.bat`: 仮想環境を構築するためのバッチファイル

これらのバッチファイルを使用すると、コマンドを簡単に入力できます。
