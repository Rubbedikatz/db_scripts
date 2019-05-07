from PythonScripts.base import engine, Base

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
for i in Base.metadata.sorted_tables:
    print("Created table %s" % i.name)