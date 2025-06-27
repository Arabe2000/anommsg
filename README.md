# Deploy do Chat Seguro no Render.com

Este guia mostra como subir o servidor do Chat Seguro no Render.com de forma rápida e segura.

## Estrutura da pasta para deploy

```
render/
├── server.py
├── requirements.txt
├── Procfile
├── render.yaml
└── README.md
```

## Passo a passo para deploy

### 1. Crie a pasta `render/` e coloque os arquivos:
- `server.py` (código do servidor)
- `requirements.txt` (dependências)
- `Procfile` (comando de inicialização)
- `render.yaml` (configuração Render)
- `README.md` (este tutorial)

### 2. Conteúdo dos arquivos

#### `Procfile`
```
web: gunicorn --worker-class eventlet -w 1 server:app
```

#### `requirements.txt`
```
cryptography==41.0.7
flask==2.3.3
flask-cors==4.0.0
flask-socketio==5.3.6
python-socketio==5.9.0
python-engineio==4.7.1
gunicorn==21.2.0
```

#### `render.yaml`
```
services:
  - type: web
    name: secure-chat-server
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --worker-class eventlet -w 1 server:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: SECRET_KEY
        generateValue: true
```

#### `server.py`
Coloque o arquivo `server.py` já configurado (o mesmo do seu projeto).

### 3. Suba para um repositório Git (GitHub, GitLab, etc)

Exemplo:
```bash
git init
cd render
# Adicione todos os arquivos
# git add .
# git commit -m "Deploy do chat seguro no Render"
# git remote add origin <url-do-seu-repo>
# git push -u origin main
```

### 4. No Render.com
- Crie um novo Web Service
- Conecte ao seu repositório
- O Render detecta o `render.yaml` e configura tudo automaticamente
- Aguarde o deploy

### 5. Após deploy
- O Render mostrará a URL do seu servidor (ex: `https://seu-app.onrender.com`)
- Use essa URL no seu `client.py` para conectar ao servidor online

### 6. Segurança
- O Render já gera uma `SECRET_KEY` forte automaticamente
- O servidor não salva logs, IPs ou mensagens
- Para máxima segurança, use sempre HTTPS (Render já fornece)

---

## Dicas
- Não suba o client.py para o Render, apenas o servidor
- Se quiser atualizar o servidor, basta dar push no repositório e o Render faz o redeploy
- Para logs, use apenas para debug temporário e nunca salve dados sensíveis

---

Pronto! Seu chat seguro estará online e pronto para uso! 