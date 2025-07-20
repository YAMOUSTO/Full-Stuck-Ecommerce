# init_local_db.py (Corrected)

# We only need the 'database' module.
# It contains the 'engine' and the 'Base' we need.
import database
# We also need to import 'models' so that Python knows about your
# User, Product, etc. classes and can create tables for them.
import models

print("--- Initializing Local SQLite Database ---")
print("This will create all tables in 'local_dev.db'.")

try:
    # Get the engine from the database module. It will default to SQLite.
    engine = database.engine

    # Get the Base from the database module, where it is defined.
    # This is the corrected line.
    Base = database.Base

    # Create all tables that inherit from this Base.
    Base.metadata.create_all(bind=engine)

    print("\n✅ Success! Local database 'local_dev.db' is ready.")

except Exception as e:
    print(f"\n❌ An error occurred: {e}")