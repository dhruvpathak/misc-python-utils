#__author__ = 'dhruv pathak'
# Borg Pattern can be used to create 'singleton' objects which share the state,
# This modification enables achieving singleton pattern for parameters based objects i.e.
# objects of a class created with same parameters will share the same state

 

    import random
    import cPickle
    
    class Borg:
        __shared_state = { }
    
        def __init__(self,*args,**kwargs):
            context_key = hash('{0}{1}'.format(cPickle.dumps(args),cPickle.dumps(kwargs)))
            self.__shared_state.setdefault(context_key, {})
            self.__dict__ = self.__shared_state[context_key]
            print(self.__shared_state)
    
        def set_random_property(self):
            self.num =  str(random.randint(1,100000))
    
    
    
    a = Borg(x='ONE')
    a.set_random_property()
    b = Borg(x = 'TWO')
    b.set_random_property()
    c = Borg(x = 'TWO')
    print('a with ONE has num:{0}'.format(a.num))
    print('b with TWO has num:{0}'.format(b.num))
    print('c with TWO has num:{0}'.format(c.num))

#output

#    {7373348246660160089: {}}
#    {7373348246660160089: {'num': '18322'}, 3334843421982509183: {}}
#    {7373348246660160089: {'num': '18322'}, 3334843421982509183: {'num': '33084'}}
#    a with ONE has num:18322
#    b with TWO has num:33084
#    c with TWO has num:33084


            
