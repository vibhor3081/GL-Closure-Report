import base64
import dateutil
import mysql.connector as sql
import os
import pandas as pd
import streamlit as st
import ruamel.yaml as yaml
import lib
import deetly as dl

db_config = dict([
    ('hostname', 'canvasdb.caxvr8jox9y6.us-east-2.rds.amazonaws.com'),
    ('port', 3306),
    ('username', 'admin'),
    ('password', '77YnH0bqO8oHMYZGmu78'),
    ('database', 'Vriddhi')
])

st.set_page_config(layout="wide")

DATA_DIR = 'DataFiles'
# creds = 'credentials.yaml'
# with open(creds) as infile:
#     config = yaml.load(infile.read(), Loader=yaml.Loader)
#     db_config = config['mysql']

TRANSACTIONS_TABLE = 'N_Account_State'
ACCOUNTS_TABLE = 'NewDB_Account'
MEMBER_TABLE = 'NewDB_User'

# these are the columns from a dataframe that we'll show. These come from the database table
TRANSACTION_COLUMNS = """AccountNumber
                         DateOfUpdate
                         Balance_OB
                         Overdue_OB
                         RegBalance_OB
                         RegCharge
                         PenalCharge
                         TotalCharge
                         TotalDue
                         EMIDue
                         TransferIn_CB
                         TransferOut_CB
                         Balance_CB
                         RegBalance_CB
                         Overdue_CB
                      """.split()

# st.image(os.path.join(DATA_DIR, 'vriddhi_logo.png'))
memberID = st.text_input("Member ID")
AccountType = st.text_input("Account Type")

st.sidebar.multiselect('Select account details you want to view', TRANSACTION_COLUMNS)

conn = sql.connect(host=db_config['hostname'], port=db_config['port'], user=db_config['username'], password=db_config['password'], database=db_config['database'])

if memberID:
    info = lib.queryTable(conn, MEMBER_TABLE, 'MemNum', memberID)
    info = info.to_dict('records')[0]
    container = st.beta_container()
    container.write(f"**Member Number**: {info['MemNum']}")
    container.write(f"**Name**: {info['MemName']}")
    container.write(f"**Field Officer**: {info['FieldOfficer']}")
    container.write(f"**Center ID**: {info['CenterName']}")
    container.write(f"**Mobile Number**: {str(info['RegMobile'])}")

    st.markdown('---')

    accounts = lib.queryTableNew(conn, ACCOUNTS_TABLE, 'MemNum', memberID, 'AccountType',AccountType)  # get all the accounts this member has
    for accNum in accounts.AccountNumber.unique():
        expanders = [st.beta_expander(f"Account Number: {accNum}")]

    transactionSpace = st.beta_container()
    for expander, account in zip(expanders, accounts.AccountNumber.unique()):  # for each account
        with expander:
            st.write(f"""**Account Number**: {str(account)}""")
            st.write(f"""**Account Type**: {str(accounts[accounts.AccountNumber==account].iloc[0].AccountType)}""")
            df = lib.queryTable(conn, TRANSACTIONS_TABLE, 'AccountNumber', account)
            df = df[df.AccountNumber == account]
            df.sort_values(by='DateOfUpdate', inplace=True)

            for colname in 'MemNum AccountNumber'.split():
                df.drop(colname, axis=1, inplace=True)

            DF = df

            for month in df.DateOfUpdate.unique():
                st.write(month)
                df = DF[DF.DateOfUpdate == month]
                df.sort_values(by='DateOfUpdate'.split(), inplace=True, ignore_index=True)
                df.fillna(value='', inplace=True)

                displayCols = ["Balance_OB Overdue_OB RegBalance_OB".split(),
                               "RegCharge PenalCharge TotalCharge".split(),
                               "TotalDue EMIDue PenalCharge Overdue_OB".split(),
                               "TransferIn_CB TransferOut_CB".split(),
                               "Balance_CB RegBalance_CB Overdue_CB".split(),
                               ]
                cols = st.beta_columns(len(displayCols))
                for col, colnames in zip(cols, displayCols):
                    with col:
                        st.write(df[colnames].T)
