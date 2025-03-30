import logging
import queue
from datetime import datetime
from .args_parser import args

# 日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 消息队列用于线程间通信
log_queue = queue.Queue()


def log_process():
    """日志处理线程，将日志写入文件并打印到日志窗口"""
    log_file = open(args.log_file, "a", encoding="utf-8")
    log_file.write(f"\n--- 新会话开始: {datetime.now()} ---\n")
    log_file.flush()

    print(f"日志进程已启动，日志将写入 {args.log_file}")

    try:
        while True:
            message = log_queue.get()
            if message == "EXIT":
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"

            # 写入日志文件
            log_file.write(log_entry)
            log_file.flush()

            # 输出到控制台
            print(log_entry, end="")

            log_queue.task_done()
    except KeyboardInterrupt:
        pass
    finally:
        log_file.close()
        print("日志进程已关闭")
