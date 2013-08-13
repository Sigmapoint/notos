'''
Created on 25-07-2013

@author: kamil
'''    
def push_with_policy(policy_class):
    def decorator(klass):
        old_finalize_response = klass.finalize_response
        def method(_self, request, response, *args, **kwargs):
            response = old_finalize_response(_self, request, response, *args, **kwargs)
            policy = (policy_class(_self, request, response))
            policy.trigger()
            return response
        klass.finalize_response = method
        return klass
    return decorator