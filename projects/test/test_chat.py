from fastapi.testclient import TestClient
from app.api.chat import app

client = TestClient(app)


def test_chat():
    response = client.post('/chat',
                           json={
                               "model": "deepseek-flash",
                               "messages": [
                                   {
                                       "role": "user",
                                       "content": "你好"
                                   }
                               ],
                               "max_tokens": 1024,
                               "temperature": 1,
                               "thinking": {
                                   "type": "disabled"
                               }
                           })
    assert response.status_code == 200


def test_stream_chat():
    response = client.post('/chat/stream',
                           json={
                                   "model": "deepseek-flash",
                                   "messages": [
                                       {
                                           "role": "user",
                                           "content": "你好介绍一下你自己"
                                       }
                                   ],
                                   "max_tokens": 1024,
                                   "temperature": 1,
                                   "thinking": {
                                       "type": "disabled"
                                   }
                                }
                           )
    assert response.status_code == 200
