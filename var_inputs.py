import datetime


# variable expenditure
varex = {
    'phone': -39.90,
    'crossfit': -90,
    'rent': -895,
    'DVLA': -1.75,
    'electricity': -83.35,
    'gas': -80,
    'zwift': -12.99,
    'specsavers': -21,
    'pcp': -201.41,
    'council tax': -150,
    'internet': -36,
    'car insurance': -1007,
    'work phone': -6,
    'spotify premium': -16.99,
    'monzo premium': -15,
    'credit ladder': -8,
    'headspace': -10,
    'mum loan payment': -168,
    'klarna': -147.7,
    'amazon prime': -7.99,
    'google drive': -2.49,

    'groceries': -280,
    'fuel': -175,
    'eating out': -100,
    'entertainment': -100,
    'transport': -20,
    'personal care': -20,

    'rebecca bday': 50,
    'jack bday': 20,
    'laura bday': 20,
    'jessica bday': 20,
    'katie bday': 20,
    'dad bday': 35,
    'granny bday': 20,
    'mum bday': 35,
    'marc bday': 20,
    'holly bday': 35,
    'pauline bday': 35,

    'rebecca xmas': 50,
    'jack xmas': 20,
    'laura xmas': 20,
    'jessica xmas': 20,
    'katie xmas': 20,
    'dad xmas': 35,
    'granny xmas': 20,
    'mum xmas': 35,
    'marc xmas': 20,
    'holly xmas': 35,
    'pauline xmas': 35,

}
varex_max = {
    'phone': -75,
    'crossfit': -120,
    'rent': -1350,
    'DVLA': -5,
    'electricity': -150,
    'zwift': -15,
    'specsavers': -40,
    'pcp': -750,
    'council tax': -250,
    'internet': -50,
    'car insurance': -1500,
    'work phone': -15,
    'spotify premium': -25,
    'monzo premium': -20,
    'credit ladder': -8,
    'headspace': -20,
    'mum loan payment': -168,

}
varex_out = {
    'rent': 1,
    'DVLA': 3,
    'electricity': 3,
    'zwift': 3,
    'crossfit': 4,
    'google drive': 6,
    'phone': 7,
    'klarna': 8,
    'amazon prime': 6,
    'specsavers': 12,
    'mum loan payment': 13,
    'pcp': 21,
    'work phone': 21,
    'spotify premium': 21,
    'credit ladder': 23,
    'monzo premium': 27,
    'headspace': 27,
    'council tax': 28,
    'internet': 28,
    'car insurance': (1, 10),

    'rebecca bday': (1, 1),
    'jack bday': (1, 2),
    'laura bday': (1, 3),
    'jessica bday': (1, 5),
    'katie bday': (1, 6),
    'dad bday': (1, 6),
    'granny bday': (1, 7),
    'mum bday': (1, 8),
    'marc bday': (1, 8),
    'holly bday': (1, 10),
    'pauline bday': (1, 12),

    'rebecca xmas': (1, 11),
    'jack xmas': (1, 11),
    'laura xmas': (1, 11),
    'jessica xmas': (1, 11),
    'katie xmas': (1, 11),
    'dad xmas': (1, 11),
    'granny xmas': (1, 11),
    'mum xmas': (1, 11),
    'marc xmas': (1, 11),
    'holly xmas': (1, 11),
    'pauline xmas': (1, 11),
}
varex_next_business_day = {
    'DVLA': True,
    'council tax': True,
    'credit ladder': True,
    'crossfit': True,
    'electricity': True,
    'google drive': True,
    'headspace': True,
    'internet': True,
    'car insurance': False,
    'klarna': True,
    'amazon prime': True,
    'monzo premium': True,
    'mum loan payment': True,
    'pcp': True,
    'phone': False,
    'rent': False,
    'specsavers': True,
    'spotify premium': False,
    'work phone': False,
    'zwift': True
}

varex_start = {
    'phone': None,
    'crossfit': None,
    'rent': None,
    'DVLA': None,
    'electricity': None,
    'zwift': None,
    'specsavers': None,
    'pcp': None,
    'council tax': None,
    'internet': None,
    'car insurance': datetime.datetime(year=2023, month=10, day=1),
    'work phone': None,
    'spotify premium': None,
    'monzo premium': None,
    'credit ladder': None,
    'headspace': None,
    'klarna': None,
    'amazon prime': None,
    'mum loan payment': None,
}
varex_end = {
    'phone': None,
    'crossfit': None,
    'rent': None,
    'DVLA': None,
    'electricity': None,
    'zwift': datetime.datetime(year=2023, month=2, day=2),
    'specsavers': None,
    'pcp': None,
    'council tax': None,
    'internet': None,
    'car insurance': None,
    'work phone': None,
    'spotify premium': None,
    'monzo premium': None,
    'credit ladder': None,
    'headspace': None,
    'klarna': datetime.datetime(year=2023, month=1, day=25),
    'amazon prime': None,
    'mum loan payment': datetime.datetime(year=2025, month=2, day=1),
}
varex_inflation = {
    'phone': True,
    'crossfit': True,
    'rent': True,
    'DVLA': True,
    'electricity': True,
    'zwift': True,
    'specsavers': True,
    'pcp': True,
    'council tax': True,
    'internet': True,
    'car insurance': True,
    'work phone': True,
    'spotify premium': True,
    'monzo premium': True,
    'credit ladder': True,
    'headspace': True,
    'amazon prime': True,
    'mum loan payment': True
}

# variable income
varinc = {
    'spotify people': 2.50 * 3,
    'rebecca': 340,
    'mum loan': 170,
    'scottish power': 67,
}
varinc_in = {
    'spotify people': 28,
    'rebecca': 3,
    'mum loan': 5,
    'scottish power': 15,
}
varinc_prev_business_day = {
    'spotify people': False,
    'rebecca': False,
    'mum loan': False,
    'scottish power': False,
}
varinc_end = {
    'spotify people': None,
    'rebecca': None,
    'mum loan': datetime.datetime(year=2025, month=2, day=1),
    'scottish power': datetime.datetime(year=2023, month=3, day=30),
}
varinc_inflation = {
    'spotify people': True,
    'rebecca': True,
    'mum loan': False,
    'scottish power': False,
}


varex_categories = {
    'flat': ['rent', 'electricity', 'gas', 'council tax', 'internet'],
    'bills': ['phone', 'crossfit', 'DVLA', 'zwift', 'specsavers', 'pcp', 'work phone',
              'monzo premium', 'credit ladder', 'headspace', 'klarna', 'amazon prime',
              'google drive', 'spotify', 'mum loan'],
    'groceries': ['groceries'],
    'fuel': ['fuel'],
    'transport': ['transport'],
    'personal care': ['personal care'],
    'gifts': [c for c in varex.keys() if 'bday' in c or 'xmas' in c],
    'fun': ['eating out', 'entertainment']
}

varinc_categories = {
    'bills': ['spotify', 'rebecca', 'mum loan', 'scottish power'],
}