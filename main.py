import os
import struct
import threading
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import List, Optional, Sequence, Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pyModbusTCP.client import ModbusClient
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import config_parameters
from services.pdf_generation_service import print_db_to_pdf

# SQLAlchemy Setup
Base = declarative_base()

executor = ThreadPoolExecutor(max_workers=1)


class RegisterData(Base):
    __tablename__ = "register_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    register1 = Column(Float)
    register2 = Column(Float)
    register3 = Column(Float)
    register4 = Column(Float)
    register5 = Column(Float)
    register6 = Column(Float)
    register7 = Column(Float)
    register8 = Column(Float)
    register9 = Column(Float)
    register10 = Column(Float)
    register11 = Column(Float)


DATABASE_URL = "sqlite+aiosqlite:///./register_data.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Modbus Client Setup
c = ModbusClient(host=config_parameters.HOST_IP, port=config_parameters.PORT, auto_open=True)

app = FastAPI()
script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
template_dir = os.path.join(script_dir, "templates")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")
templates = Jinja2Templates(directory=template_dir)


# Background Modbus Polling
# async def modbus_client():
#     while True:
#         try:
#             regs_l = c.read_holding_registers(config_parameters.REG_ADDR, config_parameters.REG_NB)
#             print("Registers read:", regs_l)  # Log the raw register values
#
#             if regs_l:
#                 regs_float = []
#                 for i in range(0, len(regs_l), 2):
#                     mypack = struct.pack('>HH', regs_l[i + 1], regs_l[i])
#                     f = struct.unpack('>f', mypack)
#                     regs_float.append(f[0])
#                 print("Processed float values:", regs_float)  # Log the processed float values
#
#                 if int(regs_float[-1]) == 1:  # Check the condition for insertion
#                     print("Inserting data into the database:", regs_float)
#                     try:
#                         async with get_session() as session:
#                             data = RegisterData(
#                                 timestamp=time.ctime(),
#                                 register1=regs_float[0],
#                                 register2=regs_float[1],
#                                 register3=regs_float[2],
#                                 register4=regs_float[3],
#                                 register5=regs_float[4],
#                                 register6=regs_float[5],
#                                 register7=regs_float[6],
#                                 register8=regs_float[7],
#                                 register9=regs_float[8],
#                                 register10=regs_float[9],
#                                 register11=regs_float[10],
#                             )
#                             session.add(data)
#                             await session.commit()
#                             print("Data committed to the database.")
#                     except Exception as e:
#                         print(f"Error inserting data: {e}")
#             else:
#                 print("Read error: No data received from Modbus server.")
#         except Exception as e:
#             print(f"Error in Modbus client: {e}")
#
#         await asyncio.sleep(config_parameters.SLEEP_TIME)
#
#
# # Start Modbus client in background thread
# modbus_thread = threading.Thread(target=lambda: asyncio.run(modbus_client()), daemon=True)
# modbus_thread.start()
async def read_modbus_registers():
    loop = asyncio.get_event_loop()
    try:
        # Offload the blocking I/O call to a separate thread
        regs_l = await loop.run_in_executor(executor, c.read_holding_registers, config_parameters.REG_ADDR,
                                            config_parameters.REG_NB)
        print("Registers read:", regs_l)  # Log the raw register values
        return regs_l
    except Exception as e:
        print(f"Error reading Modbus registers: {e}")
        return


async def modbus_client():
    while True:
        try:
            regs_l = await read_modbus_registers()

            if regs_l:
                regs_float = []
                for i in range(0, len(regs_l), 2):
                    mypack = struct.pack('>HH', regs_l[i + 1], regs_l[i])
                    f = struct.unpack('>f', mypack)
                    regs_float.append(f[0])
                print("Processed float values:", regs_float)  # Log the processed float values

                if int(regs_float[-1]) == 1:  # Check the condition for insertion
                    print("Inserting data into the database:", regs_float)
                    try:
                        async with get_session() as session:
                            data = RegisterData(
                                timestamp=time.ctime(),
                                register1=regs_float[0],
                                register2=regs_float[1],
                                register3=regs_float[2],
                                register4=regs_float[3],
                                register5=regs_float[4],
                                register6=regs_float[5],
                                register7=regs_float[6],
                                register8=regs_float[7],
                                register9=regs_float[8],
                                register10=regs_float[9],
                                register11=regs_float[10],
                            )
                            session.add(data)
                            await session.commit()
                            print("Data committed to the database.")
                    except Exception as e:
                        print(f"Error inserting data: {e}")
            else:
                print("Read error: No data received from Modbus server.")

        except Exception as e:
            print(f"Error in Modbus client loop: {e}")

        await asyncio.sleep(config_parameters.SLEEP_TIME)


# API Endpoints
@app.get("/")
async def root():
    return RedirectResponse(url="/view")


class RegisterDataResponse(BaseModel):
    id: Optional[int]
    timestamp: str
    register1: Optional[float]
    register2: Optional[float]
    register3: Optional[float]
    register4: Optional[float]
    register5: Optional[float]
    register6: Optional[float]
    register7: Optional[float]
    register8: Optional[float]
    register9: Optional[float]
    register10: Optional[float]
    register11: Optional[float]


@app.get("/data", response_model=List[RegisterDataResponse])
async def get_data(session: AsyncSession = Depends(get_session)) -> Sequence[RegisterData]:
    async with session as session:
        stmt = select(RegisterData)
        result = await session.execute(stmt)
        data = result.scalars().all()
        print("Data retrieved from the database:", data)
        return data


@app.get("/view")
async def view_data(request: Request, session: AsyncSession = Depends(get_session)):
    async with session as session:
        result = await session.execute(select(RegisterData))
        data = result.scalars().all()
        return templates.TemplateResponse("view_data.html", {"request": request, "data": data})


@app.get("/report")
async def generate_report(
    filename: str,
    batch_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    async with session as session:
        if batch_id:
            result = await session.execute(
                select(RegisterData).filter(
                    RegisterData.register1 == float(batch_id)
                )
            )
            data = result.scalars().all()

            # Transform the data into a list of lists
            data_list = [
                [
                    item.id,
                    item.timestamp,
                    item.register1,
                    item.register2,
                    item.register3,
                    item.register4,
                    item.register5,
                    item.register6,
                    item.register7,
                    item.register8,
                    item.register9,
                    item.register10,
                    item.register11,
                ]
                for item in data
            ]

            return print_db_to_pdf(data_list, filename, '1')
        return RedirectResponse(url="/view")


@app.get("/del_file/{filename}")
async def delete_file(filename: str):
    if os.path.isfile(filename):
        os.remove(filename)
        return "File removed successfully"
    return RedirectResponse(url="/view")


@app.get("/del_batch")
async def delete_batch(batch_id: str, session: AsyncSession = Depends(get_session)):
    async with session as session:
        await session.execute(select(RegisterData).filter(RegisterData.register1 == float(batch_id)).delete())
        await session.commit()
        return RedirectResponse(url="/view")


@app.get("/del_all")
async def delete_all(session: AsyncSession = Depends(get_session)):
    async with session as session:
        await session.execute(select(RegisterData).delete())
        await session.commit()
        return RedirectResponse(url="/view")


@app.get("/filterData")
async def filter_data(
        request: Request,
        draw: int,
        start: int,
        length: int,
        search: str,
        order_column: int,
        order_dir: str,
        session: AsyncSession = Depends(get_session)
):
    async with session as session:
        columns = [
            "id", "timestamp", "register1", "register2", "register3",
            "register4", "register5", "register6", "register7",
            "register8", "register9", "register10", "register11"
        ]
        order_column_name = columns[order_column]

        query = select(RegisterData)

        if search:
            query = query.filter(RegisterData.register1 == float(search))

        if order_dir == "desc":
            query = query.order_by(getattr(RegisterData, order_column_name).desc())
        else:
            query = query.order_by(getattr(RegisterData, order_column_name))

        total_records = await session.execute(select(RegisterData))
        total_count = total_records.scalars()

        filtered = await session.execute(query.offset(start).limit(length))
        data = [
            [getattr(row, col) for col in columns]
            for row in filtered.scalars().all()
        ]

        return JSONResponse({
            "draw": draw,
            "recordsTotal": total_count,
            "recordsFiltered": len(data),
            "data": data
        })


# if __name__ == "__main__":
#     asyncio.run(create_db_and_tables())
#     asyncio.run(modbus_client())
#     uvicorn.run(app, host="0.0.0.0", port=8000)

async def main():
    # Run the create_db_and_tables function once
    await create_db_and_tables()
    # Run the modbus_client function, which has its own infinite loop
    await modbus_client()


def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Start the Uvicorn server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    # Run the asynchronous main function
    asyncio.run(main())
