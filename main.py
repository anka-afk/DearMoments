import os
import sys
import argparse


def show_help():
    """显示帮助信息"""
    print("DearMoments - 一个结合大语言模型的高性能AI记忆模块")
    print("\n可用命令:")
    print("  chat        启动聊天窗口")
    print("  --help      显示帮助信息")
    print("\n示例:")
    print("  python main.py chat --api_key YOUR_API_KEY --model gemini-1.5-flash")


def main():
    """主入口函数"""
    if len(sys.argv) < 2 or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        show_help()
        return

    command = sys.argv[1]

    if command == "chat":
        # 移除第一个参数(命令)
        sys.argv.pop(1)
        # 导入并运行聊天窗口
        try:
            from LLM_Chat.chat_window import main as chat_main

            chat_main()
        except ImportError as e:
            print(f"加载聊天模块失败: {str(e)}")
    else:
        print(f"未知命令: {command}")
        show_help()


if __name__ == "__main__":
    main()
