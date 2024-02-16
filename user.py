import _sqlite3 as sqlite3

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
        currentCash: float,
        currentTreasuryBills: float,
        currentStockIndex: float,
        educationTreasuryBills: float,
        educationStockIndex: float,
        retirementTreasuryBills: float,
        retirementStockIndex: float,
        name: str,
        gradYear: int,
        isBoarder: int,
        dorm: str,
    ) -> None:
        super().__init__(email, password)
        self.name = name
        self.gradYear = gradYear
        self.isBoarder = isBoarder
        self.dorm = dorm
        self.current = {
            "cash": currentCash,
            "treasuryBills": currentTreasuryBills,
            "stockIndex": currentStockIndex,
        }
        self.education = {
            "treasuryBills": educationTreasuryBills,
            "stockIndex": educationStockIndex,
        }
        self.retirement = {
            "treasuryBills": retirementTreasuryBills,
            "stockIndex": retirementStockIndex,
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


def openConnection():
    connection = sqlite3.connect("assets/data/users.db")
    cursor = connection.cursor()
    return connection, cursor


def closeConnection(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.close()
    connection.close()


def fetchUsers() -> list[User]:
    connection, cursor = openConnection()
    rows = cursor.execute("SELECT * FROM users").fetchall()
    closeConnection(connection, cursor)
    return [User(*row) for row in rows]


def fetchUserByEmail(email: str) -> User | None:
    connection, cursor = openConnection()
    sqlSelectUser = "SELECT * FROM users WHERE email = ?"
    rows = cursor.execute(sqlSelectUser, (email,)).fetchall()
    closeConnection(connection, cursor)
    if rows:
        return User(*rows[0]) if rows else None


def fetchUserBalances(user: User) -> tuple:
    connection, cursor = openConnection()
    sqlSelectBalances = "SELECT currentCash, currentTreasuryBills, currentStockIndex, educationTreasuryBills, educationStockIndex, retirementTreasuryBills, retirementStockIndex FROM users WHERE email = ?"
    rows = cursor.execute(sqlSelectBalances, (user.email,)).fetchall()
    closeConnection(connection, cursor)
    return rows[0]


def fetchAccountsDict() -> dict[str, str]:
    connection, cursor = openConnection()
    rows = cursor.execute("SELECT email, password FROM users").fetchall()
    closeConnection(connection, cursor)
    return dict(rows)


def isValidUserLogin(account: Account) -> bool:
    connection, cursor = openConnection()
    selectPassword = "SELECT password FROM users WHERE email = ?"
    userPassword = cursor.execute(selectPassword, (account.email,)).fetchall()
    closeConnection(connection, cursor)
    try:
        return account.password == userPassword[0][0]
    except IndexError:
        return False


def appendUser(user: User):
    connection, cursor = openConnection()
    sqlInsert = f"INSERT INTO users VALUES ('{user.email}', '{user.password}', '{user.name}', {user.gradYear}, {user.isBoarder}, '{user.dorm}', {user.current['cash']}, {user.current['treasuryBills']}, {user.current['stockIndex']}, {user.education['treasuryBills']}, {user.education['stockIndex']}, {user.retirement['treasuryBills']}, {user.retirement['stockIndex']})"
    cursor.execute(sqlInsert)
    connection.commit()
    closeConnection(connection, cursor)


def transferCoins(user: User, pelicoins: float, fromAccount: str, toAccount: str):
    depositToUserBalance(user, -pelicoins, fromAccount)
    depositToUserBalance(user, pelicoins, toAccount)


def depositToUserBalance(user: User, pelicoins: float, accountType: str):
    currentUserBalances = fetchUserBalances(user)
    currentChecking, currentSavings = currentUserBalances

    typeToBalance = {"checking": currentChecking, "savings": currentSavings}

    connection, cursor = openConnection()
    sqlUpdateBalance = f"UPDATE users SET {accountType} = ? WHERE email = ?"
    cursor.execute(
        sqlUpdateBalance,
        (typeToBalance.get(accountType) + pelicoins, user.email),
    )
    connection.commit()
    closeConnection(connection, cursor)
