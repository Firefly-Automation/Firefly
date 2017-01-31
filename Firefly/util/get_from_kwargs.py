def get_kwargs_value(items, item, fallback=None):
  if items is None:
    return None
  return_value = items.get(item)
  if return_value is not None:
    return return_value
  return fallback
