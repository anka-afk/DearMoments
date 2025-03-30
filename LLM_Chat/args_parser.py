# 命令行参数
import argparse


parser = argparse.ArgumentParser(description="Chat with LLM")
parser.add_argument("--api_key", type=str, help="API key for LLM")
parser.add_argument("--model", type=str, default="gemini-2.0-flash", help="Model name")
parser.add_argument(
    "--api_url",
    type=str,
    default="https://gemini-proxy.808711.xyz/",
    help="API URL",
)
parser.add_argument("--log_file", type=str, default="chat.log", help="Log file name")
parser.add_argument("--timeout", type=int, default=120, help="API timeout in seconds")
parser.add_argument("--image", type=str, help="Path to image file to include in chat")
args = parser.parse_args()
