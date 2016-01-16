from flask import current_app

def get_documents_from_criteria(args_dict, **kwargs):
    documents_dict = {}
    criteria_list = []
    if 'gallery_url_not_null' in kwargs:
        criteria_list.append("doc.gallery_url != null")
    for key in args_dict:
        criteria_list.append("doc.{0} == '{1}'".format(key, args_dict[key]))
    criteria_string = ' && '.join(criteria_list)
    map_fun = "function(doc) {{if ("
    map_fun = map_fun + criteria_string
    map_fun = map_fun + ") {{emit(doc._id, doc);}}}}"
    for row in current_app.db.query(map_fun).rows:
        documents_dict[row['key']] = row['value']
    return documents_dict
