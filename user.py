import sqlalchemy as sql
from typing import NamedTuple

engine = sql.create_engine("sqlite:///data/test.db")

# Users
userMetadata = sql.MetaData()

usersTable = sql.Table(
    "users",
    userMetadata,
    sql.Column("email", sql.Text),
    sql.Column("password", sql.Text),
    sql.Column("name", sql.Text),
    sql.Column("gradYear", sql.Integer),
    sql.Column("dorm", sql.Text),
    sql.Column("balances", sql.JSON),
)

User = NamedTuple(
    "User",
    [
        ("email", str),
        ("password", str),
        ("name", str),
        ("dorm", str),
        ("gradYear", int),
        ("balances", dict),
    ],
)

# user = User(
#     "test@loomis.org",
#     "",
#     "Test",
#     "",
#     2024,
#     {
#         "current": {"cash": 0.0, "treasury": 0.0, "stocks": 0.0},
#         "education": {"treasury": 0.0, "stocks": 0.0},
#         "retirement": {"treasury": 0.0, "stocks": 0.0},
#     },
# )


# write
def insertUser(user: User) -> None:
    insertStatement = usersTable.insert().values(**user._asdict())

    with engine.connect() as conn:
        conn.execute(insertStatement)
        conn.commit()


def deleteGradYear(gradYear: int):
    deleteStatement = usersTable.delete().where(usersTable.c.gradYear == gradYear)

    with engine.connect() as conn:
        conn.execute(deleteStatement)
        conn.commit()


def deleteUserByEmail(email: str):
    deleteStatement = usersTable.delete().where(usersTable.c.email == email)

    with engine.connect() as conn:
        conn.execute(deleteStatement)
        conn.commit()


def setBalance(email: str, balance: float, account: str, accountType: str):
    user = fetchUserByEmail(email)

    if not User:
        return

    user.balances[account][accountType] = balance

    updateStatement = (
        usersTable.update()
        .where(usersTable.c.email == email)
        .values(balances=user.balances)
    )

    with engine.connect() as conn:
        conn.execute(updateStatement)
        conn.commit()


def depositToBalance(email: str, balance: float, account: str, accountType: str):
    user = fetchUserByEmail(email)

    if not User:
        return

    user.balances[account][accountType] += balance

    updateStatement = (
        usersTable.update()
        .where(usersTable.c.email == email)
        .values(balances=user.balances)
    )

    with engine.connect() as conn:
        conn.execute(updateStatement)
        conn.commit()


def yieldToBalance(email: str, percent: float, account: str, accountType: str):
    user = fetchUserByEmail(email)

    if not User:
        return

    user.balances[account][accountType] *= 1 + percent / 100

    updateStatement = (
        usersTable.update()
        .where(usersTable.c.email == email)
        .values(balances=user.balances)
    )

    with engine.connect() as conn:
        conn.execute(updateStatement)
        conn.commit()


# read
def fetchUsers() -> list[User]:
    fetchStatement = usersTable.select()

    with engine.connect() as conn:
        result = conn.execute(fetchStatement)
        rows = result.fetchall()

    return [User(*row) for row in rows]


def fetchUserByEmail(email: str) -> User | None:
    fetchStatement = usersTable.select().where(usersTable.c.email == email)

    with engine.connect() as conn:
        result = conn.execute(fetchStatement)
        row = result.fetchone()

        return User(*row) if row else None


def authenticateLogin(email: str, password: str) -> bool:
    user = fetchUserByEmail(email)

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

# admin = Admin(
#     "test@loomis.org",
#     "",
#     "Test",
# )


def insertAdmin(admin: Admin) -> None:
    insertStatement = adminsTable.insert().values(**admin._asdict())

    with engine.connect() as conn:
        conn.execute(insertStatement)
        conn.commit()


def fetchAdmins() -> list[Admin]:
    fetchStatement = adminsTable.select()

    with engine.connect() as conn:
        result = conn.execute(fetchStatement)
        rows = result.fetchall()

    return [Admin(*row) for row in rows]


def fetchAdminByEmail(email: str) -> Admin | None:
    fetchStatement = adminsTable.select().where(adminsTable.c.email == email)

    with engine.connect() as conn:
        result = conn.execute(fetchStatement)
        row = result.fetchone()

        return Admin(*row) if row else None


def authenticateLogin(email: str, password: str) -> bool:
    admin = fetchAdminByEmail(email)

    return admin.password == password if admin else False
