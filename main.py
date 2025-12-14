@app.get("/test-assistant")
def test_assistant():
    thread = openai_client.beta.threads.create()

    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Teste: explique o edital da PMERJ como você foi instruído."
    )

    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    while True:
        status = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if status.status == "completed":
            break
        time.sleep(0.5)

    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    return {"response": messages.data[0].content[0].text.value}
