from objects_common.jsonObject import JsonObject

class Temperature(JsonObject):

    def __init__(self, json_struct=None):
        self.TempCentigrads=""
        super(Temperature, self).__init__(json_struct)

