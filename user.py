import sqlite3 as sqlite3

# connection = sqlite3.connect("assets/data/users.db")
# cursor = connection.cursor()
# sqlCreateTable = "CREATE TABLE users (email TEXT, password TEXT, checking REAL, savings REAL, name TEXT, gradYear INTEGER, isBoarder INTEGER, dorm TEXT)"
# cursor.execute(sqlCreateTable)


class Account:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password

    def __repr__(self) -> str:
        return f"Account: {self.email}, {self.password}"


class User(Account):
    def __init__(
        self,
        email: str,
        password: str,
        name: str,
        gradYear: int,
        isBoarder: int,
        dorm: str,
        currentCash: float,
        currentTreasuryBills: float,
        currentStockIndex: float,
        educationTreasuryBills: float,
        educationStockIndex: float,
        retirementTreasuryBills: float,
        retirementStockIndex: float,
    ) -> None:
        super().__init__(email, password)
        self.name = name
        self.gradYear = gradYear
        self.isBoarder = isBoarder
        self.dorm = dorm
        self.current = {
            "Cash": currentCash,
            "Treasury Bills": currentTreasuryBills,
            "Index Fund": currentStockIndex,
        }
        self.education = {
            "Treasury Bills": educationTreasuryBills,
            "Index Fund": educationStockIndex,
        }
        self.retirement = {
            "Treasury Bills": retirementTreasuryBills,
            "Index Fund": retirementStockIndex,
        }

    def __repr__(self) -> str:
        return f"Account: {self.email, self.password} || User: {self.name} ({self.gradYear}), {'Boarder' if self.isBoarder else 'Day'} in {self.dorm}"


class Admin(Account):
    def __init__(
        self,
        email: str,
        password: str,
        name: str,
    ) -> None:
        super().__init__(email, password)
        self.name = name


# USER


def openUsersConnection():
    connection = sqlite3.connect("data/users.db")
    cursor = connection.cursor()
    return connection, cursor


def closeConnection(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.close()
    connection.close()


def fetchUsers() -> list[User]:
    connection, cursor = openUsersConnection()
    rows = cursor.execute("SELECT * FROM users").fetchall()
    closeConnection(connection, cursor)
    return [User(*row) for row in rows]


def fetchUserByEmail(email: str) -> User | None:
    connection, cursor = openUsersConnection()
    sqlSelectUser = "SELECT * FROM users WHERE email = ?"
    rows = cursor.execute(sqlSelectUser, (email,)).fetchall()
    closeConnection(connection, cursor)
    if rows:
        return User(*rows[0]) if rows else None


def fetchAccountsDict() -> dict[str, str]:
    connection, cursor = openUsersConnection()
    rows = cursor.execute("SELECT email, password FROM users").fetchall()
    closeConnection(connection, cursor)
    return dict(rows)


def isValidUserLogin(account: Account) -> bool:
    connection, cursor = openUsersConnection()
    selectPassword = "SELECT password FROM users WHERE email = ?"
    userPassword = cursor.execute(selectPassword, (account.email,)).fetchall()
    closeConnection(connection, cursor)
    try:
        return account.password == userPassword[0][0]
    except IndexError:
        return False


def appendUser(user: User):
    connection, cursor = openUsersConnection()
    sqlInsert = f"INSERT INTO users VALUES ('{user.email}', '{user.password}', '{user.name}', {user.gradYear}, {user.isBoarder}, '{user.dorm}', {user.current['Cash']}, {user.current['Treasury Bills']}, {user.current['Index Fund']}, {user.education['Treasury Bills']}, {user.education['Index Fund']}, {user.retirement['Treasury Bills']}, {user.retirement['Index Fund']})"
    cursor.execute(sqlInsert)
    connection.commit()
    closeConnection(connection, cursor)


def purgeClassYear(classYear: int):
    connection, cursor = openUsersConnection()
    sqlDelete = f"DELETE FROM users WHERE gradYear = {classYear};"
    cursor.execute(sqlDelete)
    connection.commit()
    closeConnection(connection, cursor)


def setBalance(email: str, pelicoins: float, account: str, accountType: str):
    fieldName = f"{account.lower()}{accountType.replace(' ', '')}"

    connection, cursor = openUsersConnection()
    sqlUpdateBalance = f"UPDATE users SET {fieldName} = ? WHERE email = ?"
    cursor.execute(
        sqlUpdateBalance,
        (
            pelicoins,
            email,
        ),
    )
    connection.commit()
    closeConnection(connection, cursor)


def depositToBalance(email: str, pelicoins: float, account: str, accountType: str):
    currentUser = fetchUserByEmail(email)

    fieldName = f"{account.lower()}{accountType.replace(' ', '')}"

    connection, cursor = openUsersConnection()
    sqlUpdateBalance = f"UPDATE users SET {fieldName} = ? WHERE email = ?"
    cursor.execute(
        sqlUpdateBalance,
        (
            currentUser.__getattribute__(account.lower()).get(accountType) + pelicoins,
            currentUser.email,
        ),
    )
    connection.commit()
    closeConnection(connection, cursor)


# ADMIN


def openAdminsConnection():
    connection = sqlite3.connect("data/admins.db")
    cursor = connection.cursor()
    return connection, cursor


def fetchAdminByEmail(email: str) -> Admin | None:
    connection, cursor = openAdminsConnection()
    sqlSelectAdmin = "SELECT * FROM admins WHERE email = ?"
    rows = cursor.execute(sqlSelectAdmin, (email,)).fetchall()
    closeConnection(connection, cursor)
    if rows:
        return Admin(*rows[0]) if rows else None


def isValidAdminLogin(account: Account) -> bool:
    connection, cursor = openAdminsConnection()
    selectPassword = "SELECT password FROM admins WHERE email = ?"
    adminPassword = cursor.execute(selectPassword, (account.email,)).fetchall()
    closeConnection(connection, cursor)
    try:
        return account.password == adminPassword[0][0]
    except IndexError:
        return False
