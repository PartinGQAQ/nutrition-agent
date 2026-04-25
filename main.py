"""兼容 ``uvicorn main:app``；实际应用在 ``api.main``。"""

from api.main import app

__all__ = ["app"]


def main() -> None:
    print("Hello from nutrition-agent! 启动 API: uvicorn main:app --reload --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()
