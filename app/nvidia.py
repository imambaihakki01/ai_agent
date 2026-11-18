from openai import AsyncOpenAI

from app.config import get_settings


async def ask_nvidia(prompt: str, history: list[dict[str, str]]) -> str:
    settings = get_settings()
    if not settings.nvidia_api_key:
        raise RuntimeError("NVIDIA_API_KEY belum diatur di file .env")

    client = AsyncOpenAI(
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        timeout=settings.nvidia_timeout_seconds,
    )
    messages = [
        {
            "role": "system",
            "content": (
                "Kamu adalah asisten perencanaan Facebook AI Agent. "
                "Bantu membuat draf, ide, dan analisis. Jangan mengaku telah melakukan "
                "aksi Facebook. Jangan meminta password, cookie, atau kode OTP. "
                "Aksi yang berdampak pada akun harus memerlukan persetujuan manusia."
            ),
        },
        *history[-12:],
        {"role": "user", "content": prompt},
    ]
    response = await client.chat.completions.create(
        model=settings.nvidia_model,
        messages=messages,
        temperature=0.4,
    )
    answer = response.choices[0].message.content
    return answer or "Model tidak mengembalikan teks."
