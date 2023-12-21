## マルチプロセスのインポート
from multiprocessing import Process
#from concurrent.futures import ProcessPoolExecutor ##multiprocessingよりも現代的な機能らしいので採用したが、エラーが出た。

## 共有リソース管理
from multiprocessing import Manager

## 自作する3つの機能をインポート
import toyota_accel as ac
import toyota_sensor as se
import toyota_steering as st


def main():
    print('main process is starting')
    ## 共有リソースの変数の作成
    manager = Manager()
    shared_data = manager.dict()
    
    ## プロセスの機能を定義
    sensor_process = Process(target=se.sensor, args=(shared_data,))
    # accel_process = Process(target=ac.accel, args=(shared_data,))
    steering_process = Process(target=st.steering, args=(shared_data,))

    ## 3つの機能を別プロセスで実行する
    sensor_process.start()
#    accel_process.start()
    steering_process.start()

    ## プロセスの終了を待つ
    sensor_process.join()
#    accel_process.join()
    steering_process.join()

if __name__ == "__main__":
    main()
