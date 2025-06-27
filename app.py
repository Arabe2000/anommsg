# Importa a aplicação Flask do server.py
from server import app

# Para compatibilidade com Render.com
if __name__ == "__main__":
    app.run() 