# Espresso 

zero-dependency type-safe expression parser in python

## Rationale

This has been built as part of a [larger project](https://github.com/aadv1k/project-bombay) having type-safety out of the box eliminates the need for the caller to handle it, providing better [separation of concerns](https://en.wikipedia.org/wiki/Separation_of_concerns)

## Example

```python
from espresso.Context import Context

import random
import string

ctx = Context()

# Namespaces are automatically resolved. In this case, within the space random, integer would be defined
# functionally this is syntactic sugar, the namespaces are simply nested dictionaries
ctx.define_function(random.randint, ["random", "integer"], ["int", "int"])

# Variadic typing is also supported. The method will be passed an array of all the arguments (of a singular type)
ctx.define_function(random.choice, ["random", "oneOf"], ["*any"]) 
ctx.define_function(random.choice, ["random", "oneOfInteger"], ["*int"]) 
ctx.define_function(random.choice, ["random", "oneOfString"], ["*str"]) 

def random_string(length = 32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

# Optional typing, will pass None if not provided
ctx.define_function(random_string, ["random", "string"], ["str?"]) 

ctx.eval("random.integer(0, 10)")
```

## Integration and Usage

To see how espresso is integrated into a production SaaS, you can see the [YAML Resolver](https://github.com/aadv1k/project-bombay/tree/master/core/YAMLResolver.py) which defines a bunch of functions and handles errors.

```yaml
- id: random.string(32)
- first_name: person.firstName
- last_name: person.lastName
- age: random.integer(0, 32)
- plan: choices.oneOf("beta", "pro", "free")
```
