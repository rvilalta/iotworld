import os.path, sys
sys.path.append(os.path.join('/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])))
import backend.backend as be


class HvacImpl:

    @classmethod
    def put(cls, hvac):
        print str(hvac)
        print 'handling put'
        be.HVAC = hvac

    @classmethod
    def post(cls, hvac):
        print str(hvac)
        print 'handling post'
        be.HVAC = hvac

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
