from fastapi import FastAPI
from deta import app
from bunch import Bunch
from bunch import bunchify
import requests
import json
import sys

app: FastAPI()


@app.lib.cron()
def notificaciones(event):
    respuesta = Bunch()

    usuariosFirebase = []

    usuariosFirebase.append({"fcmToken": "eIAXoTA9RUaRFeqv5BPfX1:APA91bEIWSXW8JJUZF0haWoUP_C11p8j9pSa8Lc9G5bUrSD0-Tq4BSAcnSRg0za97rGLDEzmatZv9l8xeHI0S1O7oU7byPX71fl1sM1_PxVxBelIzeNX8mqwIK1FlDXua10da0VV0f-c"})

    try:
        cloudKey = "AAAAt4bPs1w:APA91bHMj8QuWqMLKVdtE_KqKBjYAbU5miK3mZkhLZUHILpZXGjD7YI8XD5XJVUno9nrvFbRfy0usxCbBhTTrrPBWHUDh9aKVpG9KtkqAzMSUIjUUrX5LA8JZDtqjFkhw0a10rOpJQyD"

        url = 'https://fcm.googleapis.com/fcm/send'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=AAAAt4bPs1w:APA91bHMj8QuWqMLKVdtE_KqKBjYAbU5miK3mZkhLZUHILpZXGjD7YI8XD5XJVUno9nrvFbRfy0usxCbBhTTrrPBWHUDh9aKVpG9KtkqAzMSUIjUUrX5LA8JZDtqjFkhw0a10rOpJQyD'
        }

        for userFCM in usuariosFirebase:
            payload = {
                "notification": {
                    "body": "",
                    "title": "Patita Patita"
                },
                "priority": "high",
                "data": {
                    "uid": "1",
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "mensajePush": "prueba desde zato"
                },
                "to": userFCM["fcmToken"]
            }

            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                respuesta.status = "OK"
            else:
                respuesta.status = "FAIL"
                respuesta.response = str(response)

    except Exception as e:
        respuesta.error = str(e) + " " + str(sys.exc_info()[-1].tb_lineno)

    return respuesta.toJSON()