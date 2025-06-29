import os
import json
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import gc

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['DEBUG'] = False

# Configuração CORS para permitir conexões do cliente
CORS(app, origins=["*"], supports_credentials=True)

# Configuração do SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Armazenamento temporário em memória (sem persistência)
active_sessions = {}  # {session_id: {user_id, room, timestamp}}
active_rooms = {}     # {room_id: {users: set(), created_at}}

# Configuração de segurança
SESSION_TIMEOUT = 3600  # 1 hora
ROOM_TIMEOUT = 7200     # 2 horas
MAX_MESSAGE_LENGTH = 1000

def zeroize(var):
    if isinstance(var, bytearray):
        for i in range(len(var)):
            var[i] = 0
    elif isinstance(var, bytes):
        # bytes são imutáveis, mas podemos sobrescrever referências
        pass
    elif isinstance(var, str):
        pass
    elif isinstance(var, dict):
        for k in var:
            zeroize(var[k])
    elif isinstance(var, list):
        for v in var:
            zeroize(v)
    # Forçar coleta de lixo
    gc.collect()

def cleanup_expired_sessions():
    """Remove sessões expiradas"""
    current_time = datetime.now()
    expired_sessions = []
    
    for session_id, session_data in active_sessions.items():
        if current_time - session_data['timestamp'] > timedelta(seconds=SESSION_TIMEOUT):
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del active_sessions[session_id]

def cleanup_expired_rooms():
    """Remove salas expiradas"""
    current_time = datetime.now()
    expired_rooms = []
    
    for room_id, room_data in active_rooms.items():
        if current_time - room_data['created_at'] > timedelta(seconds=ROOM_TIMEOUT):
            expired_rooms.append(room_id)
    
    for room_id in expired_rooms:
        del active_rooms[room_id]

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde para o Render.com"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/join-room', methods=['POST'])
def join_room_api():
    """Permite que um usuário entre em qualquer sala (cria se não existir)"""
    try:
        data = request.get_json()
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if not room_id or not user_id:
            return jsonify({'error': 'room_id e user_id são obrigatórios'}), 400
        
        # Limpa sessões e salas expiradas
        cleanup_expired_sessions()
        cleanup_expired_rooms()
        
        # Se a sala não existe, cria automaticamente
        if room_id not in active_rooms:
            active_rooms[room_id] = {
                'users': set(),
                'created_at': datetime.now()
            }
        
        # Adiciona usuário à sala
        active_rooms[room_id]['users'].add(user_id)
        
        return jsonify({
            'room_id': room_id,
            'status': 'joined',
            'users_count': len(active_rooms[room_id]['users'])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Manipula conexão de um cliente"""
    session_id = request.sid  # type: ignore
    print(f"Cliente conectado: {session_id}")
    
    # Limpa sessões expiradas
    cleanup_expired_sessions()
    
    emit('connected', {'session_id': session_id})

@socketio.on('join_room')
def handle_join_room(data):
    """Manipula entrada em uma sala (cria se não existir)"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if not room_id or not user_id:
            emit('error', {'message': 'room_id e user_id são obrigatórios'})
            return
        
        # Se a sala não existe, cria automaticamente
        if room_id not in active_rooms:
            active_rooms[room_id] = {
                'users': set(),
                'created_at': datetime.now()
            }
        
        # Adiciona à sessão ativa
        active_sessions[request.sid] = {
            'user_id': user_id,
            'room': room_id,
            'timestamp': datetime.now()
        }  # type: ignore
        
        # Entra na sala do SocketIO
        join_room(room_id)
        
        # Só adiciona usuário se ainda não estiver
        if user_id not in active_rooms[room_id]['users']:
            active_rooms[room_id]['users'].add(user_id)
            emit('room_joined', {
                'room_id': room_id,
                'user_id': user_id,
                'users_count': len(active_rooms[room_id]['users'])
            })
            # Notifica outros usuários
            emit('user_joined', {
                'user_id': user_id,
                'users_count': len(active_rooms[room_id]['users'])
            }, to=room_id, include_self=False)
            print(f"Usuário {user_id} entrou na sala {room_id}")
        else:
            # Se já está na sala, só confirma
            emit('room_joined', {
                'room_id': room_id,
                'user_id': user_id,
                'users_count': len(active_rooms[room_id]['users'])
            })
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('send_message')
def handle_send_message(data):
    """Manipula envio de mensagem criptografada"""
    try:
        room_id = data.get('room_id')
        encrypted_message = data.get('message')
        user_id = data.get('user_id')
        msg_hmac = data.get('hmac')
        
        if not room_id or not encrypted_message or not user_id:
            emit('error', {'message': 'Dados incompletos'})
            return
        
        # Se a sala não existe, cria automaticamente
        if room_id not in active_rooms:
            active_rooms[room_id] = {
                'users': set(),
                'created_at': datetime.now()
            }
        
        # Adiciona usuário à sala se não estiver
        if user_id not in active_rooms[room_id]['users']:
            active_rooms[room_id]['users'].add(user_id)
        
        # Verifica tamanho da mensagem
        if len(encrypted_message) > MAX_MESSAGE_LENGTH:
            emit('error', {'message': 'Mensagem muito longa'})
            return

        # Repasse imediato da mensagem criptografada
        emit('new_message', {
            'room_id': room_id,
            'user_id': user_id,
            'message': encrypted_message,
            'hmac': msg_hmac,
            'timestamp': datetime.now().isoformat()
        }, to=room_id)
        
        # Não armazene mensagem, apague variáveis sensíveis
        encrypted_message = None
        msg_hmac = None
        gc.collect()
    
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Manipula saída de uma sala"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if room_id and user_id:
            if room_id in active_rooms and user_id in active_rooms[room_id]['users']:
                active_rooms[room_id]['users'].remove(user_id)
                # Se não há mais usuários, remove a sala
                if len(active_rooms[room_id]['users']) == 0:
                    del active_rooms[room_id]
                else:
                    # Notifica outros usuários
                    emit('user_left', {
                        'user_id': user_id,
                        'users_count': len(active_rooms[room_id]['users'])
                    }, to=room_id, include_self=False)
        # Remove da sessão ativa (garantido)
        if request.sid in active_sessions:  # type: ignore
            del active_sessions[request.sid]  # type: ignore
        # Sai da sala do SocketIO
        leave_room(room_id)
        emit('room_left', {'room_id': room_id})
        print(f"Usuário {user_id} saiu da sala {room_id}")
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    """Manipula desconexão de um cliente"""
    session_id = request.sid  # type: ignore
    print(f"Cliente desconectado: {session_id}")
    # Remove da sessão ativa (garantido)
    if request.sid in active_sessions:  # type: ignore
        session_data = active_sessions[request.sid]  # type: ignore
        room_id = session_data['room']
        user_id = session_data['user_id']
        # Remove usuário da sala
        if room_id in active_rooms and user_id in active_rooms[room_id]['users']:
            active_rooms[room_id]['users'].remove(user_id)
            # Se não há mais usuários, remove a sala
            if len(active_rooms[room_id]['users']) == 0:
                del active_rooms[room_id]
            else:
                # Notifica outros usuários
                emit('user_left', {
                    'user_id': user_id,
                    'users_count': len(active_rooms[room_id]['users'])
                }, to=room_id, include_self=False)
        del active_sessions[request.sid]  # type: ignore

# Zeroização e limpeza ao fechar o servidor
import atexit

def secure_cleanup():
    zeroize(active_sessions)
    zeroize(active_rooms)
    gc.collect()

atexit.register(secure_cleanup)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Servidor iniciado na porta {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False) 