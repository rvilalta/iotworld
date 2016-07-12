from objects_common.jsonObject import JsonObject
from ac import Ac
from heat import Heat
from temperature import Temperature

class HVAC(JsonObject):

    def __init__(self, json_struct=None):
        self.Ac=Ac() #import
        self.Heat=Heat() #import
        self.Temperature=Temperature() #import
        super(HVAC, self).__init__(json_struct)

