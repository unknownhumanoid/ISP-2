import flet as ft
import sqlite3

FIELD_WIDTH = 325
MAIN_BUTTON_WIDTH = 150
SECONDARY_BUTTON_WIDTH = 100

TextFieldStyle = ft.TextStyle(
    font_family="Kayak Light", size=18, weight=ft.FontWeight.NORMAL
)

ChartTitleStyle = ft.TextStyle(
    size=12, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD
)


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
        self.currentCash = currentCash
        self.currentTreasuryBills = currentTreasuryBills
        self.currentStockIndex = currentStockIndex
        self.educationTreasuryBills = educationTreasuryBills
        self.educationStockIndex = educationStockIndex
        self.retirementTreasuryBills = retirementTreasuryBills
        self.retirementStockIndex = retirementStockIndex
        self.name = name
        self.gradYear = gradYear
        self.isBoarder = isBoarder
        self.dorm = dorm

    def __repr__(self) -> str:
        return f"Account: {self.email, self.password} || User: {self.name} ({self.gradYear}), {'Boarder' if self.isBoarder else 'Day'} in {self.dorm}"


def openConnection():
    connection = sqlite3.connect("assets/data/users.db")
    cursor = connection.cursor()
    return connection, cursor


def closeConnection(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.close
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
    sqlInsert = f"INSERT INTO users VALUES ('{user.email}', '{user.password}', '{user.name}', {user.gradYear}, {user.isBoarder}, '{user.dorm}', {user.currentCash}, {user.currentTreasuryBills}, {user.currentStockIndex}, {user.educationTreasuryBills}, {user.educationStockIndex}, {user.retirementTreasuryBills}, {user.retirementStockIndex})"
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


async def main(page: ft.Page) -> None:
    page.title = "Pelicoin Banking"
    page.fonts = {
        "Kayak Light": "fonts/Kayak Sans Light.otf",
        "Kayak Regular": "fonts/Kayak Sans Regular.otf",
        "Kayak Bold": "fonts/Kayak Sans Bold.otf",
    }

    routeToView = {
        "/login": getLogInView,
        "/signup": getSignUpView,
        "/accounts": getAccountsView,
        "/accounts/current": getCurrentView,
        "/accounts/education": getEducationView,
        "/accounts/retirement": getRetirementView,
    }

    async def changeRoute(e: ft.RouteChangeEvent):
        e.page.views.clear()
        newView = await routeToView.get(e.route)(page)
        e.page.views.append(newView)
        await page.update_async()

    page.on_route_change = changeRoute

    await page.go_async("/login")


async def getLogInView(page: ft.Page):
    email = ft.TextField(
        label="Email",
        width=FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        text_style=TextFieldStyle,
    )

    password = ft.TextField(
        label="Password",
        width=FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        password=True,
        can_reveal_password=True,
        text_style=TextFieldStyle,
    )

    async def logInButtonOnClick(e: ft.ControlEvent):
        emailValue, passwordValue = email.value, password.value
        account = Account(emailValue, passwordValue)

        u = fetchUserByEmail(emailValue)
        if u and isValidUserLogin(account):
            page.session.set("user", u)
            await page.go_async("/accounts")
        else:
            print("Invalid Account Details!")

    logInButton = ft.ElevatedButton(
        text="Log In",
        width=MAIN_BUTTON_WIDTH,
        on_click=logInButtonOnClick,
    )

    async def signUpButtonOnClick(e: ft.ControlEvent):
        await page.go_async("/signup")

    signUpButton = ft.OutlinedButton(
        text="Sign Up",
        width=SECONDARY_BUTTON_WIDTH,
        on_click=signUpButtonOnClick,
    )

    return ft.View(
        route="/login",
        controls=[
            ft.AppBar(
                title=ft.Text("Pelicoin Banking"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.Column(
                controls=[email, password, logInButton, signUpButton],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


async def getSignUpView(page: ft.Page):
    nameField = ft.TextField(
        label="Name",
        width=FIELD_WIDTH / 2,
        border=ft.InputBorder.NONE,
        filled=True,
    )

    gradYearField = ft.TextField(
        label="Graduation Year",
        width=FIELD_WIDTH / 2,
        border=ft.InputBorder.NONE,
        filled=True,
        input_filter=ft.InputFilter(r"^\d{1,4}$"),
    )

    async def checkedDorm(e: ft.ControlEvent):
        dormField.visible = not dormField.visible
        await e.page.update_async()

    dormCheck = ft.Checkbox(
        label="Are you a boarder?",
        label_position=ft.LabelPosition.LEFT,
        value=False,
        on_change=checkedDorm,
        width=FIELD_WIDTH / 2,
    )

    dormField = ft.TextField(
        label="Dorm",
        width=FIELD_WIDTH / 2,
        border=ft.InputBorder.NONE,
        filled=True,
        visible=False,
    )

    email = ft.TextField(
        label="Email",
        width=FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        text_style=TextFieldStyle,
    )

    password = ft.TextField(
        label="Password",
        width=FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        password=True,
        can_reveal_password=True,
        text_style=TextFieldStyle,
    )

    async def signUp(e: ft.ControlEvent):
        emailValue = email.value
        passwordValue = password.value

        nameValue = nameField.value
        gradYearValue = gradYearField.value
        isBoarderValue = dormCheck.value
        dormValue = dormField.value

        if not nameValue or not gradYearValue:
            print("Name and Graduation Year are required fields!")
            return

        try:
            emailDomain = emailValue.split("@")[1]
        except IndexError:
            emailDomain = ""

        if emailDomain != "loomis.org":
            print("Email needs to end in '@loomis.org'!")
            return

        if not passwordValue:
            print("Password is a required field!")
            return

        newUser = User(
            emailValue,
            passwordValue,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            nameValue,
            gradYearValue,
            isBoarderValue,
            dormValue,
        )
        appendUser(newUser)

        print("Successful Account Signup!")

        await page.go_async("/login")

    submitButton = ft.ElevatedButton(text="Sign Up", on_click=signUp)

    async def backOnClick(e: ft.ControlEvent):
        await page.go_async("/login")

    return ft.View(
        route="/login",
        controls=[
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=backOnClick),
                title=ft.Text("Pelicoin Banking"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.Column(
                controls=[
                    ft.Row(
                        [
                            nameField,
                            gradYearField,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            dormCheck,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    dormField,
                    email,
                    password,
                    submitButton,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


async def getAccountsView(page: ft.Page):
    currentUser = page.session.get("user")
    accountBalances = fetchUserBalances(currentUser)
    (
        currentCash,
        currentTreasuryBills,
        currentStockIndex,
        educationTreasuryBills,
        educationStockIndex,
        retirementTreasuryBills,
        retirementStockIndex,
    ) = (
        currentUser.currentCash,
        currentUser.currentTreasuryBills,
        currentUser.currentStockIndex,
        currentUser.educationTreasuryBills,
        currentUser.educationStockIndex,
        currentUser.retirementTreasuryBills,
        currentUser.retirementStockIndex,
    ) = accountBalances

    currentBalance = sum([currentCash, currentTreasuryBills, currentStockIndex])
    educationBalance = sum([educationTreasuryBills, educationStockIndex])
    retirementBalance = sum([retirementTreasuryBills, retirementStockIndex])
    balance = sum(accountBalances)
    balanceText = ft.Text(
        value=f"{balance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    pelicoin = ft.Image(
        src="/images/peli.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )

    async def enterCurrentButtonOnClick(e: ft.ControlEvent):
        await page.go_async("/accounts/current")

    enterCurrentButton = ft.IconButton(
        ft.icons.ARROW_CIRCLE_RIGHT_OUTLINED,
        on_click=enterCurrentButtonOnClick,
    )
    currentCard = ft.Card(
        content=ft.Row(
            controls=[
                ft.Container(
                    ft.Icon(ft.icons.ATTACH_MONEY, color=ft.colors.YELLOW_300),
                    padding=ft.padding.all(25),
                ),
                ft.Text(value="Current"),
                ft.Text(value=f"{currentBalance:,.2f} Ᵽ", size=18),
                ft.Container(
                    enterCurrentButton, padding=ft.padding.symmetric(horizontal=25)
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=FIELD_WIDTH,
        ),
    )

    async def enterEducationButtonOnClick(e: ft.ControlEvent):
        await page.go_async("/accounts/education")

    enterEducationButton = ft.IconButton(
        ft.icons.ARROW_CIRCLE_RIGHT_OUTLINED,
        on_click=enterEducationButtonOnClick,
    )
    educationCard = ft.Card(
        content=ft.Row(
            controls=[
                ft.Container(
                    ft.Icon(ft.icons.SCHOOL, color=ft.colors.YELLOW_500),
                    padding=ft.padding.all(25),
                ),
                ft.Text(value="Education"),
                ft.Text(value=f"{educationBalance:,.2f} Ᵽ", size=18),
                ft.Container(
                    enterEducationButton, padding=ft.padding.symmetric(horizontal=25)
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=FIELD_WIDTH,
        ),
    )

    async def enterRetirementButtonOnClick(e: ft.ControlEvent):
        await page.go_async("/accounts/retirement")

    enterRetirementButton = ft.IconButton(
        ft.icons.ARROW_CIRCLE_RIGHT_OUTLINED,
        on_click=enterRetirementButtonOnClick,
    )
    retirementCard = ft.Card(
        content=ft.Row(
            controls=[
                ft.Container(
                    ft.Icon(ft.icons.SAVINGS, color=ft.colors.YELLOW_700),
                    padding=ft.padding.all(25),
                ),
                ft.Text(value="Retirement"),
                ft.Text(value=f"{retirementBalance:,.2f} Ᵽ", size=18),
                ft.Container(
                    enterRetirementButton, padding=ft.padding.symmetric(horizontal=25)
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=FIELD_WIDTH,
        ),
    )

    async def enterTransferButtonOnClick(e: ft.ControlEvent):
        await page.go_async("/transfer")

    enterTransferButton = ft.IconButton(
        ft.icons.ARROW_CIRCLE_RIGHT_OUTLINED,
        on_click=enterTransferButtonOnClick,
    )
    transferCard = ft.Card(
        content=ft.Row(
            controls=[
                ft.Container(
                    ft.Icon(ft.icons.COMPARE_ARROWS, color=ft.colors.BLUE_300),
                    padding=ft.padding.all(15),
                ),
                ft.Text(value="Transfer"),
                ft.Container(
                    enterTransferButton, padding=ft.padding.symmetric(horizontal=10)
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=FIELD_WIDTH / 2,
        ),
    )

    balancePieChart = ft.Container(
        ft.PieChart(
            [
                ft.PieChartSection(
                    title=f"Current",
                    title_position=1.25,
                    value=currentBalance,
                    title_style=ChartTitleStyle,
                    color=ft.colors.YELLOW_300,
                    radius=FIELD_WIDTH / 2.25,
                    badge=ft.Column(
                        [
                            ft.Icon(
                                ft.icons.ATTACH_MONEY,
                                color=ft.colors.BACKGROUND,
                                opacity=0.75,
                            ),
                            ft.Text(
                                f"{(currentBalance / balance if balance else 1) * 100:,.0f}%",
                                color=ft.colors.BACKGROUND,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.PieChartSection(
                    title=f"Education",
                    title_position=1.25,
                    value=educationBalance,
                    title_style=ChartTitleStyle,
                    color=ft.colors.YELLOW_500,
                    radius=FIELD_WIDTH / 2.25,
                    badge=ft.Column(
                        [
                            ft.Icon(
                                ft.icons.SCHOOL,
                                color=ft.colors.BACKGROUND,
                                opacity=0.75,
                            ),
                            ft.Text(
                                f"{(educationBalance / balance if balance else 1) * 100:,.0f}%",
                                color=ft.colors.BACKGROUND,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.PieChartSection(
                    title=f"Retirement",
                    title_position=1.25,
                    value=retirementBalance,
                    title_style=ChartTitleStyle,
                    color=ft.colors.YELLOW_700,
                    radius=FIELD_WIDTH / 2.25,
                    badge=ft.Column(
                        [
                            ft.Icon(
                                ft.icons.SAVINGS,
                                color=ft.colors.BACKGROUND,
                                opacity=0.75,
                            ),
                            ft.Text(
                                f"{(retirementBalance / balance if balance else 1) * 100:,.0f}%",
                                color=ft.colors.BACKGROUND,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            width=FIELD_WIDTH,
            height=FIELD_WIDTH,
            center_space_radius=0,
            sections_space=8,
        ),
        padding=ft.padding.all(50),
    )

    async def backOnClick(e: ft.ControlEvent):
        await page.go_async("/login")

    return ft.View(
        route="/accounts",
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=backOnClick),
                title=ft.Text("Pelicoin Banking"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.Row(
                [
                    ft.Column(
                        [
                            pelicoin,
                            balanceText,
                            currentCard,
                            educationCard,
                            retirementCard,
                            ft.Container(
                                bgcolor=ft.colors.ON_INVERSE_SURFACE,
                                height=5,
                                width=FIELD_WIDTH,
                                border_radius=ft.border_radius.all(10),
                            ),
                            balancePieChart,
                            # ft.Container(
                            #     bgcolor=ft.colors.ON_INVERSE_SURFACE,
                            #     height=5,
                            #     width=FIELD_WIDTH,
                            #     border_radius=ft.border_radius.all(10),
                            # ),
                            # transferCard,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.SPACE_AROUND,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


async def getCurrentView(page: ft.Page):
    currentUser = page.session.get("user")
    accountBalances = fetchUserBalances(currentUser)
    (
        currentCash,
        currentTreasuryBills,
        currentStockIndex,
        educationTreasuryBills,
        educationStockIndex,
        retirementTreasuryBills,
        retirementStockIndex,
    ) = accountBalances

    currentBalance = sum([currentCash, currentTreasuryBills, currentStockIndex])
    currentBalanceText = ft.Text(
        value=f"{currentBalance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    async def backOnClick(e: ft.ControlEvent):
        await page.go_async("/accounts")

    return ft.View(
        "/accounts/current",
        [
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=backOnClick),
                title=ft.Text("Pelicoin Banking"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.Row(
                [
                    ft.Column(
                        [currentBalanceText],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )


async def getEducationView(page: ft.Page):
    currentUser = page.session.get("user")
    accountBalances = fetchUserBalances(currentUser)
    (
        currentCash,
        currentTreasuryBills,
        currentStockIndex,
        educationTreasuryBills,
        educationStockIndex,
        retirementTreasuryBills,
        retirementStockIndex,
    ) = accountBalances

    educationBalance = sum([educationTreasuryBills, educationStockIndex])
    educationBalanceText = ft.Text(
        value=f"{educationBalance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    async def backOnClick(e: ft.ControlEvent):
        await page.go_async("/accounts")

    return ft.View(
        "/accounts/education",
        [
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=backOnClick),
                title=ft.Text("Pelicoin Banking"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.Row(
                [
                    ft.Column(
                        [educationBalanceText],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )


async def getRetirementView(page: ft.Page):
    currentUser = page.session.get("user")
    accountBalances = fetchUserBalances(currentUser)
    (
        currentCash,
        currentTreasuryBills,
        currentStockIndex,
        educationTreasuryBills,
        educationStockIndex,
        retirementTreasuryBills,
        retirementStockIndex,
    ) = accountBalances

    retirementBalance = sum([retirementTreasuryBills, retirementStockIndex])
    retirementBalanceText = ft.Text(
        value=f"{retirementBalance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    async def backOnClick(e: ft.ControlEvent):
        await page.go_async("/accounts")

    return ft.View(
        "/accounts/education",
        [
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=backOnClick),
                title=ft.Text("Pelicoin Banking"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.Row(
                [
                    ft.Column(
                        [retirementBalanceText],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )


# app = flet_fastapi.app(main, assets_dir="/Users/lucaslevine/Documents/ISP 2/assets")
app = ft.app(
    main,
    assets_dir=r"/Users/lucaslevine/Documents/ISP 2/assets",
)
