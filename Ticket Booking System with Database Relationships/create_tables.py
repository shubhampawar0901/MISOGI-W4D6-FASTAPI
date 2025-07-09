from database import engine, Base
from models import Venue, Event, TicketType, Booking

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

# Show what tables were created
print("\nTables created:")
for table_name in Base.metadata.tables.keys():
    print(f"  - {table_name}")