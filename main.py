import os
import glob
from pyppeteer import launch

from config import vik_login, vik_pass
from bd_connect import insert_events, insert_many_table, insert_names, insert_profile, insert_friend


async def parsing_file(FIO, index=None):
    folder_path = r"C:\Users\Vik\Desktop"
    ics_files = glob.glob(os.path.join(folder_path, '*.ics'))

    if ics_files:
        newest_file = max(ics_files, key=os.path.getctime)
    else:
        print('БЛят у нас эксепшен, файла нахуй нет')

    with open(newest_file, 'r', encoding='utf-8') as file:
        temp_list = list()
        for i in file.readlines():

            if i.startswith('UID'):
                temp_list.append(i[4:-1])
            elif i.startswith('DTSTART'):
                temp_list.append(i[-16:-3])
            elif i.startswith('DTEND'):
                temp_list.append(i[-16:-3])
            elif i.startswith('SUMMARY'):
                if '/' in i[8:]:
                    raw_string = ' '.join(i[8:i.index('/')].split())
                else:
                    # Обработка случая, когда '/' не найден в строке
                    raw_string = ' '.join(i[8:].split())
                finally_string = str()
                for i in raw_string:
                    if i not in {"\\", '\\'}:
                        finally_string += i
                temp_list.append(finally_string)
            elif i.startswith('LOCATION'):
                temp_list.append(' '.join(i[9:].split()))
            elif i.startswith('DESCRIPTION'):
                if temp_list[3].find('Физическая культура') != -1:
                    temp_list.append('-')
                else:
                    raw_string = ' '.join(i[i.find('Преподавател') + 14:i.find('Посмотреть') - 4].split())
                    finally_string = str()
                    for i in raw_string:
                        if i not in {"\\", 'n'}:
                            finally_string += i
                    temp_list.append(finally_string)
            elif i.startswith('CATEGORIES'):
                temp_list.append(i[11:-1])
            if len(temp_list) == 8:
                await insert_events(temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4],
                                    temp_list[5],
                                    temp_list[6], temp_list[7])
                await insert_many_table(name=FIO, event_id=temp_list[0], index=index)
                temp_list.clear()
    os.remove(newest_file)


async def login_to_modeus(FIO, id_telegram, insert_table_code):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page._client.send("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": r"C:\Users\Vik\Desktop"
    })
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

        if elements_count == 0:
            await page.browser.close()
            return '', 0, page

        elif elements_count > 1:
            people_info = await page.evaluate('''() => {
                    const peopleElements = document.querySelectorAll('.ui-multiselect-item.ui-corner-all');
                    const peopleData = [];
    
                    peopleElements.forEach(element => {
                        const label = element.querySelector('.label').innerText;
                        const descriptions = element.querySelectorAll('.description');
    
                        const descriptionsData = [];
                        descriptions.forEach(desc => {
                            descriptionsData.push(desc.innerText);
                        });
    
                        peopleData.push({ label, descriptions: descriptionsData });
                    });
    
                    return peopleData;
                }''')

            pair_smiles = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
            final_str = ""

            for index, person in enumerate(people_info):
                final_str += f"\n\n{pair_smiles[index]} <strong>{person['label']}</strong>\n"
                for desc in person['descriptions']:
                    final_str += f" {desc}"

            return final_str, elements_count, page
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

            # Скачивание
            await page.click('.btn.btn2.icon-icalendar.button-reset-default-styles.mb-0')
            await page.waitFor(2500)
            await insert_names(FIO, 1)
            if insert_table_code == 1:
                await insert_profile(profile_id=id_telegram, name=FIO, index=1)
            elif insert_table_code == 2:
                await insert_friend(profile_id=id_telegram, name=FIO, index=1)
            await parsing_file(FIO, 1)
            await page.browser.close()
            return '', 1, page
    except Exception as e:
        return (e)


async def modeus_cont(page, FIO, id_telegram, insert_table_code, index_student=0):
    element_index_to_click = index_student

    people_elements = await page.querySelectorAll('.ui-multiselect-item.ui-corner-all')

    await people_elements[element_index_to_click].click()

    await page.waitFor(1500)
    # Применение
    await page.click('.btn.btn-apply')
    await page.click(".btn-filter")
    await page.select('select.fc-view-select', 'month')
    await page.waitFor(1500)

    # Скачивание
    await page.click('.btn.btn2.icon-icalendar.button-reset-default-styles.mb-0')
    await page.waitFor(2500)
    await insert_names(name=FIO, index=index_student + 1)

    if insert_table_code == 1:
        await insert_profile(profile_id=id_telegram, name=FIO, index=index_student + 1)

    elif insert_table_code == 2:
        await insert_friend(profile_id=id_telegram, name=FIO, index=index_student + 1)

    await parsing_file(FIO, index=index_student + 1)
    await page.browser.close()
