from fastapi import FastAPI       #Fastapi는 서버가 반드시 필요하다.

app = FastAPI() #앱 생성

@app.get("/")
def read_root() : # c드라이브보다 상위 폴더가 없기 때문에 root 라고 표현한다(최상위)
    return {"message": "Hello World!!!!"}
