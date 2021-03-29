def get_data_with_callback(decorate_me, lat_lon_callback):
    def wrapper(*args, **kwargs):
        decorate_me(lat_lon_callback)  # Сама функция

    return wrapper
