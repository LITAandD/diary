# gunicorn_config.py
import os

# Render가 전달하는 PORT 환경변수 사용, 없으면 로컬용으로 10000
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
