import asyncio
import time
from datetime import datetime

from pyppeteer import launch


async def get_subjects(subject):
    actual_month = datetime.now().month
    if actual_month >= 9:
        actual_study_year = str(datetime.now().year) + '-' + str(datetime.now().year + 1) + ' учебный год'
    else:
        actual_study_year = str(datetime.now().year - 1) + '-' + str(datetime.now().year) + ' учебный год'

    browser = await launch(headless=False)
    page = await browser.newPage()

    await page.setViewport({'width': 1000, 'height': 500})
    url = 'https://utmn.modeus.org/'
    try:
        await page.goto(url)

        await page.waitForSelector('#userNameInput')

        # Вход в аккаунт
        await page.type('#userNameInput', 'stud0000261239@study.utmn.ru')
        await page.type('#passwordInput', 'Nikitos7286!')
        await page.click('#submitButton')

        # Открытие фильтров и очищение их
        await page.waitForSelector('.btn-filter')
        await page.click('.btn-filter')

        await page.waitForSelector('.btn.btn-clear')
        await page.click('.btn.btn-clear')

        await page.click(
            'body > app-root > modeus-root > div > div > mds-schedule-calendar-display > div > div > div > div > div > div > div.calendar-container > div > div > div > mds-fullcalendar > mds-schedule-calendar-filter > form > div > div:nth-child(5) > custom-multiselect > p-multiselect > div')
        await page.type(
            'body > app-root > modeus-root > div > div > mds-schedule-calendar-display > div > div > div > div > div > div > div.calendar-container > div > div > div > mds-fullcalendar > mds-schedule-calendar-filter > form > div > div:nth-child(5) > custom-multiselect > p-multiselect > div > div.ng-trigger.ng-trigger-overlayAnimation.ng-tns-c56-7.ui-multiselect-panel.ui-widget.ui-widget-content.ui-corner-all.ui-shadow.ng-star-inserted > div.ui-widget-header.ui-corner-all.ui-multiselect-header.ui-helper-clearfix.ng-tns-c56-7.ui-multiselect-header-no-toggleall.ng-star-inserted > p-header > div > input',
            subject)
        await page.waitFor(3000)

        elements_count = await page.evaluate(
            'document.querySelector("body > app-root > modeus-root > div > div > mds-schedule-calendar-display > div > div > div > div > div > div > div.calendar-container > div > div > div > mds-fullcalendar > mds-schedule-calendar-filter > form > div > div:nth-child(5) > custom-multiselect > p-multiselect > div > div.ng-trigger.ng-trigger-overlayAnimation.ng-tns-c56-7.ui-multiselect-panel.ui-widget.ui-widget-content.ui-corner-all.ui-shadow.ng-star-inserted > div.ui-multiselect-items-wrapper.ng-tns-c56-7 > ul").children.length')

        if elements_count == 0:
            await page.browser.close()
            return ''

        elif elements_count > 0:
            subject_info = await page.evaluate('''(actual_study_year) =>{

                const subjectsElements = document.querySelectorAll('.ui-multiselect-item.ui-corner-all');
                const subjectsData = [];

                subjectsElements.forEach((element, index) => 
                {
                    const label = element.querySelector('.label').innerText;
                    const descriptions = element.querySelectorAll('.description');
                    descriptions.forEach(desc => {
                        if (desc.innerText.includes(actual_study_year))
                        {
                            subjectsData.push([index, label, desc.innerText]);
                        }
                    });
                });

                return subjectsData;
            }''', actual_study_year)

            print(subject_info)

    except Exception as e:
        return (e)


asyncio.get_event_loop().run_until_complete(get_subjects('разработка'))