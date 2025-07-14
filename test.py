import base64

import requests
from openai import OpenAI

base_url = "http://localhost:8000/v1/"

hy_source = "web"
hy_user = "d76efed3f1fb4cf1b1a3b4789111bc6c"    # 替换为你的用户ID
hy_token = "8tE8bq6InCxff5mUqQZfc9aGHP6NPD80Cr/k258SiLJ9CYW8HiMzU5pREYyvnbvjj2OpKM+T7S7ee8ghrobpqLmiGPzSdAUMQl/MAAYWX+8kuVZo/AW2p3u6OBmDiYBzj7fh3CZr8YXN90ZLbp9BuodnnBQofxVAX1Lxv/i63vrxRa9Jo8pnVxl0yUkBQYNKKfW4hQhyjNc/ydiZOqtze8VuB1g0GiVSZdHe3q3tZ0b6kffbkMz8yxb4q8QUQwL02K41IAddgfQ1/lN9hfzLTSt8y5SYP5Wdwq90FlryoJ7eJWezPZrfGwu1HXcu1gxkY+nr8r9y2XBcBOdph2R4l8w0XjD+UTLJup75mPAArtmRlV5nXqDIn1uQ1M6tpE90fhqp2GfHKyjGZ2VIx76Gu/VNS3KxQm0xqN53uaR4p/JfyOfFjFKcKsqmjr0i7+FfAdDDl2fsF6OlVZluTmi/sovQ6RuPLTRypa2F78fdxbU9B4WqAGiv5uochHDcCXC9dlumv+UFl5QCd4tEGxFTX1ZeqDn8NKInrQLAN0HXSQBRLU4cvUUs56SDdOXj3sPLz3o0qoUTBIzIANypSaJaYeHshewrc1a3tOwXizN70ZLJZ0EWyD/nJp2nCh7wJNck"   # 替换为你的token

agent_id = "naQivTmsDa"
chat_id = ""    # 可选，如果不提供会自动创建

# upload，可选
url = base_url + "upload"

file_name = "example.png"
with open(file_name, "rb") as f:
    file_data = base64.b64encode(f.read()).decode("utf-8")
data = {
    "agent_id": agent_id,
    "hy_source": hy_source,
    "hy_user": hy_user,
    "file": {
        "file_name": file_name,
        "file_data": file_data ,
        "file_type": "image",   # 只能是 image 或 doc
    },
}
# headers = {"Authorization": f"Bearer {hy_token}"}
# response = requests.post(url, json=data, headers=headers)
# if response.status_code == 200:
#     print("File uploaded successfully:", response.json())
#     multimedia = [response.json()]
# else:
#     print("File upload failed:", response.status_code, response.text)
#     multimedia = []
# print(multimedia)

# chat
client = OpenAI(base_url=base_url, api_key=hy_token)

response = client.chat.completions.create(
    model="deepseek-v3",
    messages=[{"role": "user", "content": "这是什么？"}],
    stream=False,
    extra_body={
        "hy_source": hy_source,
        "hy_user": hy_user,
        "agent_id": agent_id,
        "chat_id": chat_id,
        "should_remove_conversation": False,
    },
)
print(type(response))
for chunk in response:
    print(chunk.choices[0].delta.content or "")