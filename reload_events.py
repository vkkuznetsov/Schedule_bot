from pyppeteer import launch

from config import vik_login, vik_pass, windows_path, linux_path
from bd_connect import insert_names, insert_profile
from main import parsing_file


async def reload_profile_events(FIO, id_telegram, index_student):
    browser = await launch(headless=True)
    page = await browser.newPage()
    path = windows_path
    await page.setViewport({'width': 1000, 'height': 500})
    url = 'https://utmn.modeus.org/'
    try:
        await page.goto(url)

        await page.waitForSelector('#userNameInput')

        # Вход в аккаунт
        await page.type('#userNameInput', vik_login)
        await page.type('#passwordInput', vik_pass)
        await page.click('#submitButton')

        # Открытие фильтров и очищение их
        await page.waitForSelector('.btn-filter')
        await page.click('.btn-filter')

        await page.waitForSelector('.btn.btn-clear')
        await page.click('.btn.btn-clear')

        # Выбор вкладки студенты
        await page.waitForSelector('.ui-multiselect-label.ui-corner-all.ng-tns-c56-10')
        await page.click('.ui-multiselect-label.ui-corner-all.ng-tns-c56-10')
        await page.waitFor(1000)

        # Поиск студента
        await page.keyboard.type(FIO)
        await page.waitFor(1500)

        # Подсчет найденных пользователей
        elements_count = await page.evaluate('document.querySelectorAll(".ui-multiselect-item.ui-corner-all").length')

        if elements_count > 1:
            element_index_to_click = index_student - 1

            people_elements = await page.querySelectorAll('.ui-multiselect-item.ui-corner-all')

            await people_elements[element_index_to_click].click()

            await page.waitFor(1500)
            # Применение
            await page.click('.btn.btn-apply')
            await page.click(".btn-filter")
            await page.select('select.fc-view-select', 'month')
            await page.waitFor(1500)

            import os
            os.makedirs(f"{path}{FIO}", exist_ok=True)
            await page._client.send("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": f"{path}{FIO}"
            })

            # Скачивание
            await page.click('.btn.btn2.icon-icalendar.button-reset-default-styles.mb-0')
            await page.waitFor(2500)
            await insert_names(name=FIO, index=element_index_to_click + 1)
            if id_telegram != 0:
                await insert_profile(profile_id=id_telegram, name=FIO, index=element_index_to_click + 1)

            await parsing_file(FIO, index=element_index_to_click + 1)
            await page.browser.close()
        elif elements_count == 1:
            # Выбор студента (единсвенный студент)
            await page.click('.description.ng-star-inserted')
            await page.waitFor(1500)
            # Применение фильтров
            await page.click('.btn.btn-apply')
            await page.click(".btn-filter")
            # Выбор что расписание на месяц
            await page.select('select.fc-view-select', 'month')
            await page.waitFor(1500)

            import os
            os.makedirs(f"{path}{FIO}", exist_ok=True)
            await page._client.send("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": f"{path}{FIO}"
            })

            # Скачивание
            await page.click('.btn.btn2.icon-icalendar.button-reset-default-styles.mb-0')
            await page.waitFor(2500)
            if id_telegram != 0:
                await insert_names(FIO, 1)

                await insert_profile(profile_id=id_telegram, name=FIO, index=1)

            await parsing_file(FIO, 1)
            await page.browser.close()
            return '', 1, page
    except Exception as e:
        print(e)
