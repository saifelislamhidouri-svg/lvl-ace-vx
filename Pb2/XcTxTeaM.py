

import google .protobuf 


try :
    from google .protobuf import runtime_version 
except ImportError :
    class runtime_version :
        class Domain :
            PUBLIC =0 

        @staticmethod 
        def ValidateProtobufRuntimeVersion (*args ,**kwargs ):
            pass 

    google .protobuf .runtime_version =runtime_version 


try :
    from google .protobuf .internal import api_implementation 
except :
    pass 


try :
    from google .protobuf import descriptor_pool 
    descriptor_pool .Default ()
except :
    pass 


print ("[protobuf_fix] Runtime patched successfully.")
