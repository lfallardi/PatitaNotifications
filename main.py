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
    response = Bunch()
    response.db = loadDataBase()

    return response

@app.lib.cron()
def cron_job(event):
    respuesta = Bunch()

    db = loadDataBase()

    # usuariosFirebase = []
    # usuariosFirebase.append({"fcmToken": "eIAXoTA9RUaRFeqv5BPfX1:APA91bEIWSXW8JJUZF0haWoUP_C11p8j9pSa8Lc9G5bUrSD0-Tq4BSAcnSRg0za97rGLDEzmatZv9l8xeHI0S1O7oU7byPX71fl1sM1_PxVxBelIzeNX8mqwIK1FlDXua10da0VV0f-c"})

    respuesta.status = "OK"

    try:
        respuesta.usuario = db.Usuarios
        respuesta.notificaciones = db.dataNotification

        cloudKey = "AAAAt4bPs1w:APA91bHMj8QuWqMLKVdtE_KqKBjYAbU5miK3mZkhLZUHILpZXGjD7YI8XD5XJVUno9nrvFbRfy0usxCbBhTTrrPBWHUDh9aKVpG9KtkqAzMSUIjUUrX5LA8JZDtqjFkhw0a10rOpJQyD"

        url = 'https://fcm.googleapis.com/fcm/send'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=AAAAt4bPs1w:APA91bHMj8QuWqMLKVdtE_KqKBjYAbU5miK3mZkhLZUHILpZXGjD7YI8XD5XJVUno9nrvFbRfy0usxCbBhTTrrPBWHUDh9aKVpG9KtkqAzMSUIjUUrX5LA8JZDtqjFkhw0a10rOpJQyD'
        }
        

    except Exception as e:
        respuesta.error = str(e) + " " + str(sys.exc_info()[-1].tb_lineno)
        notif = Bunch()
        notif.cloudKey = cloudKey
        notif.url = url
        notif.headers = headers
        notif.payload = payload
        respuesta.postNotif = notif

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

    try:
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

                urlBaseDB = "https://flutterpush-993a6.firebaseio.com/.json?auth={0}".format(rtaLogin["idToken"])
                rtaDB = requests.get(urlBaseDB)
                db = None
                if rtaDB.status_code == 200:
                    db = rtaDB.json()
                
                Usuarios = []
                
                localId = str
                fcmToken = str
                
                # RECORRO EL NODO USUARIOS QUE ME VA A DEVOLVER EL VALOR DEL MAIL ANTES DEL @
                for usuario in usuariosRegistrados:
                    userName = usuario

                    # OBTENGO EL ID DE CADA USUARIO GENERADO POR FIREBASE
                    for key in usuariosRegistrados.get(usuario):
                        fcmToken = usuariosRegistrados.get(usuario).get("fcmToken", '')
                        localId = usuariosRegistrados.get(usuario).get("localId", '')

                        if fcmToken != '' and localId != '':
                            Usuarios.append({
                                "userName": usuario,
                                "fcmToken": fcmToken,
                                "localId": localId,
                                "notification": loadNotifications(db, localId)
                            }) 
                            break

                        # RECORRO EL NODO USUARIOS - EJEMPLO - IDFIREBASE
                        for userData in usuariosRegistrados.get(usuario).get(key):
                            
                            if userData.upper() != "EMAIL":
                                fcmToken = usuariosRegistrados.get(usuario).get(key).get("fcmToken", '')
                                localId = usuariosRegistrados.get(usuario).get(key).get("localId", '')
                            
                        Usuarios.append({
                            "userName": usuario,
                            "fcmToken": fcmToken,
                            "localId": localId,
                            "notification": loadNotifications(db, localId)
                        })
            
        return Usuarios
    
    except Exception as e:
        return str(e) + " - linea: " + str(sys.exc_info()[-1].tb_lineno)

def loadNotifications(db, localId):
    if db is None:
        return None
    
    try:
        notificaciones = []
        for dataUser in db.get(localId):
            if dataUser.upper() == "MEDICO" or dataUser.upper() == "CURSOS":
                continue

            if dataUser.upper() == "MASCOTAS":
                # TODO 
                for mascotaId in db.get(localId).get(dataUser):
                    nombreMascota = db.get(localId).get(dataUser).get(mascotaId).get("nombre")
                    fechaNacimiento = db.get(localId).get(dataUser).get(mascotaId).get("nacimiento")

                    # mensajeMascota = ""
                    # if date.today().day() == fechaNacimiento.strptime().day() and date.today().month() == fechaNacimiento.strptime().month():
                    #     mensajeMascota = "🎊🎉🥳 Hoy es el cumpleaños de tu mascota {0}!!!🥳🎉🎊".format(nombreMascota)

                    notificaciones.append({
                        "mascotaId": mascotaId,
                        "nombre": nombreMascota,
                        "fechaNacimiento": str(fechaNacimiento),
                        # "msjNotificacion": None,
                        "vacunas": loadVacunasByUserByMascota(db, localId, mascotaId),
                        "certificados": loadCertificadosByUserByMascota(db, localId, mascotaId)
                    })

        return notificaciones

    except Exception as e:
        return str(e) + " - linea: " + str(sys.exc_info()[-1].tb_lineno)