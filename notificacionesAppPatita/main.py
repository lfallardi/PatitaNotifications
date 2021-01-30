from deta import App
from bunch import Bunch
from bunch import bunchify
import requests
import json
import sys
from datetime import date, datetime
from fastapi import FastAPI

app = App(FastAPI())

@app.post("/")
def sendNotification():
    respuesta = Bunch()

    usuariosFirebase = []
    usuariosFirebase.append({"fcmToken": "eIAXoTA9RUaRFeqv5BPfX1:APA91bEIWSXW8JJUZF0haWoUP_C11p8j9pSa8Lc9G5bUrSD0-Tq4BSAcnSRg0za97rGLDEzmatZv9l8xeHI0S1O7oU7byPX71fl1sM1_PxVxBelIzeNX8mqwIK1FlDXua10da0VV0f-c"})

    respuesta.status = "OK"
    respuesta.usuario = usuariosFirebase

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
                        "body": "Deta test notification",
                        "title": "Patita Patita"
                    },
                    "priority": "high",
                    "data": {
                        "uid": "1",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        "mensajePush": "prueba desde deta"
                    },
                    "to": userFCM["fcmToken"]
                }


            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                respuesta.statusSend = "OK"
            else:
                respuesta.statusSend = "FAIL"
                respuesta.response = str(response)


    except Exception as e:
        notif = Bunch()
        notif.cloudKey = cloudKey
        notif.url = url
        notif.headers = headers
        notif.payload = payload
        respuesta.postNotif = notif
        respuesta.error = str(e) + " " + str(sys.exc_info()[-1].tb_lineno)

    return respuesta    

def loadCertificadosByUserByMascota(db, UID, petId):
    try:
        certificados = []
        for keyData in db.get(UID):
            if keyData.upper() == "CERTIFICADOS":
                for mascotaId in db.get(UID).get(keyData): 
                    certificados = []
                    for idCertificado in db.get(UID).get(keyData).get(mascotaId): 
                        certificadoAprobado = db.get(UID).get(keyData).get(mascotaId).get(idCertificado).get("aprobado")
                        if certificadoAprobado:
                            fechaCertificado = db.get(UID).get(keyData).get(mascotaId).get(idCertificado).get("fechaCertificado")
                            
                            certificados.append({
                                "certificado": idCertificado,
                                "aprobado": certificadoAprobado,
                                "fechaCertificado": str(fechaCertificado)
                            })

        return certificados if len(certificados) > 0 else None
    except Exception as e:
        return str(e) + " - linea: " + str(sys.exc_info()[-1].tb_lineno)

def loadVacunasByUserByMascota(db, UID, petId):
    try:
        vacunas = []
        for keyData in db.get(UID):
            if keyData.upper() == "VACUNACION":
                for mascotaId in db.get(UID).get(keyData): 
                    vacunas = []
                    for idVacuna in db.get(UID).get(keyData).get(mascotaId): 
                        fechaAplicacion = db.get(UID).get(keyData).get(mascotaId).get(idVacuna).get("fechaAplicacion")
                        fechaVto = db.get(UID).get(keyData).get(mascotaId).get(idVacuna).get("fechaVencimiento", '')
                        anual = db.get(UID).get(keyData).get(mascotaId).get(idVacuna).get("anual")
                        descripcion = db.get(UID).get(keyData).get(mascotaId).get(idVacuna).get("descripcion")

                        vacunas.append({
                            "vacunaId": idVacuna,
                            "fechaAplicacion": str(fechaAplicacion),
                            "fechaVencimiento": str(fechaVto),
                            "anual": anual,
                            "descripcion": descripcion
                        })

        return vacunas if len(vacunas) > 0 else None
    except Exception as e:
        return str(e) + " - linea: " + str(sys.exc_info()[-1].tb_lineno)

def loadDataBase():
    dataBase = Bunch()

    try:
        contador = 0
        respuestaFinal = Bunch()

        apiKey = "AIzaSyAhdZtcSmitOdDVE2ER70QvtZ23w7_1eeo"

        urlLogin = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={0}".format(apiKey)

        payload = {"email":"test@test.com","password":"Test1234","returnSecureToken":True}
    
        responseLogin = requests.post(urlLogin, data=json.dumps(payload), headers={})
        
        #SI SE LOGUEO CORRECTAMENTE CON EL ADMIN
        if responseLogin.status_code == 200:
            rtaLogin = responseLogin.json()
            urlBase = "https://flutterpush-993a6.firebaseio.com/usuarios.json?auth={0}".format(rtaLogin["idToken"])

            rtaUsuarios = requests.get(urlBase)

            # OBTENGO LOS FCMToken de cada usuario registrado
            if rtaUsuarios.status_code == 200:
                usuariosRegistrados =  rtaUsuarios.json()
                
                Usuarios = []
                
                localId = str
                fcmToken = str
                
                # RECORRO EL NODO USUARIOS QUE ME VA A DEVOLVER EL VALOR DEL MAIL ANTES DEL @
                for usuario in usuariosRegistrados:
                    userName = usuario

                    # OBTENGO EL ID DE CADA USUARIO GENERADO POR FIREBASE
                    for key in usuariosRegistrados.get(usuario):
                        # RECORRO EL NODO USUARIOS - EJEMPLO - IDFIREBASE
                        for userData in usuariosRegistrados.get(usuario).get(key):
                            
                            if userData.upper() != "EMAIL":
                                fcmToken = usuariosRegistrados.get(usuario).get(key).get("fcmToken", '')
                                localId = usuariosRegistrados.get(usuario).get(key).get("localId", '')
                            
                        Usuarios.append({
                            "userName": usuario,
                            "fcmToken": fcmToken,
                            "localId": localId
                        })

            dataBase.Usuarios = Usuarios

            # OBTENGO LA DATA PARA GENERAR LA NOTIFICACION
            urlBase = "https://flutterpush-993a6.firebaseio.com/.json?auth={0}".format(rtaLogin["idToken"])

            rtaDB = requests.get(urlBase)
            
            if rtaDB.status_code == 200:
                dataBase.dataNotification = []
                
                data =  rtaDB.json()

                respuestaFinal.db = Bunch()

                # RECORRE SOLO POR KEY USUARIOS (uid)
                for uid in data:
                    dataToNotification = []

                    if uid.upper() == "SISTEMA" or uid.upper() == "USUARIOS":
                        continue

                    # RECORRER POR LAS KEY CERTIFICADOS, MEDICOS, VACUNAS, MASCOTAS, CURSOS, ETC DE CADA UID
                    for dataUID in data.get(uid):
                        
                        # si la key es igual a medico o cursos sigo el for
                        if dataUID.upper() == "MEDICO" or dataUID.upper() == "CURSOS":
                            continue
                        
                        # ENTRO SOLO SI EL NODO ES MASCOTAS (UID - mascotas)
                        if dataUID.upper() == "MASCOTAS":
                            
                            # RECORRO LAS MASCOTAS QUE TIENE EL UID
                            # OBTENGO EL ID DE CADA MASCOTA GENERADO POR FB
                            for mascotaId in data.get(uid).get(dataUID):
                                nombreMascota = data.get(uid).get(dataUID).get(mascotaId).get("nombre")
                                fechaNacimiento = data.get(uid).get(dataUID).get(mascotaId).get("nacimiento")

                                mensajeMascota = ""
                                if date.today().day() == fechaNacimiento.strptime().day() and date.today().month() == fechaNacimiento.strptime().month():
                                    mensajeMascota = "🎊🎉🥳 Hoy es el cumpleaños de tu mascota {0}!!!🥳🎉🎊".format(nombreMascota)

                                dataToNotification.append({
                                    "mascotaId": mascotaId,
                                    "nombre": nombreMascota,
                                    "fechaNacimiento": str(fechaNacimiento),
                                    "msjNotificacion": mensajeMascota if mensajeMascota != "" else None,
                                    "vacunas": loadVacunasByUserByMascota(data, uid, mascotaId),
                                    "certificados": loadCertificadosByUserByMascota(data, uid, mascotaId)
                                })

                    dataBase.dataNotification.append({
                        "uid": uid,
                        "dataToNotification": dataToNotification if len(dataToNotification) > 0 else None
                    })

    except Exception as e:
        dataBase.error = str(e) + " - linea: " + str(sys.exc_info()[-1].tb_lineno)

    return dataBase


@app.lib.cron()
def cron_job(event):
    respuesta = Bunch()

    db = loadDataBase()

    usuariosFirebase = []
    usuariosFirebase.append({"fcmToken": "eIAXoTA9RUaRFeqv5BPfX1:APA91bEIWSXW8JJUZF0haWoUP_C11p8j9pSa8Lc9G5bUrSD0-Tq4BSAcnSRg0za97rGLDEzmatZv9l8xeHI0S1O7oU7byPX71fl1sM1_PxVxBelIzeNX8mqwIK1FlDXua10da0VV0f-c"})

    respuesta.status = "OK"
    respuesta.usuario = db.Usuarios
    respuesta.notificaciones = db.dataNotification

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
                        "body": "Deta test notification 😁",
                        "title": "Patita Patita"
                    },
                    "priority": "high",
                    "data": {
                        "uid": "1",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        "mensajePush": "prueba desde deta 😁"
                    },
                    "to": userFCM["fcmToken"]
                }


            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                respuesta.statusSend = "OK"
            else:
                respuesta.statusSend = "FAIL"
                respuesta.response = str(response)

    except Exception as e:
        notif = Bunch()
        notif.cloudKey = cloudKey
        notif.url = url
        notif.headers = headers
        notif.payload = payload
        respuesta.postNotif = notif
        respuesta.error = str(e) + " " + str(sys.exc_info()[-1].tb_lineno)

    return respuesta