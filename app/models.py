from . import mongo
from bson.objectid import ObjectId 

#  USUARIOS

def create_user(data):
    return mongo.db.usuarios.insert_one(data)

def get_user_by_email(email):
    return mongo.db.usuarios.find_one({"email": email})

#  PERFILES DE USO

def create_perfil(data):
    return mongo.db.perfiles_uso.insert_one(data)

def get_all_perfiles():
    return list(mongo.db.perfiles_uso.find())

def get_perfil_by_id(id):
    try:
        return mongo.db.perfiles_uso.find_one({"_id": ObjectId(id)})
    except:
        return None

def update_perfil(id, data):
    return mongo.db.perfiles_uso.update_one({"_id": ObjectId(id)}, {"$set": data})

def delete_perfil(id):
    return mongo.db.perfiles_uso.delete_one({"_id": ObjectId(id)})

#  MARCAS

def create_marca(data):
    return mongo.db.marcas.insert_one(data)

def get_all_marcas():
    return list(mongo.db.marcas.find())

def get_marca_by_id(id):
    try:
        return mongo.db.marcas.find_one({"_id": ObjectId(id)})
    except:
        return None

def update_marca(id, data):
    return mongo.db.marcas.update_one({"_id": ObjectId(id)}, {"$set": data})

def delete_marca(id):
    return mongo.db.marcas.delete_one({"_id": ObjectId(id)})


#  MODELOS 

def create_modelo(data):
    return mongo.db.modelos_computadora.insert_one(data)

def get_all_modelos():
    return list(mongo.db.modelos_computadora.find())

def get_modelo_by_id(id):
    try:
        return mongo.db.modelos_computadora.find_one({"_id": ObjectId(id)})
    except:
        return None

def get_modelo_by_codigo(codigo):
    return mongo.db.modelos_computadora.find_one({"codigo_modelo": codigo})

def update_modelo(id, data):
    return mongo.db.modelos_computadora.update_one({"_id": ObjectId(id)}, {"$set": data})

def delete_modelo(id):
    return mongo.db.modelos_computadora.delete_one({"_id": ObjectId(id)})

def get_all_laptops():
    """
    Trae los datos de la segunda colección.
    """
    return list(mongo.db.modelos_laptops.find())

def get_all_consultas():

    return list(mongo.db.consultas.find())

def buscar_modelos_por_nombre(texto):
    query = {"nombre": {"$regex": texto, "$options": "i"}}
    return list(mongo.db.modelos_computadora.find(query))

def obtener_perfil_por_id(perfil_id):
    return mongo.db.perfiles_uso.find_one({"_id": ObjectId(perfil_id)})

def obtener_modelos():
    return list(mongo.db.modelos_computadora.find())