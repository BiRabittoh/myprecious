import base64, json

def obj_decode(text):
    base64_bytes = text.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return json.loads(message)

def obj_encode(info):
    temp_json = json.dumps(info)
    temp_bytes = temp_json.encode("utf-8")
    temp_base64 = base64.b64encode(temp_bytes)
    return temp_base64.decode("utf-8")