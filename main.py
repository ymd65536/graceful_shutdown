import signal
import sys
from threading import Event, Thread
import threading
import time
import datetime

WAIT_SECONDS_AFTER_SIGTERM = 1  # SIGTERMを受け取ってから強制終了するまでの待機時間

sigterm_event = Event()
exit_event = Event()


def count_threads(prefix):
    """
    スレッド数取得
    :param prefix:カウント対象のスレッド名プレフィックス
    :return:スレッド数
    """
    threads = threading.enumerate()
    target_threads = [
        t for t in threads
        if t.name.startswith(prefix)
    ]
    return len(target_threads)


def handle_sigterm(signum, frame):
    print("SIGTERM received. Preparing to shut down...")
    sigterm_event.set()

    if not exit_event.wait(WAIT_SECONDS_AFTER_SIGTERM):
        print(f"{WAIT_SECONDS_AFTER_SIGTERM} seconds have passed. Force exit...")

        count = 0
        # ここに強制終了前に必要な後処理を書く
        while count_threads("service_thread") > 0:
            print(f"wait exit child threads.{count}")
            time.sleep(1)
            count += 1
        time_now = datetime.datetime.now()
        print(time_now)
        can_gracefully_exit = True
        exit_event.set()
        sys.exit(0)
    else:
        can_gracefully_exit = False
        sys.exit(1)

    if can_gracefully_exit:
        print("gracefully exit")
        sys.exit(0)
    else:
        print("force exit")
        sys.exit(1)


def service():
    # 一回に時間がかかる処理
    print("loop start")
    time_now = datetime.datetime.now()
    print(time_now)
    time.sleep(20)
    print("loop finish")
    exit_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    service_thread = Thread(
        target=service,
        name="service_thread"
    )
    # service_thread.daemon = True  # メインスレッドの終了時にservice_threadも終了する
    service_thread.start()
    exit_event.wait()
