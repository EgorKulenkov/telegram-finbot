from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import Float, BigInteger, String, DateTime
from datetime import datetime

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class AllFinance(Base):
    __tablename__ = 'expenses' 
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    all_finance: Mapped[float] = mapped_column(Float)
    date: Mapped[datetime] = mapped_column(DateTime)


class MinusFin(Base):
    __tablename__ = 'MinFin'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    minus_fin: Mapped[float] = mapped_column(Float)
    description_minus: Mapped[String] = mapped_column(String(30))
    date: Mapped[datetime] = mapped_column(DateTime)

class PlusFin(Base):
    __tablename__ = 'PluFin'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    plus_fin: Mapped[float] = mapped_column(Float)
    description_plus: Mapped[String] = mapped_column(String(30))
    date: Mapped[datetime] = mapped_column(DateTime)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
