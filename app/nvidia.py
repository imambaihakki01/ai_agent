from openai import AsyncOpenAI
from app.config import get_settings

SYSTEM_PROMPT = (
    "Kamu adalah asisten kerja Facebook berbahasa Indonesia. Bantu pengguna "
    "menyusun caption, ide konten, kalender publikasi, hashtag, analisis teks "
    "komentar/pesan yang diberikan pengguna, dan draf balasan. Jangan mengaku "
    "telah membuka atau mengubah akun Facebook. Jangan meminta password, OTP, "
    "cookie, atau token sesi. Jangan memberi instruksi untuk melewati CAPTCHA, "
    "2FA, batas platform, atau kontrol keamanan. Tindakan berdampak pada akun "
    "harus dilakukan pengguna secara manual setelah meninjau draf."
)

async def ask_nvidia(prompt: str, history: list[dict[str, str]]) -> str:
    settings = get_settings()
    if not settings.nvidia_api_key:
        raise RuntimeError("NVIDIA_API_KEY belum diisi di file .env")
    async with AsyncOpenAI(
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        timeout=settings.nvidia_timeout_seconds,
        max_retries=1,
    ) as client:
        response = await client.chat.completions.create(
            model=settings.nvidia_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-12:],
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
    return response.choices[0].message.content or "Model tidak mengembalikan teks."
