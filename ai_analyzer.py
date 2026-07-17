import requests
from config import MODEL_OPENROUTER, PROMPT_SISTEM

def analisis_ai(openrouter_key, artikel, kategori_label=""):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
    }

    user_prompt = f"""
Kategori: {kategori_label}
Judul berita: {artikel['judul']}
Penjelasan berita: {artikel['deskripsi']}
Sumber: {artikel['sumber']}
Waktu terbit: {artikel['waktu_terbit']}

Buat output dengan format:
1. Inti berita
2. Dampak pasar
3. Sentimen
4. Level perhatian trader/investor
"""

    payload = {
        "model": MODEL_OPENROUTER,
        "messages": [
            {"role": "system", "content": PROMPT_SISTEM},
            {"role": "user", "content": user_prompt},
        ],
        "reasoning": {"enabled": True},
        "temperature": 0.3,
        "max_tokens": 600,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
    msg = data["choices"][0]["message"]
    return msg.get("content", "Tidak ada hasil analisis.")