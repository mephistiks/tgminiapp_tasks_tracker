import ssl
import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,

        # для локальной разработки разкоментирвоать строчки ниже
        # прописать в папке certs команду
        # mkcert localhost 127.0.0.1 ::1

        ssl_keyfile='./certs/localhost+2-key.pem',
        ssl_certfile='./certs/localhost+2.pem'
    )
