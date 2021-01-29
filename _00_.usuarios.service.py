from bunch import Bunch
from bunch import bunchify
from zato.server.service import Service
import requests
import json
import sys


class Service(Service):
    def handle(self):
        try:
            contador = 0
            redis = Bunch()

            apiKey = "AIzaSyAhdZtcSmitOdDVE2ER70QvtZ23w7_1eeo"

            urlLogin = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={0}".format(apiKey)

            payload = {"email":"test@test.com","password":"Test1234","returnSecureToken":True}
        
            response = requests.post(urlLogin, data=json.dumps(payload), headers={})
            
            if response.status_code == 200:
                rta = response.json()
                idToken = rta["idToken"]

                urlBase = "https://flutterpush-993a6.firebaseio.com/{0}.json?auth={1}".format("usuarios", idToken)

                rtaUsers = requests.get(urlBase)

                # OBTENGO LOS FCMToken de cada usuario registrado
                if rtaUsers.status_code == 200:
                    usuariosRegistrados =  rtaUsers.json()
                    contador = 0
                    
                    Usuarios = []
                    
                    localId = str
                    fcmToken = str
                    
                    for usuario in usuariosRegistrados:
                        userName = usuario
                        contador = contador + 1

                        for key in usuariosRegistrados.get(usuario):
                            for userData in usuariosRegistrados.get(usuario).get(key):
                                
                                if userData.upper() != "EMAIL":
                                    fcmToken = usuariosRegistrados.get(usuario).get(key).get("fcmToken", '')
                                
                                    localId = usuariosRegistrados.get(usuario).get(key).get("localId", '')
                                

                            Usuarios.append({
                                "userName": usuario,
                                "fcmToken": fcmToken,
                                "localId": localId
                            })


                # OBTENGO LA DATA PARA ENVIAR EN LA NOTIFICACION
                urlBase = "https://flutterpush-993a6.firebaseio.com/.json?auth={0}".format(idToken)

                rtaSistema = requests.get(urlBase)
                
                if rtaSistema.status_code == 200:
                    data =  rtaSistema.json()

                    redis.db = Bunch()

                    Certificados = []
                    Mascotas = []
                    Vacunas = []

                    # RECORRE SOLO POR KEY USUARIOS (uid)
                    for uid in data: 
                        if uid.upper() == "SISTEMA" or uid.upper() == "USUARIOS":
                            continue
                        else:

                            # RECORRER POR LAS KEY CERTIFICADOS, MEDICOS, VACUNAS, MASCOTAS, CURSOS, ETC
                            for keyData in data.get(uid):
                            
                                # si la key es igual a medico o cursos sigo el for
                                if keyData.upper() == "MEDICO" or keyData.upper() == "CURSOS":
                                    continue
                                
                                # si la key es certificados reviso los certificados de cada mascota.
                                if keyData.upper() == "CERTIFICADOS":
                                    for mascotaId in data.get(uid).get(keyData): 
                                        
                                        for idCertificado in data.get(uid).get(keyData).get(mascotaId): 
                                            certificadoAprobado = data.get(uid).get(keyData).get(mascotaId).get(idCertificado).get("aprobado")
                                            if certificadoAprobado:
                                                fechaCertificado = data.get(uid).get(keyData).get(mascotaId).get(idCertificado).get("fechaCertificado")
                                                
                                                Certificados.append({
                                                    "uid": uid,
                                                    "mascotaId": mascotaId,
                                                    "certificado": idCertificado,
                                                    "aprobado": certificadoAprobado,
                                                    "fechaCertificado": str(fechaCertificado)
                                                })

                                if keyData.upper() == "MASCOTAS":
                                    for mascotaId in data.get(uid).get(keyData):
                                        nombreMascota = data.get(uid).get(keyData).get(mascotaId).get("nombre")
                                        fechaNacimiento = data.get(uid).get(keyData).get(mascotaId).get("nacimiento")

                                        Mascotas.append({
                                            "uid": uid,
                                            "mascotaId": mascotaId,
                                            "nombre": nombreMascota,
                                            "fechaNacimiento": str(fechaNacimiento)
                                        })

                                if keyData.upper() == "VACUNACION":
                                    for mascotaId in data.get(uid).get(keyData): 
                                        for idVacuna in data.get(uid).get(keyData).get(mascotaId): 
                                            fechaAplicacion = data.get(uid).get(keyData).get(mascotaId).get(idVacuna).get("fechaAplicacion")
                                            fechaVto = data.get(uid).get(keyData).get(mascotaId).get(idVacuna).get("fechaVencimiento", '')
                                            anual = data.get(uid).get(keyData).get(mascotaId).get(idVacuna).get("anual")
                                            descripcion = data.get(uid).get(keyData).get(mascotaId).get(idVacuna).get("descripcion")

                                            Vacunas.append({
                                                "uid": uid,
                                                "mascotaId": mascotaId,
                                                "vacunaId": idVacuna,
                                                "fechaAplicacion": str(fechaAplicacion),
                                                "fechaVencimiento": str(fechaVto),
                                                "anual": anual,
                                                "descripcion": descripcion
                                            })

                    redis.usuariosNotificaciones = Usuarios
                    redis.db.certificados = Certificados
                    redis.db.vacunacion = Vacunas
                    redis.db.mascotas = Mascotas

        except Exception as e:
            redis.error = str(e) + " - linea: " + str(sys.exc_info()[-1].tb_lineno)

return redis
        # self.response.payload = redis.toJSON()
