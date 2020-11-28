import pandas as pd

def create_total_col(df, balance_col):
    restructured_df = pd.DataFrame(index=df['date'].unique())

    for account_id in df['account_id'].unique():
        df_subset = df[df['account_id']==account_id][[balance_col,'date']].set_index('date')    
        restructured_df[account_id] = df_subset

    restructured_df.interpolate(inplace=True)

    restructured_df['total'] = restructured_df.sum(axis=1)
    restructured_df['name_account'] = 'Total'
    restructured_df['date'] = restructured_df.index
    restructured_df.rename(columns={'total':balance_col}, inplace=True)
    
    df = df.append(restructured_df[['name_account', 'date', balance_col]])
    
    return df