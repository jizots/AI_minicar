## 3つの機能をインポート
import toyota_accel as ac
import toyota_sensor as se
import toyota_steering as st
## マルチプロセスの作成
from concurrent.futures import ProcessPoolExecutor ##multiprocessingよりも現代的な機能らしいので採用
## 追加するかも要素　共有リソース管理

def main():
    print('main process is starting')
    ## 追加するかも要素　初期化、共有リソース


    ## 3つの機能を別プロセスで実行する
    with ProcessPoolExecutor() as pexec:
        pexec.submit(ac.accel)
        pexec.submit(se.sensor)
        pexec.submit(st.steering)

if __name__ == "__main__":
    main()
