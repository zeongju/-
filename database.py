import sqlite3
import os
from datetime import datetime, timedelta
from config import Config

class VideoDatabase:
    def __init__(self):
        self.db_file = Config.DATABASE_FILE
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 영상 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                thumbnail_url TEXT,
                published_at TEXT NOT NULL,
                duration TEXT,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_video(self, video_data):
        """영상 추가"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO videos 
                (video_id, title, description, thumbnail_url, published_at, duration, view_count, like_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data['video_id'],
                video_data['title'],
                video_data.get('description', ''),
                video_data.get('thumbnail_url', ''),
                video_data['published_at'],
                video_data.get('duration', ''),
                video_data.get('view_count', 0),
                video_data.get('like_count', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"영상 추가 오류: {e}")
            return False
    
    def get_all_videos(self, limit=50):
        """모든 영상 조회"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM videos 
            ORDER BY published_at DESC 
            LIMIT ?
        ''', (limit,))
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row[0],
                'video_id': row[1],
                'title': row[2],
                'description': row[3],
                'thumbnail_url': row[4],
                'published_at': row[5],
                'duration': row[6],
                'view_count': row[7],
                'like_count': row[8],
                'created_at': row[9]
            })
        
        conn.close()
        return videos
    
    def get_recent_videos(self, days=7):
        """최근 N일간의 영상 조회"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # N일 전 날짜 계산
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT * FROM videos 
            WHERE published_at >= ?
            ORDER BY published_at DESC
        ''', (cutoff_date,))
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row[0],
                'video_id': row[1],
                'title': row[2],
                'description': row[3],
                'thumbnail_url': row[4],
                'published_at': row[5],
                'duration': row[6],
                'view_count': row[7],
                'like_count': row[8],
                'created_at': row[9]
            })
        
        conn.close()
        return videos
    
    def video_exists(self, video_id):
        """영상이 이미 존재하는지 확인"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM videos WHERE video_id = ?', (video_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    def get_video_by_id(self, video_id):
        """특정 영상 조회"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM videos WHERE video_id = ?', (video_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'video_id': row[1],
                'title': row[2],
                'description': row[3],
                'thumbnail_url': row[4],
                'published_at': row[5],
                'duration': row[6],
                'view_count': row[7],
                'like_count': row[8],
                'created_at': row[9]
            }
        return None 