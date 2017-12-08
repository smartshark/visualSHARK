#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score


DROP_METRICS = ['class_Runtime Rules',
 'interface_Runtime Rules',
 'method_HCPL',
 'method_HDIF',
 'method_HEFF',
 'method_HNDB',
 'method_HPL',
 'method_HPV',
 'method_HTRP',
 'method_HVOL',
 'method_MI',
 'method_MIMS',
 'method_MISEI',
 'method_MISM',
 'method_Runtime Rules']
# also interfaces are NaN
DROP_METRICS += ['interface_AD',
 'interface_CBO',
 'interface_CBOI',
 'interface_CC',
 'interface_CCL',
 'interface_CCO',
 'interface_CD',
 'interface_CI',
 'interface_CLC',
 'interface_CLLC',
 'interface_CLOC',
 'interface_DIT',
 'interface_DLOC',
 'interface_LCOM5',
 'interface_LDC',
 'interface_LLDC',
 'interface_LLOC',
 'interface_LOC',
 'interface_NA',
 'interface_NG',
 'interface_NII',
 'interface_NL',
 'interface_NLA',
 'interface_NLE',
 'interface_NLG',
 'interface_NLM',
 'interface_NLPA',
 'interface_NLPM',
 'interface_NLS',
 'interface_NM',
 'interface_NOA',
 'interface_NOC',
 'interface_NOD',
 'interface_NOI',
 'interface_NOP',
 'interface_NOS',
 'interface_NPA',
 'interface_NPM',
 'interface_NS',
 'interface_PDA',
 'interface_PUA',
 'interface_RFC',
 'interface_Runtime Rules',
 'interface_TCD',
 'interface_TCLOC',
 'interface_TLLOC',
 'interface_TLOC',
 'interface_TNA',
 'interface_TNG',
 'interface_TNLA',
 'interface_TNLG',
 'interface_TNLM',
 'interface_TNLPA',
 'interface_TNLPM',
 'interface_TNLS',
 'interface_TNM',
 'interface_TNOS',
 'interface_TNPA',
 'interface_TNPM',
 'interface_TNS',
 'interface_WMC']

DROP_METRICS += ['enum_AD',
 'enum_CBO',
 'enum_CBOI',
 'enum_CC',
 'enum_CCL',
 'enum_CCO',
 'enum_CD',
 'enum_CI',
 'enum_CLC',
 'enum_CLLC',
 'enum_CLOC',
 'enum_DIT',
 'enum_DLOC',
 'enum_LCOM5',
 'enum_LDC',
 'enum_LLDC',
 'enum_LLOC',
 'enum_LOC',
 'enum_NA',
 'enum_NG',
 'enum_NII',
 'enum_NL',
 'enum_NLA',
 'enum_NLE',
 'enum_NLG',
 'enum_NLM',
 'enum_NLPA',
 'enum_NLPM',
 'enum_NLS',
 'enum_NM',
 'enum_NOA',
 'enum_NOC',
 'enum_NOD',
 'enum_NOI',
 'enum_NOP',
 'enum_NOS',
 'enum_NPA',
 'enum_NPM',
 'enum_NS',
 'enum_PDA',
 'enum_PUA',
 'enum_RFC',
 'enum_Runtime Rules',
 'enum_TCD',
 'enum_TCLOC',
 'enum_TLLOC',
 'enum_TLOC',
 'enum_TNA',
 'enum_TNG',
 'enum_TNLA',
 'enum_TNLG',
 'enum_TNLM',
 'enum_TNLPA',
 'enum_TNLPM',
 'enum_TNLS',
 'enum_TNM',
 'enum_TNOS',
 'enum_TNPA',
 'enum_TNPM',
 'enum_TNS',
 'enum_WMC']


def combine(tlist):
    ret = []
    for tl in tlist:
        ret += tl['product']
    return pd.DataFrame(ret)


def drop_metrics(df):
    drop = []
    for col in df.columns:
        if col in DROP_METRICS:
            drop.append(col)
    return df.drop(drop, axis=1)


def predict(train, test, prediction_type='NB'):
    train = combine(train)
    test = combine(test)

    # first drop columns that are NaN everywhere
    train = drop_metrics(train)
    test = drop_metrics(test)

    train = train.dropna()
    test = test.dropna()

    train_data = train.drop(['long_name', 'bugs', 'label'], axis=1).values
    train_labels = train['label'].values

    test_data = test.drop(['long_name', 'bugs', 'label'], axis=1).values
    test_labels = test['label'].values

    if prediction_type == 'NB':
        c = GaussianNB()

    elif prediction_type == 'LR':
        c = LogisticRegression()

    c.fit(train_data, train_labels)
    pred_labels = c.predict(test_data)

    results = []
    for i, l in enumerate(pred_labels):
        row = test.iloc[i]
        results.append({'long_name': row['long_name'], 'bugs': row['bugs'], 'label': l})

    return {'product': results}


def predict_evaluate(train, test, prediction_type='NB'):
    train = combine(train)
    test = combine(test)

    # first drop columns that are NaN everywhere
    train = drop_metrics(train)
    test = drop_metrics(test)

    train = train.dropna()
    test = test.dropna()

    train_data = train.drop(['long_name', 'bugs', 'label'], axis=1).values
    train_labels = train['label'].values

    test_data = test.drop(['long_name', 'bugs', 'label'], axis=1).values
    test_labels = test['label'].values

    if prediction_type == 'NB':
        c = GaussianNB()

    elif prediction_type == 'LR':
        c = LogisticRegression()

    c.fit(train_data, train_labels)
    pred_labels = c.predict(test_data)

    auc_score = roc_auc_score(test_labels, pred_labels)
    prec = precision_score(test_labels, pred_labels)
    rec = recall_score(test_labels, pred_labels)

    return {'auc': auc_score, 'precision': prec, 'recall': rec}
