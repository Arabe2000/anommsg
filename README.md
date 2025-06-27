# Protocolo 20M - Servidor Seguro

Servidor de comunicação segura para o Protocolo 20M.

## Deploy no Render.com

Este projeto está configurado para deploy automático no Render.com.

### Configuração

1. **Fork** este repositório para sua conta GitHub
2. No Render.com, crie um novo **Web Service**
3. Conecte com seu repositório GitHub
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app`
   - **Python Version**: 3.9.16

### Variáveis de Ambiente

O Render irá gerar automaticamente:
- `SECRET_KEY`: Chave secreta para o Flask
- `PORT`: Porta do servidor (gerenciada pelo Render)

### Estrutura de Arquivos

- `server.py`: Aplicação Flask principal
- `wsgi.py`: Entry point para o Gunicorn
- `Procfile`: Configuração do Render
- `requirements.txt`: Dependências Python
- `runtime.txt`: Versão do Python

### Endpoints

- `GET /health`: Verificação de saúde
- `POST /api/create-room`: Criar nova sala
- `POST /api/join-room`: Entrar em sala existente
- WebSocket: Comunicação em tempo real

### Segurança

- Criptografia end-to-end com Fernet
- IDs de sala como seed phrases
- Zeroização de memória
- Autenticação HMAC
- Sem persistência de dados

### Cliente

Use o cliente Python (`client.py`) para conectar ao servidor. 