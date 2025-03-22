# Genshin Artifact OCR - 仮想環境構築手順

このプロジェクトでは、Pythonの仮想環境を使用して依存関係を管理することを推奨します。以下の手順に従って、仮想環境を構築し、必要なパッケージをインストールしてください。

## 1. 仮想環境の作成

まず、プロジェクトのルートディレクトリに仮想環境を作成します。以下のコマンドを実行してください。

```bash
python -m venv venv
```

このコマンドは、`venv`という名前の仮想環境を作成します。

## 2. 仮想環境のアクティベート

作成した仮想環境をアクティベートします。

### Windowsの場合

```bash
venv\Scripts\activate
```

### macOS/Linuxの場合

```bash
source venv/bin/activate
```

仮想環境がアクティベートされると、ターミナルのプロンプトに`(venv)`と表示されます。

## 3. 依存関係のインストール

必要なPythonパッケージをインストールします。このプロジェクトでは、`requirements.txt`ファイルに依存関係が記述されていると仮定します。以下のコマンドを実行して、必要なパッケージをインストールしてください。

```bash
pip install -r requirements.txt
```

もし`requirements.txt`ファイルが存在しない場合は、以下のパッケージを手動でインストールしてください。

```bash
pip install pytesseract Pillow Levenshtein
```

## 4. プロジェクトの実行

仮想環境がアクティベートされた状態で、`main.py`スクリプトを実行します。

```bash
python main.py
```

## 5. 仮想環境のディアクティベート

作業が完了したら、以下のコマンドを実行して仮想環境をディアクティベートします。

```bash
deactivate
```

これで、Genshin Artifact OCRプロジェクトを実行するための仮想環境が構築されました。
