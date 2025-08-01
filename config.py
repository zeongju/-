import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # YouTube 채널 설정
    YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@%EC%98%88%EC%82%B0%ED%99%94%ED%83%80"
    
    # 데이터베이스 설정
    DATABASE_FILE = 'videos.db'
    
    # 스케줄러 설정
    SCHEDULE_TIME = "09:00"  # 매주 일요일 오전 9시
    
    # 웹 서버 설정
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
    FLASK_DEBUG = True
    
    # 홈페이지 설정
    HOMEPAGE_TITLE = "예산화타 영상 모음"
    HOMEPAGE_DESCRIPTION = "매주 업데이트되는 예산화타 채널의 최신 영상들 (최근 일주일)" 