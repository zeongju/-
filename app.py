from flask import Flask, render_template, jsonify, request
from datetime import datetime
from youtube_monitor import YouTubeMonitor
from scheduler import VideoScheduler
from config import Config
import threading

app = Flask(__name__)
monitor = YouTubeMonitor()
scheduler = VideoScheduler()

# 백그라운드에서 스케줄러 시작
scheduler_thread = scheduler.run_in_background()

@app.route('/')
def home():
    """홈페이지 - 최근 7일간의 영상만 표시"""
    videos = monitor.get_recent_videos_from_db(days=7)
    return render_template('home.html', 
                         videos=videos, 
                         title=Config.HOMEPAGE_TITLE,
                         description=Config.HOMEPAGE_DESCRIPTION)

@app.route('/api/videos')
def api_videos():
    """영상 목록 API - 최근 7일간의 영상만 반환"""
    days = request.args.get('days', 7, type=int)
    videos = monitor.get_recent_videos_from_db(days=days)
    return jsonify(videos)

@app.route('/api/recent')
def api_recent():
    """최근 영상 API"""
    days = request.args.get('days', 7, type=int)
    videos = monitor.get_recent_videos_from_db(days=days)
    return jsonify(videos)

@app.route('/api/check-new')
def api_check_new():
    """수동 새 영상 확인 API"""
    try:
        new_count = scheduler.manual_check()
        return jsonify({
            'success': True,
            'new_videos_count': new_count,
            'message': f'{new_count}개의 새 영상이 추가되었습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """시스템 상태 API - 최근 7일간의 영상만 집계"""
    try:
        recent_videos = len(monitor.get_recent_videos_from_db(days=7))
        
        return jsonify({
            'status': 'running',
            'recent_videos': recent_videos,
            'next_schedule': str(scheduler.next_run())
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.template_filter('format_date')
def format_date(date_string):
    """날짜 포맷팅"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y년 %m월 %d일 %H:%M')
    except:
        return date_string

@app.template_filter('format_duration')
def format_duration(duration):
    """영상 길이 포맷팅"""
    if not duration:
        return "알 수 없음"
    
    # ISO 8601 duration 형식 파싱 (PT4M13S -> 4분 13초)
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        elif minutes > 0:
            return f"{minutes}분 {seconds}초"
        else:
            return f"{seconds}초"
    
    return duration

@app.template_filter('format_number')
def format_number(number):
    """숫자 포맷팅 (조회수, 좋아요 수)"""
    if not number:
        return "0"
    
    if number >= 10000:
        return f"{number // 10000}만"
    elif number >= 1000:
        return f"{number // 1000}천"
    else:
        return str(number)

if __name__ == '__main__':
    # 데이터베이스 초기화
    monitor.db.init_database()
    
    # Flask 앱 실행
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    ) 