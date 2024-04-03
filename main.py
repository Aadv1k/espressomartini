from espresso.Parser import Parser, StackFrame
from espresso.Lexer import Lexer
from espresso.utils import Stack

from typing import NamedTuple, List, Union

class Func(NamedTuple):
    func_call: callable
    func_name: List[str]
    func_argument_types: List[str]

class Evaluator:
    def __init__(self) -> None:
        self.namespace = {}

    def get_function(self, func_name: Union[List[str], str]) -> Func:
        func_call_chain = func_name if isinstance(type(func_name), list) else func_name.split(".")
        final_func = None
        for call in func_call_chain:
            final_func =  self.namespace.get(call)

        if not final_func:
            raise NameError("Function \"{}\" is not defined in Namespace \"{}\"".format(func_call_chain[-1], ".".join(func_call_chain[:-1])))
            
        return final_func

    def define_function(self, f: Func):
        def_space = self.namespace
        for name in f.func_name[:-1]:
            def_space = self.namespace.setdefault(name, {})

        def_space[f.func_name[-1]] = f

    def is_variadic(self, func: Func, params: List[Union[str, int]]):
        return len(func.func_argument_types) > 0 and func.func_argument_types[0].startswith("*"):

    def get_typed_params(self, func: Func, params: List[Union[str, int]]):
        param_types = func.func_argument_types
        parsed_params = []

        if self.is_variadic(func, params):
            param_types = [param_types[0][1:]] * len(param_types)

        for i, param_type in enumerate(param_types):
            if param_type.endswith("?") and not params[i]:
                parsed_params.append(None)
                continue

            if param_type.startswith("str") and not isinstance(params[i], str):
                raise Exception("PROPER ERROR MESSAGE HERE")
            elif param_type.startswith("int") and not isinstance(params[i], int):
                raise Exception("PROPER ERROR MESSAGE HERE")
            elif param_type.startswith("any"): # simply ignore and push
                pass
            else:
                raise Exception("UNKNOWN PARAM TYPE LOL")
            
            parsed_params.append(params[i])

        return parsed_params
            

            

    def is_variadic(self) -> bool:
        pass

    def _eval_stack_frame(self, frame: StackFrame):
        func_def = self.get_function(frame.func_chain)
        func_params = []

        for func_param in frame.func_params:
            if isinstance(func_param, StackFrame):
                self._eval_stack_frame(func_param)
            elif isinstance(func_param, int) or isinstance(func_param, str):
                func_params.append(func_param)
            else:
                assert False, "_eval_stack_frame: Undefined stack param type {}".format(type(func_param))
        
        typed_params = self.get_typed_params(func_def, func_params)
        is_variadic = self.is_variadic(func_def, func_params)
        
        if is_variadic:
            return func_def.func_call(*typed_params)
        else:
            return func_def.func_call(typed_params)

    def eval(self, call_stack: Stack) -> any:
        pass

s = "foo.bar()"

evaluator = Evaluator() 

evaluator.define_function(Func(lambda: 1 + 2, ["foo", "bar"], []))

# evaluator.eval(Parser().parse(Lexer().lex(s)))
