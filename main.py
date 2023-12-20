## 自作する3つの機能をインポート
import toyota_accel as ac
import toyota_sensor as se
import toyota_steering as st
## マルチプロセスのインポート
from concurrent.futures import ProcessPoolExecutor ##multiprocessingよりも現代的な機能らしいので採用
## 共有リソース管理
from multiprocessing import Manager

def main():
    print('main process is starting')
    ## 共有リソースの変数の作成
    with Manager() as manager:
        shared_data = manager.dict()


    ## 3つの機能を別プロセスで実行する
    with ProcessPoolExecutor() as pexec:
        pexec.submit(ac.accel, shared_data)
        pexec.submit(se.sensor, shared_data)
        pexec.submit(st.steering, shared_data)

if __name__ == "__main__":
    main()
