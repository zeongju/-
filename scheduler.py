import schedule
import time
import threading
from datetime import datetime
from youtube_monitor import YouTubeMonitor
from config import Config

class VideoScheduler:
    def __init__(self):
        self.monitor = YouTubeMonitor()
        self.schedule_time = Config.SCHEDULE_TIME
        
    def check_new_videos_job(self):
        """매주 일요일 실행되는 작업"""
        print(f"=== 매주 일요일 새 영상 확인 시작 ({datetime.now()}) ===")
        
        try:
            # 최근 일주일간의 새 영상 확인
            new_count = self.monitor.check_recent_videos()
            
            if new_count > 0:
                print(f"✅ {new_count}개의 새 영상이 추가되었습니다.")
            else:
                print("ℹ️ 새로 추가된 영상이 없습니다. 기존 데이터를 유지합니다.")
                
        except Exception as e:
            print(f"❌ 새 영상 확인 중 오류 발생: {e}")
        
        print("=== 새 영상 확인 완료 ===\n")
    
    def manual_check(self):
        """수동 새 영상 확인"""
        print("수동 새 영상 확인 시작...")
        return self.monitor.check_recent_videos()
    
    def setup_schedule(self):
        """스케줄 설정"""
        # 매주 일요일 오전 9시에 실행
        schedule.every().sunday.at(self.schedule_time).do(self.check_new_videos_job)
        print(f"📅 스케줄 설정 완료: 매주 일요일 {self.schedule_time}")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        self.setup_schedule()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    
    def run_in_background(self):
        """백그라운드에서 스케줄러 실행"""
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        return scheduler_thread
    
    def next_run(self):
        """다음 실행 시간 반환"""
        try:
            return schedule.next_run()
        except:
            return "알 수 없음" 