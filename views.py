import flet as ft
import styles, user


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
        account = user.Account(emailValue, passwordValue)

        u = user.fetchUserByEmail(emailValue)
        if u and user.isValidUserLogin(account):
            page.session.set("user", u)
            await page.go_async("/accounts")
        else:
            print("Invalid Account Details!")

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
        account = user.Account(emailValue, passwordValue)

        a = user.fetchAdminByEmail(emailValue)
        if a and user.isValidAdminLogin(account):
            page.session.set("admin", a)
            await page.go_async("/admin")
        else:
            print("Invalid Account Details!")

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

        newUser = user.User(
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
        user.appendUser(newUser)

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
    currentUser: user.User = page.session.get("user")
    accountBalances = {
        "current": currentUser.current,
        "education": currentUser.education,
        "retirement": currentUser.retirement,
    }

    currentBalance = sum(accountBalances.get("current").values())
    educationBalance = sum(accountBalances.get("education").values())
    retirementBalance = sum(accountBalances.get("retirement").values())
    balance = currentBalance + educationBalance + retirementBalance
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
    currentUser = page.session.get("user")
    accountBalances = user.fetchUserBalances(currentUser)
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
    accountBalances = user.fetchUserBalances(currentUser)
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
    accountBalances = user.fetchUserBalances(currentUser)
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


async def getAdminView(page: ft.Page):
    allUsers = user.fetchUsers()

    async def selectChanged(e: ft.ControlEvent):
        e.control.selected = not e.control.selected
        await namesTable.update_async()

    allNameRows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(u.name)),
                ft.DataCell(ft.Text(str(sum(u.current.values())))),
                ft.DataCell(ft.Text(str(sum(u.education.values())))),
                ft.DataCell(ft.Text(str(sum(u.education.values())))),
            ],
            on_select_changed=selectChanged,
        )
        for u in allUsers
    ]

    async def nameSearchOnChange(e: ft.ControlEvent):
        namesTable.rows = [
            nameRow
            for nameRow in allNameRows
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

    namesTable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Current"), numeric=True),
            ft.DataColumn(ft.Text("Education"), numeric=True),
            ft.DataColumn(ft.Text("Retirement"), numeric=True),
        ],
        rows=allNameRows,
        width=styles.FIELD_WIDTH * 2,
        column_spacing=25,
        show_checkbox_column=True,
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
            ft.TextField(label="Add"),
            ft.Divider(),
            ft.TextField(label="Subtract"),
            ft.Divider(),
            ft.TextField(label="Set"),
        ],
        controls_padding=10,
    )

    ratesTile = ft.ExpansionTile(
        title=ft.Row(
            [
                ft.Icon(ft.icons.AREA_CHART),
                ft.Text("Rates", size=24),
            ],
        ),
        subtitle=ft.Text("Set earning rates."),
        controls=[],
    )

    controlPanelColumn = ft.Column(
        [balancesTile, ratesTile],
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
