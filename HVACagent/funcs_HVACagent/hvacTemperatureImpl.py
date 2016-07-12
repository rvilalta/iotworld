import os.path, sys
sys.path.append(os.path.join('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])))
import backend.backend as be


class HvacTemperatureImpl:

    @classmethod
    def put(cls, temperature):
        print str(temperature)
        print 'handling put'
        be.HVAC = temperature

    @classmethod
    def post(cls, temperature):
        print str(temperature)
        print 'handling post'
        be.HVAC = temperature

    @classmethod
    def delete(cls, ):
        print 'handling delete'
        if be.HVAC:
            del be.HVAC
        else:
            raise KeyError('')

    @classmethod
    def get(cls, ):
        print 'handling get'
        if be.HVAC:
            return be.HVAC
        else:
            raise KeyError('')
