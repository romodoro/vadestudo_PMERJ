import os
import time
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

# ================== VARIÁVEIS DE AMBIENTE ==================
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# ================== CLIENTES ==================
openai_client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()

# ================== HEALTH CHECK ==================
@app.get("/")
def health():
    return {"status": "online"}

# ================== CONTROLE DE ASSINATURA ==================
def is_subscriber(telegram_id: int) -> bool:
    """
    MVP: todos são assinantes.
    Futuro: integrar com Stripe / Mercado Pago / Supabase
    """
    return True

# ================== ENVIO DE MENSAGEM TELEGRAM ==================
def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# ================== THREADS EM MEMÓRIA (MVP) ==================
# Em produção real: usar banco (Redis / Supabase)
threads = {}

def get_thread(chat_id: int):
    if chat_id not in threads:
        thread = openai_client.beta.threads.create()
        threads[chat_id] = thread.id
    return threads[chat_id]

# ================== WEBHOOK TELEGRAM ==================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    try:
        message = data.get("message")
        if not message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        if not user_text:
            return {"ok": True}

        # 🔐 Verifica assinatura
        if not is_subscriber(chat_id):
            send_message(
                chat_id,
                "🚫 Você não é assinante.\n\nAssine por apenas *R$ 9,90/mês*:\nhttps://vadestudo.com.br"
            )
            return {"ok": True}

        # 🧠 Recupera ou cria thread
        thread_id = get_thread(chat_id)

        # ➕ Envia mensagem do usuário
        openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_text
        )

        # ▶️ Executa Assistant
        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # ⏳ Aguarda conclusão
        while True:
            run_status = openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            time.sleep(0.6)

        # 📥 Busca resposta
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread_id
        )

        answer = messages.data[0].content[0].text.value
        send_message(chat_id, answer)

    except Exception as e:
        print("Erro no webhook:", e)

    return {"ok": True}
