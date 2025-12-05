#Exemplo de Backend em Python para Vadestudo_PMERJ

from fastapi import FastAPI, Request
import requests
import openai
import os

# ENV
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

openai.api_key = OPENAI_API_KEY

app = FastAPI()

# ======== FUNÇÃO TEMPORÁRIA =========
# Aqui você valida no futuro com seu banco de dados.
def is_subscriber(telegram_id):
    """
    Versão inicial: aceita todos os usuários como assinantes.
    Depois trocaremos pelo Supabase ou Firebase.
    """
    return True


# ====== FUNÇÃO PARA ENVIAR MENSAGEM AO TELEGRAM ======
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


# ============ WEBHOOK PRINCIPAL =============
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        # Verificação de assinatura
        if not is_subscriber(chat_id):
            send_message(
                chat_id,
                "🚫 Você não é assinante.\nAssine por apenas R$ 9,90/mês:\nhttps://vadestudo.com.br"
            )
            return {"ok": True}

        # Enviar mensagem ao Assistente da OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "PROMPT MESTRE PMERJ VAI AQUI"},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response["choices"][0]["message"]["content"]
        send_message(chat_id, answer)

    except Exception as e:
        print("Erro:", e)

    return {"ok": True}
