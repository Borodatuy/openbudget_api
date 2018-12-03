import json
import requests
import logging


class OpenBudget:

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.regions_data = json.load(open('regions.json'))
        self.base_url = 'https://openbudget.gov.ua/api/localBudgets'

    def get_list_of_local_budgets(self, region_id):
        """
        Ged list of local budgets by region id
        :param region_id: 1-27
        :return:
        """
        url = f'{self.base_url}/getBudgets?regionId={region_id}'
        return requests.get(url).json()

    def get_local_expenses(self, budget_id, classification, month_from, month_to, year, fund_type, detailing):
        """
        Getting JSON with expenses for selected budget ID
        :param budget_id: Budget ID населенного пункту (regions.json)
        :param classification: 'functional': Функціональна класифікація,
                     'program': Програмна класифікація,
                     'economic': Економічна класифікація
        :param month_from: З якого місяця (1-12)
        :param month_to: До якого місяця (1-12)
        :param year: Рік (2018)
        :param fund_type: Тип Фонду (TOTAL: Разом, SPECIAL: Спеціальний, COMMON: Загальний)
        :param detailing: Деталізація (WITHOUT_DETALISATION)
        :return: JSON
                {
                    "level" ?
                    "code" КПК
                    "codeName" Найменування КПК
                    "periodId" ?
                    "data" Данні
                        {
                            "codeEK" ?
                            "codeEkName" ?
                            "codeEkName" ?
                            "codePK" ?
                            "codePkName" ?
                            "codeFK" КФК
                            "codeFkName" Найменування КФК
                            "rozpis" Розпис на рік з урахуванням змін, тис.грн.
                            "rozpisBank" ?
                            "koshtorys" Кошторисні призначення на рік з урахуванням змін, тис.грн.
                            "koshtorysBank" ?
                            "vykonano" Виконано за період, тис.грн.
                            "vykonanoBank" ?
                            "correctionYearDonePercent" Виконання до уточненого річного розпису, %
                            "vykonanoIk" ?
                            "vykonanoIkBank" ?
                            "vykonanoPP" ?
                            "vykonanoPPBank" ?
                            "vykonanoId" ?
                            "vykonanoIdBank" ?
                        }
                }
        """
        url = f'{self.base_url}/{classification}?' \
              f'monthFrom={month_from}&' \
              f'monthTo={month_to}&' \
              f'year={year}&' \
              f'fundType={fund_type}&' \
              f'treeType={detailing}&' \
              f'codeBudget={budget_id}'
        return requests.get(url).json()['items']

    def export_local_expenses(self, filename='local_expenses.csv',
                              classification='program',
                              month_from=1, month_to=10, year=2018,
                              fund_type='TOTAL', detailing='WITHOUT_DETALISATION'):
        """
        Вигрузити усі локальні бюджети у CSV форматі
        :param filename: Назва CSV файу для експорту
        :param classification: 'functional': Функціональна класифікація,
                     'program': Програмна класифікація,
                     'economic': Економічна класифікація
        :param month_from: З якого місяця (1-12)
        :param month_to: До якого місяця (1-12)
        :param year: Рік (2018)
        :param fund_type: Тип Фонду (TOTAL: Разом, SPECIAL: Спеціальний, COMMON: Загальний)
        :param detailing: Деталізація (WITHOUT_DETALISATION)
        :return:
        """

        with open(filename, 'w+') as f:
            f.write(
                'Назва регіону,'
                'Локальний бюджет,'
                'ID бюджету,'
                'Виконання до уточненого річного розпису (%),'
                'Розпис на рік з урахуванням змін (тис.грн.),'
                'Кошторисні призначення на рік з урахуванням змін (тис.грн.),'
                'Виконано за період (тис.грн.),Найменування КПК'
                '\n'
            )

            regions = self.regions_data['regions']
            number_of_regions = len(regions)

            while regions:
                for region in regions:
                    logging.info(f'Regions left: {number_of_regions}')
                    local_budgets = region['localBudgets']
                    number_of_local_budgets = len(local_budgets)

                    while local_budgets:
                        try:
                            for local_budget in local_budgets:
                                logging.info(f'Local budgets left: {number_of_local_budgets}')
                                lid = local_budget['budgetId']
                                name = local_budget['budgetName']
                                res = self.get_local_expenses(
                                    budget_id=lid,
                                    classification=classification,
                                    month_from=month_from,
                                    month_to=month_to,
                                    year=year,
                                    fund_type=fund_type,
                                    detailing=detailing
                                )

                                for item in res:
                                    percent_done = item['data']['correctionYearDonePercent']
                                    line = f'{region["regionName"]},' \
                                           f'{name},' \
                                           f'{lid},' \
                                           f'{percent_done},' \
                                           f'{item["data"]["rozpis"]},' \
                                           f'{item["data"]["koshtorys"]},' \
                                           f'{item["data"]["vykonano"]},' \
                                           f'{item["codeName"]}\n'
                                    f.write(line)

                                number_of_local_budgets -= 1
                                local_budgets.remove(local_budget)
                        except Exception as ex:
                            logging.warning(f'Exception: {ex}')

                    number_of_regions -= 1
                    regions.remove(region)
