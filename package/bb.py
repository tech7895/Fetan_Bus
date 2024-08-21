def parse(facts):
    
    store = {}
    left, right = facts.split("=")
    left_value, left_unit = left.strip().split()
    right_value, right_unit = right.strip().split()
    
    left_value = float(left_value)
    right_value = float(right_value)
    
    store[left_unit] = {}
    store[right_unit] = {}
    
    store[left_unit][right_unit] = right_value/left_value
    store[right_unit][left_unit] = left_value/right_value
    
    return store


print(parse("1 m = 100 cm"))