import flet as ft
import styles
from user import *


async def errorDialog(page: ft.Page, titleText: str, actionText: str):
    async def onDismiss(e):
        await e.page.close_dialog_async()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(titleText, text_align=ft.TextAlign.CENTER),
        content=ft.Text(actionText, text_align=ft.TextAlign.CENTER),
        actions=[
            ft.TextButton("Dismiss", on_click=onDismiss),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    await page.show_dialog_async(dialog)


# Views


async def getLogInView(page: ft.Page):
    email = ft.TextField(
        label="Email",
        width=styles.FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        text_style=styles.TextFieldStyle,
    )

    password = ft.TextField(
        label="Password",
        width=styles.FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        password=True,
        can_reveal_password=True,
        text_style=styles.TextFieldStyle,
    )

    async def logInButtonOnClick(e: ft.ControlEvent):
        emailValue, passwordValue = email.value, password.value

        user = fetchUserByEmail(emailValue)
        if user and authenticateUserLogin(emailValue, passwordValue):
            page.session.set("user", user)
            await page.go_async("/accounts")
        else:
            await errorDialog(
                page, "Invalid Account Details", "Check your email and password."
            )

    logInButton = ft.ElevatedButton(
        text="Log In",
        width=styles.MAIN_BUTTON_WIDTH,
        on_click=logInButtonOnClick,
    )

    async def signUpButtonOnClick(e: ft.ControlEvent):
        await page.go_async("/signup")

    signUpButton = ft.OutlinedButton(
        text="Sign Up",
        width=styles.MAIN_BUTTON_WIDTH - 20,
        on_click=signUpButtonOnClick,
    )

    async def adminButtonOnClick(e: ft.ControlEvent):
        emailValue, passwordValue = email.value, password.value

        admin = fetchAdminByEmail(emailValue)
        if admin and authenticateAdminLogin(emailValue, passwordValue):
            page.session.set("admin", admin)
            await page.go_async("/admin")
        else:
            await errorDialog(
                page, "Invalid Account Details", "Check your email and password."
            )

    adminButton = ft.Container(
        ft.TextButton(
            text="Admin?",
            width=styles.MAIN_BUTTON_WIDTH / 2,
            on_click=adminButtonOnClick,
            scale=0.75,
        ),
        padding=ft.padding.all(5),
    )

    return ft.View(
        route="/login",
        controls=[
            ft.AppBar(
                title=ft.Text("Pelicoin Banking"),
                actions=[adminButton],
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
        width=styles.FIELD_WIDTH / 2,
        border=ft.InputBorder.NONE,
        filled=True,
    )

    gradYearField = ft.TextField(
        label="Graduation Year",
        width=styles.FIELD_WIDTH / 2,
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
        width=styles.FIELD_WIDTH / 2,
    )

    dormField = ft.TextField(
        label="Dorm",
        width=styles.FIELD_WIDTH / 2,
        border=ft.InputBorder.NONE,
        filled=True,
        visible=False,
    )

    email = ft.TextField(
        label="Email",
        width=styles.FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        text_style=styles.TextFieldStyle,
    )

    password = ft.TextField(
        label="Password",
        width=styles.FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        password=True,
        can_reveal_password=True,
        text_style=styles.TextFieldStyle,
    )

    async def signUp(e: ft.ControlEvent):
        emailValue = email.value
        passwordValue = password.value

        nameValue = nameField.value
        gradYearValue = gradYearField.value
        isBoarderValue = dormCheck.value
        dormValue = dormField.value

        if not nameValue or not gradYearValue:
            await errorDialog(
                page,
                "Required Fields Missing",
                "Name and Graduation Year are required fields.",
            )
            return

        try:
            emailDomain = emailValue.split("@")[1]
        except IndexError:
            emailDomain = ""

        if emailDomain != "loomis.org":
            await errorDialog(
                page, "Email Invalid", "Email needs to end in '@loomis.org'."
            )
            return

        if not passwordValue:
            await errorDialog(
                page, "Required Fields Missing", "Password is a required field."
            )
            return

        if fetchUserByEmail(emailValue):
            await errorDialog(page, "Email Invalid", "This email is already in use.")
            return

        newUser = User(
            emailValue,
            passwordValue,
            nameValue,
            dormValue,
            gradYearValue,
            {
                "current": {"cash": 0.0, "treasury": 0.0, "stocks": 0.0},
                "education": {"treasury": 0.0, "stocks": 0.0},
                "retirement": {"treasury": 0.0, "stocks": 0.0},
            },
        )
        insertUser(newUser)

        page.session.set("user", newUser)
        await page.go_async("/accounts")

        await errorDialog(
            page, "Successful Account Sign Up", "Welcome to Pelicoin Banking!"
        )

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
    user: User = page.session.get("user")

    welcomeText = ft.Container(
        ft.Text(f"Welcome, {user.name}.", size=28),
        bgcolor=ft.colors.ON_INVERSE_SURFACE,
        border_radius=25,
        padding=10,
    )

    currentBalance = sum(user.balances["current"].values())
    educationBalance = sum(user.balances["education"].values())
    retirementBalance = sum(user.balances["retirement"].values())
    balance = currentBalance + educationBalance + retirementBalance
    balanceText = ft.Text(
        value=f"{balance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    pelicoin = ft.Image(
        src="images/peli.png",
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
            width=styles.FIELD_WIDTH,
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
            width=styles.FIELD_WIDTH,
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
            width=styles.FIELD_WIDTH,
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
            width=styles.FIELD_WIDTH / 2,
        ),
    )

    balancePieChart = ft.Container(
        ft.PieChart(
            [
                ft.PieChartSection(
                    title=f"Current",
                    title_position=1.25,
                    value=currentBalance,
                    title_style=styles.ChartTitleStyle,
                    color=ft.colors.YELLOW_300,
                    radius=styles.FIELD_WIDTH / 2.25,
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
                    title_style=styles.ChartTitleStyle,
                    color=ft.colors.YELLOW_500,
                    radius=styles.FIELD_WIDTH / 2.25,
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
                    title_style=styles.ChartTitleStyle,
                    color=ft.colors.YELLOW_700,
                    radius=styles.FIELD_WIDTH / 2.25,
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
            width=styles.FIELD_WIDTH,
            height=styles.FIELD_WIDTH,
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
            ft.ResponsiveRow(
                [
                    ft.Column(
                        [
                            welcomeText,
                            pelicoin,
                            balanceText,
                            currentCard,
                            educationCard,
                            retirementCard,
                            ft.Container(
                                bgcolor=ft.colors.ON_INVERSE_SURFACE,
                                height=5,
                                width=styles.FIELD_WIDTH,
                                border_radius=ft.border_radius.all(10),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        col={"sm": 8, "md": 6},
                    ),
                    ft.Column(
                        [
                            balancePieChart,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        col={"sm": 8, "md": 6},
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                columns=12,
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.SPACE_AROUND,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


async def getCurrentView(page: ft.Page):
    user: User = page.session.get("user")

    currentBalance = sum(user.balances["current"].values())
    currentBalanceText = ft.Text(
        value=f"{currentBalance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    currentBalanceDetailed = ft.Row(
        [
            ft.Text(f"Cash: {user.balances['current']['cash']}"),
            ft.Text(f"Treasury Bills: {user.balances['current']['treasury']}"),
            ft.Text(f"Index Fund: {user.balances['current']['stocks']}"),
        ]
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
                        [currentBalanceText, currentBalanceDetailed],
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
    user: User = page.session.get("user")

    educationBalance = sum(user.balances["education"].values())
    educationBalanceText = ft.Text(
        value=f"{educationBalance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    educationBalanceDetailed = ft.Row(
        [
            ft.Text(f"Treasury Bills: {user.balances['education']['treasury']}"),
            ft.Text(f"Index Fund: {user.balances['education']['stocks']}"),
        ]
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
                        [educationBalanceText, educationBalanceDetailed],
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
    user: User = page.session.get("user")

    retirementBalance = sum(user.balances["retirement"].values())
    retirementBalanceText = ft.Text(
        value=f"{retirementBalance:,.2f} Ᵽ",
        text_align=ft.TextAlign.CENTER,
        width=350,
        size=50,
    )

    retirementBalanceDetailed = ft.Row(
        [
            ft.Text(f"Treasury Bills: {user.balances['retirement']['treasury']}"),
            ft.Text(f"Index Fund: {user.balances['retirement']['stocks']}"),
        ]
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
                        [retirementBalanceText, retirementBalanceDetailed],
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


async def getAdminView(page: ft.Page):
    labelToType = {"Cash": "cash", "Treasury Bills": "treasury", "Index Fund": "stocks"}

    async def selectChanged(e: ft.ControlEvent):
        e.control.selected = not e.control.selected
        await namesTable.update_async()

    async def getAllNameRows(users: list[User], sortBy: str | None = None):
        match sortBy:
            case "name":
                users.sort(key=lambda u: u.name, reverse=namesTable.sort_ascending)
            case "current":
                users.sort(
                    key=lambda u: sum(u.balances["current"].values()),
                    reverse=namesTable.sort_ascending,
                )
            case "education":
                users.sort(
                    key=lambda u: sum(u.balances["education"].values()),
                    reverse=namesTable.sort_ascending,
                )
            case "retirement":
                users.sort(
                    key=lambda u: sum(u.balances["retirement"].values()),
                    reverse=namesTable.sort_ascending,
                )
            case "year":
                users.sort(
                    key=lambda u: u.gradYear,
                    reverse=namesTable.sort_ascending,
                )

        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(u.name)),
                    ft.DataCell(
                        ft.Column(
                            [
                                ft.Text(
                                    f"{(sum(u.balances['current'].values())):,.2f}",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    str(
                                        [
                                            f"{val:,.2f}"
                                            for val in u.balances["current"].values()
                                        ]
                                    )
                                    .replace("[", "")
                                    .replace("]", "")
                                    .replace("'", ""),
                                    size=10,
                                    weight=ft.FontWeight.W_100,
                                ),
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ),
                    ft.DataCell(
                        ft.Column(
                            [
                                ft.Text(
                                    f"{(sum(u.balances['education'].values())):,.2f}",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    str(
                                        [
                                            f"{val:,.2f}"
                                            for val in u.balances["education"].values()
                                        ]
                                    )
                                    .replace("[", "")
                                    .replace("]", "")
                                    .replace("'", ""),
                                    size=10,
                                    weight=ft.FontWeight.W_100,
                                ),
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ),
                    ft.DataCell(
                        ft.Column(
                            [
                                ft.Text(
                                    f"{(sum(u.balances['retirement'].values())):,.2f}",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    str(
                                        [
                                            f"{val:,.2f}"
                                            for val in u.balances["retirement"].values()
                                        ]
                                    )
                                    .replace("[", "")
                                    .replace("]", "")
                                    .replace("'", ""),
                                    size=10,
                                    weight=ft.FontWeight.W_100,
                                ),
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ),
                    ft.DataCell(ft.Text(u.gradYear)),
                    ft.DataCell(ft.Text(u.email), visible=False),
                ],
                on_select_changed=selectChanged,
            )
            for u in users
        ]

    async def nameSearchOnChange(e: ft.ControlEvent):
        namesTable.rows = [
            nameRow
            for nameRow in await getAllNameRows(fetchUsers())
            if e.control.value.lower() in nameRow.cells[0].content.value.lower()
        ]
        await namesTable.update_async()

    nameSearch = ft.TextField(
        label="Name",
        width=styles.FIELD_WIDTH,
        border=ft.InputBorder.OUTLINE,
        filled=True,
        text_style=styles.TextFieldStyle,
        on_change=nameSearchOnChange,
    )

    def onSortFactory(sortBy: str):
        async def new(e: ft.ControlEvent):
            namesTable.rows = await getAllNameRows(fetchUsers(), sortBy)
            namesTable.sort_ascending = not namesTable.sort_ascending
            match sortBy:
                case "name":
                    namesTable.sort_column_index = 0
                case "current":
                    namesTable.sort_column_index = 1
                case "education":
                    namesTable.sort_column_index = 2
                case "retirement":
                    namesTable.sort_column_index = 3
                case "year":
                    namesTable.sort_column_index = 4
            await namesTable.update_async()

        return new

    namesTable = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Text("Name"),
                on_sort=onSortFactory("name"),
            ),
            ft.DataColumn(
                ft.Text("Current"), numeric=True, on_sort=onSortFactory("current")
            ),
            ft.DataColumn(
                ft.Text("Education"), numeric=True, on_sort=onSortFactory("education")
            ),
            ft.DataColumn(
                ft.Text("Retirement"), numeric=True, on_sort=onSortFactory("retirement")
            ),
            ft.DataColumn(ft.Text("Year"), numeric=True, on_sort=onSortFactory("year")),
        ],
        rows=await getAllNameRows(fetchUsers()),
        width=styles.FIELD_WIDTH * 2,
        column_spacing=25,
        show_checkbox_column=True,
        sort_column_index=0,
        sort_ascending=False,
    )

    accountLabel = ft.Text("Current", size=16, weight=ft.FontWeight.W_500)

    async def accountChanged(e: ft.ControlEvent):
        if e.control.value == 1:
            accountLabel.value = "Current"
            accountTypeLabel.value = "Cash"
            accountTypeSlider.min = 1
            accountTypeSlider.value = 1
            accountTypeSlider.divisions = 2
        elif e.control.value == 2:
            accountLabel.value = "Education"
            accountTypeLabel.value = "Treasury Bills"
            accountTypeSlider.min = 2
            accountTypeSlider.value = 2
            accountTypeSlider.divisions = 1
        else:
            accountLabel.value = "Retirement"
            accountTypeLabel.value = "Treasury Bills"
            accountTypeSlider.min = 2
            accountTypeSlider.value = 2
            accountTypeSlider.divisions = 1

        await accountLabel.update_async()
        await accountTypeSlider.update_async()
        await accountTypeLabel.update_async()

    accountSlider = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        height=20,
        on_change=accountChanged,
    )

    accountTypeLabel = ft.Text("Cash", size=13, weight=ft.FontWeight.NORMAL)

    async def accountTypeChanged(e: ft.ControlEvent):
        if e.control.value == 1:
            accountTypeLabel.value = "Cash"
        elif e.control.value == 2:
            accountTypeLabel.value = "Treasury Bills"
        else:
            accountTypeLabel.value = "Index Fund"

        await accountTypeLabel.update_async()

    accountTypeSlider = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        height=20,
        on_change=accountTypeChanged,
    )

    accountLabeledSlider = ft.Container(
        ft.Column(
            [
                ft.Row(
                    [
                        accountLabel,
                        ft.Text("|"),
                        accountTypeLabel,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                accountSlider,
                accountTypeSlider,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.all(10),
        bgcolor=ft.colors.GREY_700,
        border_radius=25,
    )

    async def formatNumberOnBlur(e: ft.ControlEvent):
        e.control.value = f"{float(e.control.value):,.2f}" if e.control.value else ""
        await e.control.update_async()

    async def onAddClick(e: ft.ControlEvent):
        for row in namesTable.rows:
            if row.selected:
                depositToBalance(
                    row.cells[-1].content.value,
                    float(
                        addRow.controls[0].value.replace(",", "")
                        if addRow.controls[0].value
                        else 0.0
                    ),
                    accountLabel.value.lower(),
                    f"{labelToType.get(accountTypeLabel.value)}",
                )
        namesTable.rows = await getAllNameRows(fetchUsers())
        await namesTable.update_async()

    addRow = ft.ResponsiveRow(
        [
            ft.TextField(
                label="Add",
                col=10,
                input_filter=ft.InputFilter(
                    regex_string=r"^\d+(\.\d*)?$",
                    allow=True,
                    replacement_string="",
                ),
                on_blur=formatNumberOnBlur,
            ),
            ft.IconButton(
                ft.icons.ADD,
                col=2,
                on_click=onAddClick,
            ),
        ]
    )

    async def onSubClick(e: ft.ControlEvent):
        for row in namesTable.rows:
            if row.selected:
                depositToBalance(
                    row.cells[-1].content.value,
                    -float(
                        subtractRow.controls[0].value.strip(",")
                        if subtractRow.controls[0].value
                        else 0.0
                    ),
                    accountLabel.value.lower(),
                    f"{labelToType.get(accountTypeLabel.value)}",
                )

        namesTable.rows = await getAllNameRows(fetchUsers())
        await namesTable.update_async()

    subtractRow = ft.ResponsiveRow(
        [
            ft.TextField(
                label="Subtract",
                col=10,
                input_filter=ft.InputFilter(
                    regex_string=r"^\d+(\.\d*)?$",
                    allow=True,
                    replacement_string="",
                ),
                on_blur=formatNumberOnBlur,
            ),
            ft.IconButton(ft.icons.MINIMIZE, col=2, on_click=onSubClick),
        ],
    )

    async def onSetClick(e: ft.ControlEvent):
        for row in namesTable.rows:
            if row.selected:
                setBalance(
                    row.cells[-1].content.value,
                    float(
                        setRow.controls[0].value.strip(",")
                        if setRow.controls[0].value
                        else 0.0
                    ),
                    accountLabel.value.lower(),
                    f"{labelToType.get(accountTypeLabel.value)}",
                )

        namesTable.rows = await getAllNameRows(fetchUsers())
        await namesTable.update_async()

    setRow = ft.ResponsiveRow(
        [
            ft.TextField(
                label="Set",
                col=10,
                input_filter=ft.InputFilter(
                    regex_string=r"^\d+(\.\d*)?$",
                    allow=True,
                    replacement_string="",
                ),
                on_blur=formatNumberOnBlur,
            ),
            ft.IconButton(ft.icons.ARROW_FORWARD, col=2, on_click=onSetClick),
        ]
    )

    balancesTile = ft.ExpansionTile(
        title=ft.Row(
            [
                ft.Icon(ft.icons.ATTACH_MONEY),
                ft.Text("Balances", size=20),
            ],
        ),
        subtitle=ft.Text("Add, substract, set."),
        controls=[
            accountLabeledSlider,
            ft.Divider(opacity=0),
            addRow,
            ft.Divider(),
            subtractRow,
            ft.Divider(),
            setRow,
        ],
        controls_padding=10,
    )

    accountLabelRates = ft.Text("Current", size=16, weight=ft.FontWeight.W_500)

    async def accountChangedRates(e: ft.ControlEvent):
        if e.control.value == 1:
            accountLabelRates.value = "Current"
            accountTypeLabelRates.value = "Cash"
            accountTypeSliderRates.min = 1
            accountTypeSliderRates.value = 1
            accountTypeSliderRates.divisions = 2
        elif e.control.value == 2:
            accountLabelRates.value = "Education"
            accountTypeLabelRates.value = "Treasury Bills"
            accountTypeSliderRates.min = 2
            accountTypeSliderRates.value = 2
            accountTypeSliderRates.divisions = 1
        else:
            accountLabelRates.value = "Retirement"
            accountTypeLabelRates.value = "Treasury Bills"
            accountTypeSliderRates.min = 2
            accountTypeSliderRates.value = 2
            accountTypeSliderRates.divisions = 1

        await accountLabelRates.update_async()
        await accountTypeSliderRates.update_async()
        await accountTypeLabelRates.update_async()

    accountSliderRates = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        height=20,
        on_change=accountChangedRates,
    )

    accountTypeLabelRates = ft.Text("Cash", size=13, weight=ft.FontWeight.NORMAL)

    async def accountTypeChangedRates(e: ft.ControlEvent):
        if e.control.value == 1:
            accountTypeLabelRates.value = "Cash"
        elif e.control.value == 2:
            accountTypeLabelRates.value = "Treasury Bills"
        else:
            accountTypeLabelRates.value = "Index Fund"

        await accountTypeLabelRates.update_async()

    accountTypeSliderRates = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        height=20,
        on_change=accountTypeChangedRates,
    )

    accountLabeledSliderRates = ft.Container(
        ft.Column(
            [
                ft.Row(
                    [
                        accountLabelRates,
                        ft.Text("|"),
                        accountTypeLabelRates,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                accountSliderRates,
                accountTypeSliderRates,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.all(10),
        bgcolor=ft.colors.GREY_700,
        border_radius=25,
    )

    async def yieldReturnOnClick(e: ft.ControlEvent):
        for row in namesTable.rows:
            yieldToBalance(
                row.cells[-1].content.value,
                float(
                    yieldReturn.content.controls[0].value.replace(",", "")
                    if yieldReturn.content.controls[0].value
                    else 0.0
                ),
                accountLabelRates.value.lower(),
                f"{labelToType.get(accountTypeLabelRates.value)}",
            )
        namesTable.rows = await getAllNameRows(fetchUsers())
        await namesTable.update_async()

    yieldReturn = ft.Container(
        ft.ResponsiveRow(
            [
                ft.TextField(
                    label="Yield Percentage",
                    col=10,
                    input_filter=ft.InputFilter(
                        regex_string=r"^\d+(\.\d*)?$",
                        allow=True,
                        replacement_string="",
                    ),
                    on_blur=formatNumberOnBlur,
                    suffix=ft.Text("%"),
                ),
                ft.IconButton(
                    ft.icons.ARROW_FORWARD, col=2, on_click=yieldReturnOnClick
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
    )

    ratesTile = ft.ExpansionTile(
        title=ft.Row(
            [
                ft.Icon(ft.icons.AREA_CHART),
                ft.Text("Rates", size=24),
            ],
        ),
        subtitle=ft.Text("Set earning rates."),
        controls=[accountLabeledSliderRates, yieldReturn],
        controls_padding=10,
    )

    gradYearField = ft.TextField(
        label="Graduation Year",
        col=8,
        input_filter=ft.NumbersOnlyInputFilter(),
    )

    async def purgeOnClick(e: ft.ControlEvent):
        deleteGradYear(gradYearField.value)
        namesTable.rows = await getAllNameRows(fetchUsers())
        await namesTable.update_async()

    purgeSeniors = ft.ResponsiveRow(
        [
            gradYearField,
            ft.OutlinedButton("Purge", col=4, on_click=purgeOnClick),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    async def purgeSelected(e: ft.ControlEvent):
        for row in namesTable.rows:
            if row.selected:
                deleteUserByEmail(row.cells[-1].content.value)
        namesTable.rows = await getAllNameRows(fetchUsers())
        await namesTable.update_async()

    purgeSelect = ft.Container(
        ft.FilledButton("Purge Selected Users", on_click=purgeSelected), padding=10
    )

    miscTile = ft.ExpansionTile(
        title=ft.Row(
            [
                ft.Icon(ft.icons.MISCELLANEOUS_SERVICES),
                ft.Text("Misc.", size=24),
            ],
        ),
        subtitle=ft.Text("Manage miscellaneous functions."),
        controls=[purgeSelect, purgeSeniors],
        controls_padding=10,
    )

    controlPanelColumn = ft.Column(
        [balancesTile, ratesTile, miscTile],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    async def backOnClick(e: ft.ControlEvent):
        await page.go_async("/login")

    return ft.View(
        "/admin",
        [
            ft.AppBar(
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=backOnClick),
                title=ft.Text("Pelicoin Admin Panel"),
                center_title=True,
                toolbar_height=50,
            ),
            ft.ResponsiveRow(
                [
                    ft.Column(
                        [nameSearch, namesTable],
                        col=8,
                    ),
                    ft.Container(
                        controlPanelColumn,
                        bgcolor=ft.colors.ON_INVERSE_SURFACE,
                        col=4,
                        padding=10,
                        border_radius=10,
                    ),
                ]
            ),
        ],
    )
