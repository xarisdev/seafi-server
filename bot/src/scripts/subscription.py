from ..models.subscription import SubscriptionCreate

def loads_params(text: str) -> SubscriptionCreate | None:
    raw_params = text.split("^")

    config = {}
    for item in raw_params:
        if not item.strip() or "create_sub" in item:
            continue

        if ':' in item:
            name, value = item.split(":", maxsplit=1)
            
            param_name = name.lower().strip()
            param_value = value.strip()

            if param_name == "amount":
                try: param_value = float(param_value)
                except: return None
                
            elif param_name == "duration_hours":
                try: param_value = int(param_value)
                except: return None

            config[param_name] = param_value

    try:
        subscription = SubscriptionCreate(**config)
        return subscription
    
    except:
        return None