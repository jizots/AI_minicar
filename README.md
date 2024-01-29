# ラズベリーパイを使用した自動走行ミニカー

このプロジェクトでは、ラズベリーパイを使用して制御する自動走行ミニカーを開発することを目的としています。  
超音波センサーを用いて障害物を検知し、コースを認識します。  


![image](https://github.com/jizots/AI_minicar/blob/main/minicar_pic1.jpg)
![image2](https://github.com/jizots/AI_minicar/blob/main/minicar_pic2.jpg)

## 概要

ミニカーは5つの超音波センサーを備えており、これにより周囲の障害物との距離を計測。  
そして、コース上の障害物を認識し、適切に回避します。  
このシステムはラズベリーパイ上で、Pythonで記述しています。  

# Code
## 特徴
リソースを有効活用するために、ミニカーの機能を3つにわけ、それぞれを別プロセス（つまりマルチプロセス）で実行しています。  
＊センサー  
＊ステアリング  
＊アクセル  
さらにセンサーは5つのスレッドに分かれており、各スレッドが超音波1つを動作させています。  
プロセスは共有データ（センサーが取得したデータ）にアクセスし、機能毎に挙動を決定することができます。  

## プロジェクトの実行
python main.py  

# 工作
## 購入した部品リスト
2023年12月時点で、合計は約3.5万円でした。  

Raspberry Pi4 Model B  
SanDisk microSDHC ULTRA 32GB  
バクソーハー ガンマ  
Anker PowerCore Fusion 5000  
超音波距離センサー　ＨＣ－ＳＲ０４　（5個）  
カーボン抵抗（炭素皮膜抵抗）　１／４Ｗ２２０Ω　（１００本入）  
カーボン抵抗（炭素皮膜抵抗）　１／４Ｗ４７０Ω  
ミニブレッドボード　２５穴（6個）  
PCA9685 16チャンネル 12-ビット　PWM Servo モーター ドライバー IIC モジュール  
ジャンパーワイヤー（オス-メス オス-オス メス-メス）1セット(120本入)  
３６０°連続回転サーボ（ローテーションサーボ）（2個）  
M2 ナイロンネジナット 320個セット 六角スペーサー ネジセット スタンドオフ  
タミヤ 楽しい工作シリーズ No.157 ユニバーサルプレート 2枚セット (70157)(2個)  
ミニブレッドボード用ベースプレート[ZY-002(WHITE)]  

## 参考サイト
工作は以下2つのサイトを参考にしました。  
https://minicarbattle.com/us-minicar/01-introduction/  
https://stemship.com/raspberry-pi-donkeycar/  

# Special thanks
TOYOTA, 42tokyo
