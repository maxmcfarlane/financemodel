import datetime

varex_categories = {
    'bills': ['phone', 'crossfit', 'rent', 'DVLA', 'electricity', 'gas', 'zwift', 'specsavers', 'pcp', 'council tax',
              'internet', 'work phone', 'monzo premium', 'credit ladder', 'headspace', 'klarna', 'amazon prime',
              'google drive', 'spotify', 'mum loan'],
    'groceries': ['groceries'],
    'fuel': ['fuel'],
    'transport': ['transport'],
    'personal care': ['personal care'],
    'gifts care': ['gifts'],
    'fun': ['eating out', 'entertainment']
}

varinc_categories = {
    'bills': ['spotify', 'rebecca', 'mum loan', 'scottish power'],
}

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
    'work phone': -6,
    'spotify': -16.99,
    'monzo premium': -15,
    'credit ladder': -8,
    'headspace': -10,
    'mum loan': -168,
    'klarna': -147.7,
    'amazon prime': -7.99,
    'google drive': -2.49,

    'groceries': -280,
    'fuel': -175,
    'eating out': -100,
    'entertainment': -100,
    'transport': -20,
    'personal care': -20,
    #      xmas,rp,lm,
    'gifts': -((500 + 75 + 30 * 7 + 30 * 3) / 12),
    '': 0,

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
    'work phone': -15,
    'spotify': -25,
    'monzo premium': -20,
    'credit ladder': -8,
    'headspace': -20,
    'mum loan': -168,

}
varex_end = {
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
    'work phone': None,
    'spotify': None,
    'monzo premium': None,
    'credit ladder': None,
    'headspace': None,
    'klarna': datetime.datetime(year=2023, month=1, day=8),
    'mum loan': datetime.datetime(year=2025, month=2, day=1),
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
    'work phone': True,
    'spotify': True,
    'monzo premium': True,
    'credit ladder': True,
    'headspace': True,
    'mum loan': True
}

# variable income
varinc = {
    'spotify': 2.50 * 3,
    'rebecca': 340,
    'mum loan': 170,
    'scottish power': 67,
}
varinc_end = {
    'spotify': None,
    'rebecca': None,
    'mum loan': datetime.datetime(year=2025, month=2, day=1),
    'scottish power': datetime.datetime(year=2023, month=3, day=30),
}
varinc_inflation = {
    'spotify': True,
    'rebecca': True,
    'mum loan': False,
    'scottish power': False,
}
