import pandas as pd
import requests
from datetime import datetime

def create_total_col(df, balance_col):
    restructured_df = pd.DataFrame(index=df['date'].unique())

    for account_id in df['account_id'].unique():
        df_subset = df[df['account_id']==account_id][[balance_col,'date']].set_index('date')    
        restructured_df[account_id] = df_subset

    restructured_df.sort_index(inplace=True)
    restructured_df.interpolate(method='time', inplace=True)

    restructured_df['total'] = restructured_df.sum(axis=1)
    restructured_df['name_account'] = 'Total'
    restructured_df['date'] = restructured_df.index
    restructured_df.rename(columns={'total':balance_col}, inplace=True)
    
    df = df.append(restructured_df[['name_account', 'date', balance_col]])
    
    return df

def compile_records(client, records, accounts, labels):

    compiled_df = records.merge(
        accounts.to_pandas(), 
        how='left', 
        left_on='account_id', 
        right_on='id', 
        suffixes=('_record', '_account')
    )

    compiled_df = compiled_df.merge(
        labels.to_pandas(), 
        how='left', 
        left_on='label_id', 
        right_on='id', 
        suffixes=('_account', '_label')
    )
    
    return compiled_df


def get_sparebank1_balances(auth, account_id_mapping):
    '''Retrieves all Sparebank1 account balances and returns subset of information
    
    Args:
        auth (str): Bearer token for Sparebank1 API
        account_mapping (dict): mapping for each account between 
            key = api_account_id 
            value = db_account_id
        
    Returns:
        (list of dict): filtered API response with balances for all accounts
    
    '''
    
    url = "https://api.sparebank1.no/open/personal/banking/accounts/all"
    response = requests.request("GET", url, headers={'Authorization': auth}).json()
    filtered_response = [
        {
            'name':account['description'],
            'api_account_id':account['id'],
            'balance':account['balance']['amount'], 
            'currency':account['balance']['currencyCode'],
            'datetime':datetime.now()
        }
        for account in response['accounts']
    ]
    
    for account in filtered_response:
        account['db_account_id'] = account_id_mapping[account['api_account_id']]
    
    return filtered_response


def auto_retrieve_account_data(auto_details):
    '''Retrieve all accounts as specified in auto_details
    
    Args:
        auto_details (dict): requires keys ('name', 'account-mapping', 'function')
        
    Returns:
        (dict): relevant details for each account balance, including ids
            keys = 'name', 'balance', 'api_account_id', 
                'currency', 'datetime', 'db_account_id'
    '''
    
    balances = []
    
    for method in auto_details:
        
        function = method['function']
        balances += globals()[function['name']](**function['args'])
        
    return balances