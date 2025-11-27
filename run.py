from app import create_app

# inicializar dotenv
from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)