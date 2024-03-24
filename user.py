import sqlalchemy as sql
from sqlalchemy.ext.asyncio import create_async_engine
from typing import NamedTuple

engine = create_async_engine(
    "mysql+aiomysql://avnadmin:AVNS_xZcwleIEU8MCWe_lx1S@mysql-6781937-pelicoin.a.aivencloud.com:25375/pelicoin"
)

# engine = create_async_engine(
#     "postgresql+asyncpg://localhost/lucaslevine", connect_args={"password": "pelicoin"}
# )

# Users
userMetadata = sql.MetaData()

usersTable = sql.Table(
    "users",
    userMetadata,
    sql.Column("email", sql.Text),
    sql.Column("password", sql.Text),
    sql.Column("name", sql.Text),
    sql.Column("graduation", sql.Text),
    sql.Column("dorm", sql.Text),
    sql.Column("balances", sql.JSON),
    sql.Column("transactions", sql.JSON),
)

User = NamedTuple(
    "User",
    [
        ("email", str),
        ("password", str),
        ("name", str),
        ("graduation", str),
        ("dorm", str),
        ("balances", dict),
        ("transactions", list),
    ],
)

user = User(
    email="",
    password="",
    name="Test",
    graduation="2024",
    dorm="",
    balances={
        "current": {"cash": 0.0, "treasury": 0.0, "stocks": 0.0},
        "education": {"treasury": 0.0, "stocks": 0.0},
        "retirement": {"treasury": 0.0, "stocks": 0.0},
    },
    transactions=[
        {
            "balancesSnapshot": {
                "current": {"cash": 20.0, "treasury": 0.0, "stocks": 0.0},
                "education": {"treasury": 0.0, "stocks": 0.0},
                "retirement": {"treasury": 0.0, "stocks": 0.0},
            },
            "transaction": {
                "executer": "user",
                "reason": "transfer",
                "pelicoins": -20.0,
                "accountFrom": "current",
                "typeFrom": "cash",
                "accountTo": "current",
                "typeTo": "treasury",
            },
        },
        {
            "balancesSnapshot": {
                "current": {"cash": 0.0, "treasury": 20.0, "stocks": 0.0},
                "education": {"treasury": 0.0, "stocks": 0.0},
                "retirement": {"treasury": 0.0, "stocks": 0.0},
            },
            "transaction": {
                "executer": "admin",
                "reason": "event",
                "pelicoins": 100.0,
                "accountFrom": "",
                "typeFrom": "",
                "accountTo": "current",
                "typeTo": "cash",
            },
        },
    ],
)


async def insertUser(user: User) -> None:
    insertStatement = usersTable.insert().values(**user._asdict())

    async with engine.connect() as conn:
        await conn.execute(insertStatement)
        await conn.commit()


async def deleteGradYear(gradYear: int):
    deleteStatement = usersTable.delete().where(usersTable.c.graduation == gradYear)

    async with engine.connect() as conn:
        await conn.execute(deleteStatement)
        await conn.commit()


async def deleteUserByEmail(email: str):
    deleteStatement = usersTable.delete().where(usersTable.c.email == email)

    async with engine.connect() as conn:
        await conn.execute(deleteStatement)
        await conn.commit()


Transaction = NamedTuple(
    "Transaction",
    [
        ("balancesSnapshot", dict),
        ("executer", str),
        ("reason", str),
        ("pelicoins", float),
        ("accountFrom", str),
        ("typeFrom", str),
        ("accountTo", str),
        ("typeTo", str),
    ],
)

transaction = Transaction(
    balancesSnapshot={
        "current": {"cash": 0.0, "treasury": 0.0, "stocks": 0.0},
        "education": {"treasury": 0.0, "stocks": 0.0},
        "retirement": {"treasury": 0.0, "stocks": 0.0},
    },
    executer="user",
    reason="transfer",
    pelicoins=-20.00,
    accountFrom="current",
    typeFrom="cash",
    accountTo="current",
    typeTo="treasury",
)


def transactionToJson(transaction: Transaction) -> dict:
    return {
        "balancesSnapshot": transaction.balancesSnapshot,
        "transaction": {
            "executer": transaction.executer,
            "reason": transaction.reason,
            "pelicoins": transaction.pelicoins,
            "accountFrom": transaction.accountFrom,
            "typeFrom": transaction.typeFrom,
            "accountTo": transaction.accountTo,
            "typeTo": transaction.typeTo,
        },
    }


async def setBalance(
    email: str,
    balance: float,
    account: str,
    accountType: str,
    *_,
    executer: str = "",
    reason: str = ""
):
    user = await fetchUserByEmail(email)

    if not User:
        return

    user.balances[account][accountType] = balance

    transaction = Transaction(
        user.balances, executer, reason, balance, "SET", "SET", account, accountType
    )
    user.transactions.append(transactionToJson(transaction))

    updateStatement = (
        usersTable.update()
        .where(usersTable.c.email == email)
        .values(balances=user.balances, transactions=user.transactions)
    )

    async with engine.connect() as conn:
        await conn.execute(updateStatement)
        await conn.commit()


async def depositToBalance(
    email: str,
    balance: float,
    account: str,
    accountType: str,
    *_,
    executer: str = "",
    reason: str = ""
):
    user = await fetchUserByEmail(email)

    if not User:
        return

    user.balances[account][accountType] += balance

    transaction = Transaction(
        user.balances,
        executer,
        reason,
        balance,
        "INFUSION",
        "INFUSION",
        account,
        accountType,
    )
    user.transactions.append(transactionToJson(transaction))

    updateStatement = (
        usersTable.update()
        .where(usersTable.c.email == email)
        .values(balances=user.balances, transactions=user.transactions)
    )

    async with engine.connect() as conn:
        await conn.execute(updateStatement)
        await conn.commit()


async def yieldToBalance(
    email: str,
    percent: float,
    account: str,
    accountType: str,
    *_,
    executer: str = "",
    reason: str = ""
):
    user = await fetchUserByEmail(email)

    if not User:
        return

    gained = user.balances[account][accountType] * (percent / 100)

    user.balances[account][accountType] *= 1 + percent / 100

    transaction = Transaction(
        user.balances,
        executer,
        reason,
        gained,
        "INFUSION",
        "INFUSION",
        account,
        accountType,
    )
    user.transactions.append(transactionToJson(transaction))

    updateStatement = (
        usersTable.update()
        .where(usersTable.c.email == email)
        .values(balances=user.balances, transactions=user.transactions)
    )

    async with engine.connect() as conn:
        await conn.execute(updateStatement)
        await conn.commit()


async def fetchUsers() -> list[User]:
    fetchStatement = usersTable.select()

    engine.connect()

    async with engine.connect() as conn:
        result = await conn.execute(fetchStatement)
        rows = result.fetchall()

    return [User(*row) for row in rows]


async def fetchUserByEmail(email: str) -> User | None:
    fetchStatement = usersTable.select().where(usersTable.c.email == email)

    async with engine.connect() as conn:
        result = await conn.execute(fetchStatement)
        row = result.fetchone()

        return User(*row) if row else None


async def authenticateUserLogin(email: str, password: str) -> bool:
    user = await fetchUserByEmail(email)

    return user.password == password if user else False


# Admins
adminMetadata = sql.MetaData()

adminsTable = sql.Table(
    "admins",
    adminMetadata,
    sql.Column("email", sql.Text),
    sql.Column("password", sql.Text),
    sql.Column("name", sql.Text),
)

Admin = NamedTuple(
    "Admin",
    [
        ("email", str),
        ("password", str),
        ("name", str),
    ],
)

admin = Admin(
    "",
    "",
    "Test",
)


async def insertAdmin(admin: Admin) -> None:
    insertStatement = adminsTable.insert().values(**admin._asdict())

    async with engine.connect() as conn:
        await conn.execute(insertStatement)
        await conn.commit()


async def fetchAdmins() -> list[Admin]:
    fetchStatement = adminsTable.select()

    async with engine.connect() as conn:
        result = await conn.execute(fetchStatement)
        rows = result.fetchall()

    return [Admin(*row) for row in rows]


async def fetchAdminByEmail(email: str) -> Admin | None:
    fetchStatement = adminsTable.select().where(adminsTable.c.email == email)

    async with engine.connect() as conn:
        result = await conn.execute(fetchStatement)
        row = result.fetchone()

        return Admin(*row) if row else None


async def authenticateAdminLogin(email: str, password: str) -> bool:
    admin = await fetchAdminByEmail(email)

    return admin.password == password if admin else False


# syncengine = sql.create_engine(
#     "mysql+pymysql://avnadmin:AVNS_xZcwleIEU8MCWe_lx1S@mysql-6781937-pelicoin.a.aivencloud.com:25375/pelicoin"
# )


# userMetadata.create_all(syncengine)
# adminMetadata.create_all(syncengine)
