import requests
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
from config import Config
from database import VideoDatabase

class YouTubeMonitor:
    def __init__(self):
        # 예산화타 채널로 고정
        self.channel_url = "https://www.youtube.com/@%EC%98%88%EC%82%B0%ED%99%94%ED%83%80"
        self.db = VideoDatabase()
        
    def extract_channel_handle_from_url(self, url):
        """YouTube URL에서 채널 핸들 추출"""
        try:
            if '@' in url:
                channel_handle = url.split('@')[1]
                return channel_handle
            return None
        except Exception as e:
            print(f"채널 핸들 추출 오류: {e}")
            return None
    
    def get_channel_videos(self, max_results=20):
        """채널의 최근 영상들 가져오기 (웹 스크래핑)"""
        channel_handle = self.extract_channel_handle_from_url(self.channel_url)
        if not channel_handle:
            print("채널 핸들을 찾을 수 없습니다.")
            return []
        
        try:
            channel_url = f"https://www.youtube.com/@{channel_handle}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(channel_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = self.extract_videos_from_page(soup, max_results)
            return videos
        except Exception as e:
            print(f"채널 정보 조회 오류: {e}")
            return []
    
    def extract_videos_from_page(self, soup, max_results):
        """페이지에서 영상 정보 추출"""
        videos = []
        
        try:
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    data_match = re.search(r'var ytInitialData = ({.*?});', script.string)
                    if data_match:
                        try:
                            data = json.loads(data_match.group(1))
                            videos = self.parse_youtube_data(data, max_results)
                            break
                        except json.JSONDecodeError:
                            continue
            
            if not videos:
                print("YouTube 페이지에서 영상 정보를 추출할 수 없습니다.")
                
        except Exception as e:
            print(f"영상 정보 추출 오류: {e}")
        
        return videos
    
    def parse_youtube_data(self, data, max_results):
        """YouTube 데이터에서 영상 정보 파싱"""
        videos = []
        
        try:
            tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
            
            for tab in tabs:
                if tab.get('tabRenderer', {}).get('selected', False):
                    tab_content = tab.get('tabRenderer', {}).get('content', {})
                    video_list = self.find_video_list(tab_content)
                    
                    if video_list:
                        for item in video_list[:max_results]:
                            video_info = self.extract_video_info(item)
                            if video_info:
                                videos.append(video_info)
                        break
                        
        except Exception as e:
            print(f"YouTube 데이터 파싱 오류: {e}")
        
        return videos
    
    def find_video_list(self, content):
        """영상 목록 찾기"""
        try:
            paths = [
                ['sectionListRenderer', 'contents', 0, 'itemSectionRenderer', 'contents', 0, 'gridRenderer', 'items'],
                ['sectionListRenderer', 'contents', 0, 'itemSectionRenderer', 'contents', 0, 'shelfRenderer', 'content', 'expandedShelfContentsRenderer', 'items'],
                ['richGridRenderer', 'contents']
            ]
            
            for path in paths:
                current = content
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    elif isinstance(current, list) and isinstance(key, int) and key < len(current):
                        current = current[key]
                    else:
                        break
                else:
                    if isinstance(current, list):
                        return current
            
        except Exception as e:
            print(f"영상 목록 찾기 오류: {e}")
        
        return []
    
    def extract_video_info(self, item):
        """영상 정보 추출"""
        try:
            renderers = ['gridVideoRenderer', 'videoRenderer', 'richItemRenderer']
            
            for renderer in renderers:
                if renderer in item:
                    video_data = item[renderer]
                    video_id = video_data.get('videoId', '')
                    if not video_id:
                        continue
                    
                    title = ''
                    title_runs = video_data.get('title', {}).get('runs', [])
                    if title_runs:
                        title = ''.join([run.get('text', '') for run in title_runs])
                    
                    thumbnails = video_data.get('thumbnail', {}).get('thumbnails', [])
                    thumbnail_url = ''
                    if thumbnails:
                        thumbnail_url = thumbnails[-1].get('url', '')
                    
                    published_time = video_data.get('publishedTimeText', {}).get('simpleText', '')
                    view_count_text = video_data.get('viewCountText', {}).get('simpleText', '0')
                    view_count = self.parse_view_count(view_count_text)
                    length_text = video_data.get('lengthText', {}).get('simpleText', '')
                    duration = self.parse_duration(length_text)
                    
                    return {
                        'video_id': video_id,
                        'title': title,
                        'description': '',
                        'thumbnail_url': thumbnail_url,
                        'published_at': self.convert_time_to_iso(published_time),
                        'duration': duration,
                        'view_count': view_count,
                        'like_count': 0
                    }
            
        except Exception as e:
            print(f"영상 정보 추출 오류: {e}")
        
        return None
    
    def parse_view_count(self, view_count_text):
        """조회수 파싱"""
        try:
            if '만' in view_count_text:
                number = float(view_count_text.replace('조회수 ', '').replace('만회', ''))
                return int(number * 10000)
            elif '천' in view_count_text:
                number = float(view_count_text.replace('조회수 ', '').replace('천회', ''))
                return int(number * 1000)
            else:
                numbers = re.findall(r'\d+', view_count_text)
                if numbers:
                    return int(''.join(numbers))
        except:
            pass
        return 0
    
    def parse_duration(self, duration_text):
        """영상 길이 파싱"""
        try:
            if ':' in duration_text:
                parts = duration_text.split(':')
                if len(parts) == 2:
                    minutes, seconds = int(parts[0]), int(parts[1])
                    return f"PT{minutes}M{seconds}S"
                elif len(parts) == 3:
                    hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"PT{hours}H{minutes}M{seconds}S"
        except:
            pass
        return duration_text
    
    def convert_time_to_iso(self, time_text):
        """시간 텍스트를 ISO 형식으로 변환"""
        try:
            now = datetime.now()
            
            if '시간' in time_text:
                hours = int(re.findall(r'\d+', time_text)[0])
                return (now - timedelta(hours=hours)).isoformat()
            elif '일' in time_text:
                days = int(re.findall(r'\d+', time_text)[0])
                return (now - timedelta(days=days)).isoformat()
            elif '주' in time_text:
                weeks = int(re.findall(r'\d+', time_text)[0])
                return (now - timedelta(weeks=weeks)).isoformat()
            elif '개월' in time_text:
                months = int(re.findall(r'\d+', time_text)[0])
                return (now - timedelta(days=months*30)).isoformat()
            else:
                return now.isoformat()
        except:
            return datetime.now().isoformat()
    
    def check_recent_videos(self):
        """최근 일주일간의 새 영상 확인 및 데이터베이스에 추가"""
        print("최근 일주일간의 새 영상 확인 중...")
        
        videos = self.get_channel_videos(max_results=20)
        
        if not videos:
            print("새 영상이 없거나 스크래핑에 실패했습니다. 기존 데이터를 유지합니다.")
            return 0
        
        # 최근 일주일 기준 날짜 계산
        one_week_ago = datetime.now() - timedelta(days=7)
        
        new_videos_count = 0
        
        for video in videos:
            # 영상이 최근 일주일 내에 업로드되었는지 확인
            try:
                video_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                if video_date >= one_week_ago:
                    if not self.db.video_exists(video['video_id']):
                        if self.db.add_video(video):
                            new_videos_count += 1
                            print(f"새 영상 추가: {video['title']}")
            except Exception as e:
                print(f"영상 날짜 파싱 오류: {e}")
                continue
        
        if new_videos_count == 0:
            print("최근 일주일간 새로 추가된 영상이 없습니다.")
        else:
            print(f"총 {new_videos_count}개의 새 영상이 추가되었습니다.")
        
        return new_videos_count
    
    def get_recent_videos_from_db(self, days=7):
        """데이터베이스에서 최근 영상 조회"""
        return self.db.get_recent_videos(days)
    
    def get_all_videos_from_db(self, limit=50):
        """데이터베이스에서 모든 영상 조회"""
        return self.db.get_all_videos(limit) 