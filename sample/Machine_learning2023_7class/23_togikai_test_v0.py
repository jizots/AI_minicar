# 学習結果を確認するプログラム

# ライブラリのimport
import numpy as np
import pickle
from sklearn import metrics
from sklearn.neural_network import MLPClassifier
import glob
import pathlib

# データの読み込みと確認
print("現在のディレクトリにあるcsvファイルは以下になります。\nない場合は持ってきてください\n")
p_temp = pathlib.Path('./').glob('*.csv')
for p in p_temp:
    print(p.name)
print("\nファイル名を入力してください\n")
csv=str(input())
# テストデータ(精度を確認するためのデータ)の読み込み
# ・テストデータは学習データと異なるものを使用
# ・学習データの精度に対しテストデータの精度が大きく低下する場合は「過学習」の可能性
test_data = np.loadtxt("./"+csv, delimiter=" ")

# 学習済みモデルの読み込み
model = pickle.load(open("./save_model.pickle", 'rb'))
# センサー値を学習時と同じく正規化するため平均・標準偏差の読み込み
X_mean = np.loadtxt("./save_mean.txt", delimiter=" ")
X_std = np.loadtxt("./save_std.txt", delimiter=" ")

# センサー値
X_test = test_data[:, 4:]
# 正規化
X_test_norm = (X_test - X_mean) / X_std

# 予測
pred = model.predict(X_test_norm)

# 予測で出力されるクラスIDをsteer値に変換
pred_steer = []
for i in range(pred.shape[0]):
    if pred[i] == 0:
        pred_steer.append(-0.9)
    elif pred[i] == 1:        
        pred_steer.append(-0.6)
    elif pred[i] == 2:        
        pred_steer.append(-0.3)
    elif pred[i] == 3:        
        pred_steer.append(0.)
    elif pred[i] == 4:        
        pred_steer.append(0.3)
    elif pred[i] == 5:        
        pred_steer.append(0.6)
    elif pred[i] == 6:        
        pred_steer.append(0.9)

pred_steer = np.array(pred_steer)

# 予測精度を確認するためのsteer値の正解データ
steer = test_data[:, 1]

# steer値をクラスのIDに変換
class_steer = []
for i in range(steer.shape[0]):
    if steer[i] == -0.9:
        class_steer.append(0)
    elif steer[i] == -0.6:
        class_steer.append(1)
    elif steer[i] == -0.3:
        class_steer.append(2)
    elif steer[i] == 0.:
        class_steer.append(3)
    elif steer[i] == 0.3:
        class_steer.append(4)
    elif steer[i] == 0.6:
        class_steer.append(5)
    elif steer[i] == 0.9:
        class_steer.append(6)

y_test = np.array(class_steer)

# 正解率の確認
print("正解率{0:.3f}".format(model.score(X_test_norm, y_test)))
