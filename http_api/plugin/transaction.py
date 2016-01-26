# from .configure import db
# database = 'default'        # used by auto_rollback
# db = None
# auto_rollback = True       # auto rollback the current transaction while result code != success

# setting database
# cls.db = db.get(cls.database)

# rollback the current transaction while result code != success
# if self.auto_rollback:
#     with self.db.transaction():
#         return self.dispatch_request(*args, **kwargs)
# else:
#     return self.dispatch_request(*args, **kwargs)


# rollback the current transaction
# if self.auto_rollback and code != 'success':
#     self.db.rollback()
