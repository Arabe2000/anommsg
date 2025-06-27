# Protocolo 20M - Servidor Seguro

Servidor de comunicação segura para o Protocolo 20M.

## Deploy no Render.com

Este projeto está configurado para deploy automático no Render.com.

### Configuração

1. **Fork** este repositório para sua conta GitHub
2. No Render.com, crie um novo **Web Service**
3. Conecte com seu repositório GitHub
4. O Render detectará automaticamente o `render.yaml` e configurará tudo

### Estrutura de Arquivos

- `server.py`: Aplicação Flask principal com SocketIO
- `app.py`: Entry point para o Gunicorn (importa server.py)
- `render.yaml`: Configuração do Render.com
- `Procfile`: Configuração alternativa do Render
- `requirements.txt`: Dependências Python
- `runtime.txt`: Versão do Python (3.9.16)

### Comando de Inicialização

O Render usará:
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

### Variáveis de Ambiente

O Render irá gerar automaticamente:
- `SECRET_KEY`: Chave secreta para o Flask
- `PORT`: Porta do servidor (gerenciada pelo Render)

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

### Teste Local

Para testar localmente:
```bash
python server.py
```

Em outro terminal:
```bash
python test_local.py
```

### Cliente

Use o cliente Python (`client.py`) para conectar ao servidor.

## Solução de Problemas

Se o deploy falhar:
1. Verifique se todos os arquivos estão no repositório
2. Confirme que o `render.yaml` está correto
3. O Render deve usar `app:app` (não `server:app`)
4. Verifique os logs no Render para detalhes do erro 