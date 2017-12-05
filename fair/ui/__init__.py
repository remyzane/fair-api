

def adapter(view_func, sign='test'):
    from .doc import doc_ui
    if sign == 'doc':
        return doc_ui(view_func)
