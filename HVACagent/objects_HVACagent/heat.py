from objects_common.jsonObject import JsonObject
from objects_common.enumType import EnumType

class Heat(JsonObject):

    def __init__(self, json_struct=None):
        self.Status=Status(0)
        super(Heat, self).__init__(json_struct)

class Status(EnumType):
    possible_values = ['Stop', 'Run', 'Error']
    range_end = 3

    def __init__(self, initial_value):
        super(Status, self).__init__(initial_value)
