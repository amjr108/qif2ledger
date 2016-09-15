#!/usr/bin/env python3
#-*- coding: utf-8 -*-"

import sys
from qifparse.parser import QifParser, AmountSplit

dateFormat = '20%y/%m/%d'
accountPrefix = 'Активи'
expencesPrefix = 'Витрати'
incomePrefix = 'Доходи'
defaultPayee = 'Без платника'
defaultCategory = 'Інше'

def memo2comment(memo):
    if memo:
       return '  ; ' + ' '.join( [':{}:'.format(token[1:]) \
                                 if token.startswith('#') else token \
                                       for token in memo.split()] )
    else:
       return ''

def transaction2ledger(transaction, accountName):
    result = '{} * {}\n'.format(transaction.date.strftime(dateFormat),\
                                transaction.payee or defaultPayee)
    if len(transaction.splits) == 0:
        transaction.splits.append(AmountSplit(**transaction.__dict__))
    for split in transaction.splits:
        if split.amount < 0:
            accountLine = accountPrefix + ':' + split.to_account \
                          if split.to_account else expencesPrefix + ':'\
                                   + (split.category or defaultCategory)
            amount = split.amount*-1
        else:
            accountLine = accountPrefix + ':' + accountName
            amount = split.amount
        result += '    {}  {}{}\n'.format(accountLine, \
                   str(amount).rjust(74-len(accountLine)), memo2comment(split.memo))

    if transaction.amount < 0:
        accountLine = accountPrefix + ':' +  accountName
        amount = transaction.amount
    else:
        if transaction.to_account:
            return ''
        accountLine = incomePrefix + ':' +  (transaction.category or defaultCategory)
        amount = -1*transaction.amount
    return result + '    ' + accountLine + '  ' + str(amount).rjust(74-len(accountLine)) + '\n\n'


qif = QifParser.parse(open('cash.qif'))

for account in qif.get_accounts():
    transactions = account.get_transactions()
    for transaction in transactions[0]:
        print(transaction2ledger(transaction, account.name))
