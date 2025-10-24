from typing import Dict, Optional
from datetime import datetime


class SessionManager:
    def __init__(self):
        # 활성 세션 저장
        # room_id -> session_data
        self.sessions: Dict[str, dict] = {}
        # sid -> room_id 매핑
        self.sid_to_room: Dict[str, str] = {}

    async def add_connection(
        self,
        room_id: str,
        sid: str,
        user_type: str,
        language: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        """연결 추가"""
        if room_id not in self.sessions:
            self.sessions[room_id] = {
                'customer_sid': None,
                'agent_sid': None,
                'customer_language': None,
                'agent_id': None,
                'created_at': datetime.now().isoformat(),
                'status': 'waiting'
            }

        session = self.sessions[room_id]

        if user_type == 'customer':
            session['customer_sid'] = sid
            session['customer_language'] = language
        else:  # agent
            session['agent_sid'] = sid
            session['agent_id'] = agent_id
            session['status'] = 'active'

        self.sid_to_room[sid] = room_id

    async def remove_connection(self, sid: str):
        """연결 제거"""
        if sid in self.sid_to_room:
            room_id = self.sid_to_room[sid]
            if room_id in self.sessions:
                session = self.sessions[room_id]
                if session['customer_sid'] == sid:
                    session['customer_sid'] = None
                elif session['agent_sid'] == sid:
                    session['agent_sid'] = None
                    session['status'] = 'waiting'

            del self.sid_to_room[sid]

    async def get_session(self, room_id: str) -> Optional[dict]:
        """세션 정보 가져오기"""
        return self.sessions.get(room_id)

    async def end_session(self, room_id: str):
        """세션 종료"""
        if room_id in self.sessions:
            session = self.sessions[room_id]
            # sid_to_room 정리
            if session['customer_sid']:
                self.sid_to_room.pop(session['customer_sid'], None)
            if session['agent_sid']:
                self.sid_to_room.pop(session['agent_sid'], None)

            # 세션 삭제
            del self.sessions[room_id]

    async def get_waiting_rooms(self) -> list:
        """대기 중인 채팅방 목록"""
        waiting = []
        for room_id, session in self.sessions.items():
            if session['status'] == 'waiting' and session['customer_sid']:
                waiting.append({
                    'room_id': room_id,
                    'customer_language': session['customer_language'],
                    'created_at': session['created_at']
                })
        return waiting


# 싱글톤 인스턴스
session_manager = SessionManager()
