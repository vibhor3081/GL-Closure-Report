import base64
import dateutil
import mysql.connector as sql
import os
import pandas as pd
import streamlit as st
import ruamel.yaml as yaml
import lib
import deetly as dl
import numpy as np
import streamlit.components.v1 as components
#from pandas_profiling import ProfileReport

db_config = dict([
    ('hostname', 'canvasdb.caxvr8jox9y6.us-east-2.rds.amazonaws.com'),
    ('port', 3306),
    ('username', 'admin'),
    ('password', '77YnH0bqO8oHMYZGmu78'),
    ('database', 'Vriddhi')
])

st.set_page_config(layout="wide")

DATA_DIR = 'DataFiles'


TRANSACTIONS_TABLE = 'N_Transaction'
STATE_TABLE = 'N_Account_State'
ACCOUNTS_TABLE = 'NewDB_Account'
#GL_ACC_STATE_TABLE = 'NewDB_Account_GL_State'
GL_ACC_TABLE = 'NewDB_Account_GL'
#SSA_ACC_TABLE = 'NewDB_Account_SSA_State'
#COT_ACC_TABLE = 'NewDB_Account_COT_State'
MEMBER_TABLE = 'NewDB_User'


GL_STATE_COLUMNS = """Balance_CB
                      TotalDue
                      LoanAmount
                      Date_Closure              
                   """.split()

SSA_STATE_COLUMNS = """Balance_CB
                    """.split()

COT_STATE_COLUMNS = """Balance_CB
                    """.split()

AccountType = "GL"

memberID = st.text_input("Member ID")

trans_details = GL_STATE_COLUMNS

ssa_details = SSA_STATE_COLUMNS

cot_details = COT_STATE_COLUMNS

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
    if not accounts.empty:

        for expander, account in zip(expanders, accounts.AccountNumber.unique()):  # for each account

            with expander:

                st.write(f"""**Account Number**: {str(account)}""")
                st.write(f"""**Account Type**: {str(accounts[accounts.AccountNumber==account].iloc[0].AccountType)}""")
                df1 = lib.queryTable(conn, STATE_TABLE, 'AccountNumber', account)
                df1 = df1[df1.AccountNumber == account]
                df1 = df1.sort_values(by='DateOfUpdate', ascending=True, inplace=False, na_position='last')
                df1 = df1.tail(1)



                df2 = lib.queryTable(conn, GL_ACC_TABLE, 'AccountNumber', account)
                df2 = df2[df2.AccountNumber == account]
                df2 = df2.tail(1)
                st.write("Closure Date", df2[['Date_Closure']], "Loan Amount", df2[['LoanAmount']])
                print(df2)
                #st.write("Loan Closure Date", df2['DateClosure'])

                df5 = pd.read_sql(f"SELECT * FROM N_Transaction WHERE AccountNumber = '{account}'",
                                  conn)

                account = memberID + "-" + "SSA"



                #df1 = df1.append(df2)


                DF = df1

                df1.fillna(value='', inplace=True)

                displayCols = trans_details

                #cols = st.beta_columns(len(displayCols))
                #for col, colnames in zip(cols, displayCols):

                #    with col:

                #        st.write(df1[colnames])

                displayCols = ssa_details

                df3 = lib.queryTable(conn, STATE_TABLE, 'AccountNumber', account)
                df3 = df3[df3.AccountNumber == account]
                df3 = df3.sort_values(by='DateOfUpdate', ascending=True, inplace=False, na_position='last')
                df3 = df3.tail(1)

                df1 = df1.append(df3)
                #cols = st.beta_columns(len(displayCols))

                #for col, colnames in zip(cols, displayCols):

                #    with col:

                #        st.write(df3[colnames].T)

                account = memberID + "-" + "COT"

                displayCols = cot_details

                df4 = lib.queryTable(conn, STATE_TABLE, 'AccountNumber', account)
                df4 = df4[df4.AccountNumber == account]
                df4 = df4.sort_values(by='DateOfUpdate', ascending=True, inplace=False, na_position='last')
                df4 = df4.tail(1)

                df1 = df1.append(df4)

                print(df1)

                df1.fillna("0")

                st.title("Gold Loan COT and SSA Details")

                st.table(df1[['AccountNumber', 'Balance_CB', 'TotalDue']])

                #cols = st.beta_columns(len(displayCols))
                #st.table(df4)

                #for col, colnames in zip(cols, displayCols):
                #    with col:
                #        st.table(df4[colnames].T)

                df5 = df5.sort_values(by='Date', ascending=True, inplace=False, na_position='last')

                st.title("GL Transaction History")

                st.table(df5)


