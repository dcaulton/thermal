from flask import current_app

def get_documents_from_criteria(args_dict):
    documents_dict = {}
    criteria_list = []
    for key in args_dict:
        criteria_list.append("doc.{0} == '{1}'".format(key, args_dict[key]))
    criteria_string = ' && '.join(criteria_list)
    map_fun = "function(doc) {{if ("
    map_fun = map_fun + criteria_string
    map_fun = map_fun + ") {{emit(doc._id, doc);}}}}"
    for row in current_app.db.query(map_fun).rows:
        documents_dict[row['key']] = row['value']
    return documents_dict
