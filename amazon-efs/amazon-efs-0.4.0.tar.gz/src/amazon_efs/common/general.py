def convert_tag_obj_to_tag_arr(tag_obj):
    if tag_obj is None:
        return []

    tag_set = []
    for key, value in tag_obj.items():
        tag_set.append({
            'Key': key,
            'Value': value
        })
    tags = tag_set

    return tags

