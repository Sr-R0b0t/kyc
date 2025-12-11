def merge_kyc_data(data_list):
    """
    Junta dados de várias páginas, priorizando valores não vazios.
    """
    merged = {}

    for data in data_list:
        for key, value in data.items():
            if value and not merged.get(key):
                merged[key] = value

    return merged
