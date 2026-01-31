from sqlmodel import Field, SQLModel, BigInteger

class EventLink(SQLModel, table=True):
    google_id: str = Field(primary_key=True)
    discord_id: int = Field(primary_key=True, sa_type=BigInteger)

class Calendar(SQLModel, table=True):
    google_id: str = Field(primary_key=True)
    discord_id: int = Field(primary_key=True, sa_type=BigInteger)
    channel_id: int | None = Field(None, sa_type=BigInteger)
    
