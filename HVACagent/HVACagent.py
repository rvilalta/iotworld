from flask import json, Blueprint, request, Response
from flask.views import MethodView
import sys
from objects_common.keyedArrayType import KeyedArrayKeyError

import base64
import re

# BACKEND FUNCTIONS
from funcs_HVACagent.hvacImpl import HvacImpl
from funcs_HVACagent.hvacTemperatureImpl import HvacTemperatureImpl
from funcs_HVACagent.hvacAcImpl import HvacAcImpl
from funcs_HVACagent.hvacHeatImpl import HvacHeatImpl

# CALLABLE OBJECTS
from objects_HVACagent.ac import Ac
from objects_HVACagent.heat import Heat
from objects_HVACagent.hVAC import HVAC
from objects_HVACagent.temperature import Temperature

users = {"admin": "pswd1", "user": "pswd2"}

setattr(sys.modules[__name__], __name__,  Blueprint(__name__, __name__))



def byteify(input):
    # Convert JSON unicode strings to python byte strings, recursively on a json_struct
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def json_loads(json_string):
    # Try to use json.loads and raise HTTP Error
    try:
        json_struct = json.loads(json_string) #json parser.
    except ValueError:
        raise BadRequestError("Malformed JSON")
    else:
        return byteify(json_struct)

def json_dumps(js):
    # Pretty-print version of json.dumps
    return json.dumps(js, sort_keys=True, indent=4, separators=(',', ': '))

def create_instance(klass, json_struct, id=None):
    # Try to create an object instance and raise HTTP Errors
    try:
        new_object = klass(json_struct) # Creates an object instance of type klass from the json_struct data
    except KeyError as inst:
        return BadRequestError("Unknown entity name in JSON:" + "<br>" + inst.args[0])
    except TypeError as inst:
        key = inst.args[0]
        value = json.dumps(inst.args[1])
        return BadRequestError("Incorrect type in JSON:" + "<br>" +
                              key + " was:" + "<br>" +
                              value + "<br>" +
                              "Allowed type:" + "<br>" +
                              inst.args[2])
    except ValueError as inst:
        if type(inst.args[1]) == str:
            return BadRequestError("Incorrect value in JSON:" + "<br>" +
                                  "Enum " + inst.args[0] + " was:" + "<br>" +
                                  inst.args[1] + "<br>" +
                                  "Allowed values:" + "<br>" +
                                  "[" + ", ".join(inst.args[2]) + "]")
        elif type(inst.args[1]) == int:
            return BadRequestError("Incorrect value in JSON:" + "<br>" +
                                  "Enum " + inst.args[0] + " was:" + "<br>" +
                                  str(inst.args[1]) + "<br>" +
                                  "Allowed range:" + "<br>" +
                                  "1 - " + str(inst.args[2]))
    except KeyedArrayKeyError as inst:
        return BadRequestError("Error in JSON:" + "<br>" +
                              "Missing key in list:" + "<br>" +
                              inst.args[0] + "<br>" +
                              "Received JSON:" + "<br>" +
                              json.dumps(inst.args[1]) + "<br>" +
                              "Key name:" + "<br>" +
                              inst.args[2])
    else:
        # Check if the id given in the URL matches the id given in the body
        if id != None and id[0] != getattr(new_object, id[1]):
            return BadRequestError(id[1] + " in body not matching " + id[1] + " in URL")
        else:
            return new_object

def modify_instance(existing_object, json_struct):
    try:
        existing_object.load_json(json_struct)
    except KeyError as inst:
        return BadRequestError("Unknown entity name in JSON:" + "<br>" + inst.args[0])
    except TypeError as inst:
        key = inst.args[0]
        value = json.dumps(inst.args[1])
        return BadRequestError("Incorrect type in JSON:" + "<br>" +
                              key + " was:" + "<br>" +
                              value + "<br>" +
                              "Allowed type:" + "<br>" +
                              inst.args[2])
    except ValueError as inst:
        if type(inst.args[1]) == str:
            return BadRequestError("Incorrect value in JSON:" + "<br>" +
                                  "Enum " + inst.args[0] + " was:" + "<br>" +
                                  inst.args[1] + "<br>" +
                                  "Allowed values:" + "<br>" +
                                  "[" + ", ".join(inst.args[2]) + "]")
        elif type(inst.args[1]) == int:
            return BadRequestError("Incorrect value in JSON:" + "<br>" +
                                  "Enum " + inst.args[0] + " was:" + "<br>" +
                                  str(inst.args[1]) + "<br>" +
                                  "Allowed range:" + "<br>" +
                                  "1 - " + str(inst.args[2]))
    except KeyedArrayKeyError as inst:
        return BadRequestError("Error in JSON:" + "<br>" +
                              "Missing key in list:" + "<br>" +
                              inst.args[0] + "<br>" +
                              "Received JSON:" + "<br>" +
                              json.dumps(inst.args[1]) + "<br>" +
                              "Key name:" + "<br>" +
                              inst.args[2])
    else:
        return existing_object


class NotFoundError(Response):
    def __init__(self, message):
        super(NotFoundError, self).__init__()
        self.status = '404 '+message
        self.status_code = 404
        self.headers = {'Content-Type': 'text/html'}
        self.data = '<h1>'+message+'</h1>'

class BadRequestError(Response):
    def __init__(self, message):
        super(BadRequestError, self).__init__()
        self.status = '400 '+message
        self.status_code = 400
        self.headers = {'Content-Type': 'text/html'}
        self.data = '<h1>'+message+'</h1>'

class Unauthorized(Response):
    def __init__(self, message):
        super(Unauthorized, self).__init__()
        self.status = '401 '+message
        self.status_code = 401
        self.headers = {'WWW-Authenticate','Basic realm="Auth example"'}
        self.data = '<h1>'+message+'</h1>'

class Successful(Response):
    def __init__(self, message, info=''):
        super(Successful, self).__init__()
        self.status = '200 '+message
        self.status_code = 200
        self.headers = {'Content-Type': 'application/json'}
        self.data = info


#/restconf/config/HVAC/
class HvacMethodView(MethodView):

    def put(self, ):
        print "Update operation of resource: HVAC"
        json_struct = request.get_json() #json parser.
        try:
            existing_object = HvacImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            new_object = create_instance(HVAC, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacImpl.put(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            existing_object = modify_instance(existing_object, json_struct)
            if isinstance(existing_object, BadRequestError):
                return existing_object
            elif isinstance(existing_object, NotFoundError):
                return existing_object
            else:
                try:
                    HvacImpl.put(existing_object)
                    js=existing_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")

        return Successful("Successful operation",json_dumps(js))



    def post(self, ):
        print "Create operation of resource: HVAC"
        try:
            response = HvacImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            json_struct = request.get_json() #json parser.
            new_object = create_instance(HVAC, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacImpl.post(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            return BadRequestError("Object already exists. For updates use PUT.")
        return Successful("Successful operation",json_dumps(js))


    def delete(self, ):
        print "Delete operation of resource: HVAC"
        try:
            response=HvacImpl.delete()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            return Successful('Successful operation')


    def get(self, ):
        print "Retrieve operation of resource: HVAC"
        try:
            response = HvacImpl.get()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            js = response.json_serializer()
            return Successful("Successful operation",json_dumps(js))


#/restconf/config/HVAC/Temperature/
class HvacTemperatureMethodView(MethodView):

    def put(self, ):
        print "Update operation of resource: Temperature"
        json_struct = request.get_json() #json parser.
        try:
            existing_object = HvacTemperatureImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            new_object = create_instance(Temperature, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacTemperatureImpl.put(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            existing_object = modify_instance(existing_object, json_struct)
            if isinstance(existing_object, BadRequestError):
                return existing_object
            elif isinstance(existing_object, NotFoundError):
                return existing_object
            else:
                try:
                    HvacTemperatureImpl.put(existing_object)
                    js=existing_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")

        return Successful("Successful operation",json_dumps(js))



    def post(self, ):
        print "Create operation of resource: Temperature"
        try:
            response = HvacTemperatureImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            json_struct = request.get_json() #json parser.
            new_object = create_instance(Temperature, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacTemperatureImpl.post(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            return BadRequestError("Object already exists. For updates use PUT.")
        return Successful("Successful operation",json_dumps(js))


    def delete(self, ):
        print "Delete operation of resource: Temperature"
        try:
            response=HvacTemperatureImpl.delete()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            return Successful('Successful operation')


    def get(self, ):
        print "Retrieve operation of resource: Temperature"
        try:
            response = HvacTemperatureImpl.get()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            js = response.json_serializer()
            return Successful("Successful operation",json_dumps(js))


#/restconf/config/HVAC/Ac/
class HvacAcMethodView(MethodView):

    def put(self, ):
        print "Update operation of resource: Ac"
        json_struct = request.get_json() #json parser.
        try:
            existing_object = HvacAcImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            new_object = create_instance(Ac, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacAcImpl.put(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            existing_object = modify_instance(existing_object, json_struct)
            if isinstance(existing_object, BadRequestError):
                return existing_object
            elif isinstance(existing_object, NotFoundError):
                return existing_object
            else:
                try:
                    HvacAcImpl.put(existing_object)
                    js=existing_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")

        return Successful("Successful operation",json_dumps(js))



    def post(self, ):
        print "Create operation of resource: Ac"
        try:
            response = HvacAcImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            json_struct = request.get_json() #json parser.
            new_object = create_instance(Ac, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacAcImpl.post(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            return BadRequestError("Object already exists. For updates use PUT.")
        return Successful("Successful operation",json_dumps(js))


    def delete(self, ):
        print "Delete operation of resource: Ac"
        try:
            response=HvacAcImpl.delete()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            return Successful('Successful operation')


    def get(self, ):
        print "Retrieve operation of resource: Ac"
        try:
            response = HvacAcImpl.get()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            js = response.json_serializer()
            return Successful("Successful operation",json_dumps(js))


#/restconf/config/HVAC/Heat/
class HvacHeatMethodView(MethodView):

    def put(self, ):
        print "Update operation of resource: Heat"
        json_struct = request.get_json() #json parser.
        try:
            existing_object = HvacHeatImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            new_object = create_instance(Heat, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacHeatImpl.put(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            existing_object = modify_instance(existing_object, json_struct)
            if isinstance(existing_object, BadRequestError):
                return existing_object
            elif isinstance(existing_object, NotFoundError):
                return existing_object
            else:
                try:
                    HvacHeatImpl.put(existing_object)
                    js=existing_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")

        return Successful("Successful operation",json_dumps(js))



    def post(self, ):
        print "Create operation of resource: Heat"
        try:
            response = HvacHeatImpl.get()
        except KeyError as inst:
            if inst.args[0] != '':
                return NotFoundError(inst.args[0] + " not found")

            json_struct = request.get_json() #json parser.
            new_object = create_instance(Heat, json_struct)
            if isinstance(new_object, BadRequestError):
                return new_object
            elif isinstance(new_object, NotFoundError):
                return new_object
            else:
                try:
                    HvacHeatImpl.post(new_object)
                    js=new_object.json_serializer()
                except KeyError as inst:
                    return NotFoundError(inst.args[0] + " not found")
        else:
            return BadRequestError("Object already exists. For updates use PUT.")
        return Successful("Successful operation",json_dumps(js))


    def delete(self, ):
        print "Delete operation of resource: Heat"
        try:
            response=HvacHeatImpl.delete()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            return Successful('Successful operation')


    def get(self, ):
        print "Retrieve operation of resource: Heat"
        try:
            response = HvacHeatImpl.get()
        except KeyError as inst:
            return NotFoundError(inst.args[0] + " not found")
        else:
            js = response.json_serializer()
            return Successful("Successful operation",json_dumps(js))



getattr(sys.modules[__name__], __name__).add_url_rule("/restconf/config/HVAC/", view_func = globals()["HvacMethodView"].as_view('"Hvac"'+'"_api"'), methods=['PUT', 'POST', 'DELETE', 'GET'])
getattr(sys.modules[__name__], __name__).add_url_rule("/restconf/config/HVAC/Temperature/", view_func = globals()["HvacTemperatureMethodView"].as_view('"HvacTemperature"'+'"_api"'), methods=['PUT', 'POST', 'DELETE', 'GET'])
getattr(sys.modules[__name__], __name__).add_url_rule("/restconf/config/HVAC/Ac/", view_func = globals()["HvacAcMethodView"].as_view('"HvacAc"'+'"_api"'), methods=['PUT', 'POST', 'DELETE', 'GET'])
getattr(sys.modules[__name__], __name__).add_url_rule("/restconf/config/HVAC/Heat/", view_func = globals()["HvacHeatMethodView"].as_view('"HvacHeat"'+'"_api"'), methods=['PUT', 'POST', 'DELETE', 'GET'])
