import requests
import json
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

# .env 파일 로드
load_dotenv(find_dotenv())

class JasoseolScraper:
    def __init__(self):
        self.base_url = "https://jasoseol.com"
        self.session = requests.Session()
        
        # .env에서 쿠키 가져오기
        self.cookies_str = os.getenv("JASOSEOL_COOKIE")
        if not self.cookies_str:
            raise ValueError(".env 파일에 'JASOSEOL_COOKIE'가 설정되어 있지 않습니다.")
        
        # 공통 헤더 설정
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://jasoseol.com",
            "referer": "https://jasoseol.com/recruit",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "cookie": self.cookies_str
        }
        self.session.headers.update(self.headers)

    def get_calendar_list(self, start_time, end_time):
        """특정 기간의 공고 리스트와 employment_id를 가져옴"""
        url = f"{self.base_url}/employment/calendar_list.json"
        payload = {
            "start_time": start_time,
            "end_time": end_time
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                employment = data.get('employment')
                if isinstance(employment, list):
                    return employment
                else:
                    print(f"Warning: 'employment' is not a list. Got: {employment}")
                    return []
            else:
                print(f"Failed to fetch calendar list: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error occurred while fetching calendar list: {e}")
            return []

    def get_questions(self, employment_id):
        """특정 employment_id에 대한 질문 상세 정보를 가져옴"""
        url = f"{self.base_url}/employment/employment_question.json"
        payload = {"employment_id": employment_id}
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                questions = data.get('employment_question')
                if isinstance(questions, list):
                    return questions
                else:
                    print(f"Warning: 'employment_question' is not a list for ID {employment_id}. Got: {questions}")
                    return []
            else:
                print(f"Failed to fetch questions for ID {employment_id}: {response.status_code}")
                # 세션 만료 여부 확인을 위해 응답 내용 일부 출력
                if response.status_code == 401 or response.status_code == 403:
                    print("세션이 만료되었거나 권한이 없는 것 같습니다. 쿠키를 확인해주세요.")
                return []
        except Exception as e:
            print(f"Error occurred while fetching questions for ID {employment_id}: {e}")
            return []

    def run(self):
        # 날짜 범위 설정: 오늘 00시 ~ 일주일 후 00시
        now = datetime.utcnow()
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(days=7)
        
        # API 형식에 맞게 문자열 변환 (Z 포맷)
        start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        print(f"[{datetime.now()}] 스크래핑을 시작합니다... ({start_str} ~ {end_str})")
        recruitments = self.get_calendar_list(start_str, end_str)
        print(f"총 {len(recruitments)}개의 공고를 발견했습니다.")
        
        all_data = []
        output_file = "jasoseol_questions.json"
        
        try:
            for idx, recruit in enumerate(recruitments):
                company_name = recruit.get('name')
                recruit_title = recruit.get('title')
                recruit_id = recruit.get('id')
                
                employments = recruit.get('employments', [])
                
                for emp in employments:
                    emp_id = emp.get('id')
                    print(f"[{idx+1}/{len(recruitments)}] {company_name} - {recruit_title} (ID: {emp_id}) 추출 중...")
                    
                    try:
                        questions = self.get_questions(emp_id)
                        
                        processed_questions = []
                        if isinstance(questions, list):
                            for q in questions:
                                total_count = q.get('total_count')
                                # 글자 수 제한이 없거나 0인 경우 처리
                                max_length = total_count if total_count and total_count > 0 else "글자수 제한 없음"
                                
                                processed_questions.append({
                                    "question": q.get('question'),
                                    "max_length": max_length
                                })
                        
                        item = {
                            "recruit_id": recruit_id,
                            "employment_id": emp_id,
                            "company_name": company_name,
                            "title": recruit_title,
                            "end_time": recruit.get('end_time'),
                            "questions": processed_questions
                        }
                        all_data.append(item)
                        
                        # 질문 출력 추가 (글자 수 제한 포함)
                        if processed_questions:
                            for i, q_item in enumerate(processed_questions, 1):
                                q_text = q_item["question"] or ""
                                q_max = q_item["max_length"]
                                # q_max가 숫자면 '자'를 붙이고, 문자열이면 그대로 출력
                                limit_str = f"{q_max}자" if isinstance(q_max, int) else q_max
                                print(f"  Q{i} (최대 {limit_str}): {q_text[:100]}{'...' if len(q_text) > 100 else ''}")
                        else:
                            print("  (질문 정보 없음)")
                        
                        # 중간 저장 (혹시 모를 중단에 대비)
                        with open(output_file, "w", encoding='utf-8') as f:
                            json.dump(all_data, f, ensure_ascii=False, indent=4)
                            
                    except Exception as e:
                        print(f"Error processing employment {emp_id}: {e}")
                        continue
                        
                    # 요청 간 지연 시간 (5초 이상으로 설정)
                    print(f"서버 부하 방지를 위해 5초 대기 중...")
                    time.sleep(5)
        except KeyboardInterrupt:
            print("\n사용자에 의해 스크래핑이 중단되었습니다. 현재까지 데이터를 저장합니다.")
        except Exception as e:
            print(f"\n치명적인 에러 발생: {e}. 현재까지 데이터를 저장합니다.")
        finally:
            # 최종 저장
            if all_data:
                with open(output_file, "w", encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=4)
                print(f"\n최종 완료! 총 {len(all_data)} 건의 데이터를 {output_file}에 안전하게 저장했습니다.")
            else:
                print("\n저장할 데이터가 없습니다.")

if __name__ == "__main__":
    scraper = JasoseolScraper()
    scraper.run()
