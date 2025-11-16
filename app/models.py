from bson.objectid import ObjectId
from . import mongo

# PERFILES DE USO

def get_all_perfiles():
    return list(mongo.db.perfiles_uso.find())


def get_perfil_by_id(perfil_id):
    return mongo.db.perfiles_uso.find_one({"_id": ObjectId(perfil_id)})


def create_perfil(data):
    return mongo.db.perfiles_uso.insert_one(data)


def update_perfil(perfil_id, data):
    return mongo.db.perfiles_uso.update_one(
        {"_id": ObjectId(perfil_id)},
        {"$set": data}
    )


def delete_perfil(perfil_id):
    return mongo.db.perfiles_uso.delete_one({"_id": ObjectId(perfil_id)})


# MARCAS

def get_all_marcas():
    return list(mongo.db.marcas.find())


def get_marca_by_id(marca_id):
    return mongo.db.marcas.find_one({"_id": ObjectId(marca_id)})


def create_marca(data):
    return mongo.db.marcas.insert_one(data)


def update_marca(marca_id, data):
    return mongo.db.marcas.update_one(
        {"_id": ObjectId(marca_id)},
        {"$set": data}
    )


def delete_marca(marca_id):
    return mongo.db.marcas.delete_one({"_id": ObjectId(marca_id)})


# MODELOS DE COMPUTADORA

def get_all_modelos():
    return list(mongo.db.modelos_computadora.find())


def get_modelo_by_id(modelo_id):
    return mongo.db.modelos_computadora.find_one({"_id": ObjectId(modelo_id)})


def get_modelo_by_codigo(codigo_modelo):
    return mongo.db.modelos_computadora.find_one({"codigo_modelo": codigo_modelo})


def create_modelo(data):
    return mongo.db.modelos_computadora.insert_one(data)


def update_modelo(modelo_id, data):
    return mongo.db.modelos_computadora.update_one(
        {"_id": ObjectId(modelo_id)},
        {"$set": data}
    )


def delete_modelo(modelo_id):
    return mongo.db.modelos_computadora.delete_one({"_id": ObjectId(modelo_id)})


# CONSULTAS DEL CORE

def get_all_consultas():
    #  Implementacion futura del core del usuario
    return list(mongo.db.consultas.find())


def create_consulta(data):
    return mongo.db.consultas.insert_one(data)