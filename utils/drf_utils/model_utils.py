def get_obj_child_ids(parent: int, models_class_name, ids: set):
    """
    获取models模型的子id集合
    :param parent: models模型类ID
    :param models_class_name: models模型对象类
    :param ids: 默认为空集合
    """
    objs = models_class_name.objects.filter(parent=parent)
    for obj in objs:
        ids.add(obj.id)
        get_obj_child_ids(obj.id, models_class_name, ids)


def get_user_permissions(user_obj):
    """
    获取用户对象所拥有的所有API权限
    @param user_obj:
    @return:
    """
    role_list = user_obj.roles.all()
    request_api_permissions = list()
    for role in role_list:
        permission_list = role.permissions.all()
        for permission in permission_list:
            # 去重
            permission_data = {
                'method': permission.method,
                'url_path': permission.url_path
            }
            if permission_data not in request_api_permissions:
                request_api_permissions.append(permission_data)
    return request_api_permissions


def generate_object_tree_data(p_serializer_data):
    tree_dict = {}
    tree_data = []
    try:
        for item in p_serializer_data:
            tree_dict[item['id']] = item
        for item_id in tree_dict:
            if tree_dict.get(item_id).get('parent'):
                pid = tree_dict.get(item_id).get('parent')
                # 父权限的完整数据
                parent_data = tree_dict.get(pid)
                # 如果有children就直接追加数据，没有则添加children并设置默认值为[]，然后追加数据
                parent_data.setdefault('children', []).append(tree_dict.get(item_id))
            else:
                # item没有parent, 放在最顶层
                tree_data.append(tree_dict.get(item_id))
        data = {
            'count': len(tree_data),
            'next': None,
            'previous': None,
            'results': tree_data,
            'total_pages': None,
            'current_page': None,
        }

        return data
    except Exception:
        return []

