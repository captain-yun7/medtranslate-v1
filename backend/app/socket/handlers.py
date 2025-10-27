import socketio
from app.services.translation import translation_service
from app.services.session import session_manager
import logging

logger = logging.getLogger(__name__)


def register_socket_handlers(sio: socketio.AsyncServer):

    @sio.on('connect')
    async def connect(sid, environ):
        logger.info(f"Client connected: {sid}")
        await sio.emit('connected', {'sid': sid}, room=sid)

    @sio.on('disconnect')
    async def disconnect(sid):
        logger.info(f"Client disconnected: {sid}")
        # 세션 정리
        await session_manager.remove_connection(sid)

    @sio.on('join_room')
    async def join_room(sid, data):
        """
        채팅방 입장
        data = {
            'room_id': 'room_123',
            'user_type': 'customer' | 'agent',
            'customer_language': 'vi',  # 고객인 경우
            'agent_id': 'agent_001'     # 상담사인 경우
        }
        """
        room_id = data['room_id']
        user_type = data['user_type']

        # Socket.io 룸 입장
        await sio.enter_room(sid, room_id)

        # 세션에 연결 정보 저장
        await session_manager.add_connection(
            room_id=room_id,
            sid=sid,
            user_type=user_type,
            language=data.get('language') or data.get('customer_language'),
            agent_id=data.get('agent_id')
        )

        logger.info(f"{user_type} joined room {room_id}: {sid}")

        # 입장 확인
        await sio.emit('joined_room', {
            'room_id': room_id,
            'user_type': user_type
        }, room=sid)

        # 상대방이 이미 있으면 알림
        session = await session_manager.get_session(room_id)
        if user_type == 'agent' and session.get('customer_sid'):
            await sio.emit('customer_online', {
                'language': session['customer_language']
            }, room=sid)
        elif user_type == 'customer' and session.get('agent_sid'):
            await sio.emit('agent_online', {}, room=sid)

    @sio.on('customer_message')
    async def handle_customer_message(sid, data):
        """
        고객 메시지 처리
        data = {
            'room_id': 'room_123',
            'message': 'Xin chào',
            'timestamp': '2025-10-24T...'
        }
        """
        room_id = data['room_id']
        message = data['message']

        # 세션 정보 가져오기
        session = await session_manager.get_session(room_id)
        if not session:
            await sio.emit('error', {
                'message': 'Session not found'
            }, room=sid)
            return

        source_lang = session['customer_language']

        try:
            # 1. 한국어로 번역
            translated = await translation_service.translate(
                text=message,
                source_lang=source_lang,
                target_lang='ko',
                context='medical'
            )

            # 2. DB에 저장 (TODO: 구현 필요)
            # await save_message(...)

            # 3. 상담사에게 전송 (원문 + 번역)
            agent_sid = session.get('agent_sid')
            if agent_sid:
                await sio.emit('agent_receive_message', {
                    'message_id': f"msg_{data['timestamp']}",
                    'original': message,
                    'translated': translated,
                    'source_lang': source_lang,
                    'timestamp': data['timestamp']
                }, room=agent_sid)

            # 4. 고객에게 발신 확인
            await sio.emit('message_sent', {
                'message_id': f"msg_{data['timestamp']}",
                'message': message,
                'timestamp': data['timestamp']
            }, room=sid)

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            await sio.emit('error', {
                'message': 'Translation failed',
                'detail': str(e)
            }, room=sid)

    @sio.on('agent_message')
    async def handle_agent_message(sid, data):
        """
        상담사 메시지 처리
        data = {
            'room_id': 'room_123',
            'message': '안녕하세요, 무엇을 도와드릴까요?',
            'timestamp': '2025-10-24T...'
        }
        """
        room_id = data['room_id']
        message = data['message']

        # 세션 정보
        session = await session_manager.get_session(room_id)
        if not session:
            return

        target_lang = session['customer_language']

        try:
            # 1. 고객 언어로 번역
            translated = await translation_service.translate(
                text=message,
                source_lang='ko',
                target_lang=target_lang,
                context='medical'
            )

            # 2. DB 저장 (TODO: 구현 필요)
            # await save_message(...)

            # 3. 고객에게 전송 (번역된 메시지만)
            customer_sid = session.get('customer_sid')
            if customer_sid:
                await sio.emit('customer_receive_message', {
                    'message_id': f"msg_{data['timestamp']}",
                    'message': translated,
                    'timestamp': data['timestamp']
                }, room=customer_sid)

            # 4. 상담사에게 발신 확인 (원문 + 번역 미리보기)
            await sio.emit('message_sent', {
                'message_id': f"msg_{data['timestamp']}",
                'original': message,
                'translated': translated,
                'target_lang': target_lang,
                'timestamp': data['timestamp']
            }, room=sid)

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            await sio.emit('error', {
                'message': 'Translation failed'
            }, room=sid)

    @sio.on('send_message')
    async def handle_send_message(sid, data):
        """
        통합 메시지 전송 핸들러
        data = {
            'room_id': 'room_123',
            'text': 'message text',
            'language': 'en' or 'ko'
        }
        """
        room_id = data['room_id']
        text = data['text']
        source_lang = data.get('language', 'ko')

        # 세션 정보 가져오기
        session = await session_manager.get_session(room_id)
        if not session:
            await sio.emit('error', {'message': 'Session not found'}, room=sid)
            return

        # 발신자 유형 확인
        sender_type = 'agent' if sid == session.get('agent_sid') else 'customer'

        try:
            # 번역 처리
            if sender_type == 'customer':
                # 고객 메시지 -> 한국어로 번역
                target_lang = 'ko'
                translated = await translation_service.translate(
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    context='medical'
                )

                # 상담사에게 전송
                agent_sid = session.get('agent_sid')
                if agent_sid:
                    await sio.emit('new_message', {
                        'sender_type': 'customer',
                        'text': text,
                        'translated_text': translated,
                        'source_lang': source_lang,
                        'target_lang': target_lang
                    }, room=agent_sid)

                # 고객에게도 전송 (에코)
                await sio.emit('new_message', {
                    'sender_type': 'customer',
                    'text': text,
                    'translated_text': translated,
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }, room=sid)

            else:
                # 상담사 메시지 -> 고객 언어로 번역
                target_lang = session.get('customer_language', 'en')
                translated = await translation_service.translate(
                    text=text,
                    source_lang='ko',
                    target_lang=target_lang,
                    context='medical'
                )

                # 고객에게 전송
                customer_sid = session.get('customer_sid')
                if customer_sid:
                    await sio.emit('new_message', {
                        'sender_type': 'agent',
                        'text': translated,
                        'translated_text': text,
                        'source_lang': 'ko',
                        'target_lang': target_lang
                    }, room=customer_sid)

                # 상담사에게도 전송 (에코)
                await sio.emit('new_message', {
                    'sender_type': 'agent',
                    'text': text,
                    'translated_text': translated,
                    'source_lang': 'ko',
                    'target_lang': target_lang
                }, room=sid)

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            await sio.emit('error', {
                'message': 'Translation failed',
                'detail': str(e)
            }, room=sid)

    @sio.on('typing')
    async def handle_typing(sid, data):
        """타이핑 표시"""
        room_id = data['room_id']

        session = await session_manager.get_session(room_id)
        if not session:
            return

        # 세션에서 발신자 타입 확인
        user_type = 'agent' if sid == session.get('agent_sid') else 'customer'

        # 상대방에게만 전송
        if user_type == 'customer':
            agent_sid = session.get('agent_sid')
            if agent_sid:
                await sio.emit('typing', {}, room=agent_sid)
        else:
            customer_sid = session.get('customer_sid')
            if customer_sid:
                await sio.emit('typing', {}, room=customer_sid)

    @sio.on('stop_typing')
    async def handle_stop_typing(sid, data):
        """타이핑 중지"""
        room_id = data['room_id']

        session = await session_manager.get_session(room_id)
        if not session:
            return

        # 세션에서 발신자 타입 확인
        user_type = 'agent' if sid == session.get('agent_sid') else 'customer'

        if user_type == 'customer':
            agent_sid = session.get('agent_sid')
            if agent_sid:
                await sio.emit('stop_typing', {}, room=agent_sid)
        else:
            customer_sid = session.get('customer_sid')
            if customer_sid:
                await sio.emit('stop_typing', {}, room=customer_sid)

    @sio.on('end_chat')
    async def handle_end_chat(sid, data):
        """채팅 종료"""
        room_id = data['room_id']

        # 세션 종료 처리
        await session_manager.end_session(room_id)

        # 룸의 모든 참가자에게 알림
        await sio.emit('chat_ended', {
            'room_id': room_id,
            'ended_by': data.get('ended_by', 'user')
        }, room=room_id)

        # 룸 정리
        await sio.leave_room(sid, room_id)
