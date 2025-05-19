import pandas as pd
import re
from rapidfuzz import process, fuzz


def our_data():
    __placeholder__ = r"GitHub.xlsx"
    df_our_data = pd.read_excel(r"__placeholder__", sheet_name='Export')

    return df_our_data


def name_loop(df_our_data):
    #count = 0
    # prepare list of names and a lowercased version for matching
    our_names = df_our_data['Partner Name'].dropna().astype(str).tolist()
    lower_our_names = [name.lower() for name in our_names]

    # add lower-case Partner Name column for fast matching back to dataframe rows
    df_our_data['_lower_partner_name'] = df_our_data['Partner Name'].str.lower()

    # clean and deduplicate comp. names from Account Name column
    their_names = (
        df_our_data['Account Name']
        .dropna()
        .astype(str)
        .str.strip()
    )
    their_names = their_names[their_names != ""].drop_duplicates().tolist()

    # prepare the formatted address column once
    df_our_data['Formatted_address'] = (
        df_our_data['Partner Address'].fillna('') + '\n' +
        df_our_data['Partner Post Code'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True) + ' ' +
        df_our_data['Partner City'].fillna('').str.title() + '\n' +
        df_our_data['Partner Country Code'].fillna('')
    )

    best_matches = []

    for idx1, name1 in enumerate(their_names):
        #count += 1
        if idx1 % 200 == 0:
            print(f"Processing {idx1} / {len(their_names)} names...")

        name1_lower = name1.lower()
        best_match = process.extractOne(name1_lower, choices=lower_our_names, scorer=fuzz.token_sort_ratio)

        matching_rows = df_our_data[df_our_data['Account Name'].str.strip() == name1]

        if matching_rows.empty:
            # if no matching row found, skip or assign defaults
            their_code = None
            their_addy = ''
            their_city = ''
            their_postcode = None
        else:
            # use first matching row for their address info
            their_row = matching_rows.iloc[0]
            their_code = their_row.get('External ID')
            their_addy = str(their_row.get('Address 1', ''))
            their_city = their_row.get('Address 1: City', '')
            postcode_match = re.search(r'\b\d{4}\b', their_addy)
            their_postcode = postcode_match.group(0) if postcode_match else None
            channel = their_row.get('Channel', '')
            sub_channel = their_row.get('Sub Channel', '')

        if best_match:
            best_match_name, score, _ = best_match
            matched_idx = df_our_data[df_our_data['_lower_partner_name'] == best_match_name].index

            if not matched_idx.empty:
                matched_row = df_our_data.loc[matched_idx[0]]
                our_code = matched_row.get('Partner Code')
                formatted_address = matched_row['Formatted_address']
                our_addy = matched_row.get('Partner Address')
                our_postcode = matched_row.get('Partner Post Code')
                our_city = matched_row.get('Partner City')
                our_countrycode = matched_row.get('Partner Country Code')
            else:
                our_code = formatted_address = our_addy = our_postcode = our_city = our_countrycode = None

            address_score = 0
            if score < 101 and their_addy and formatted_address:
                address_score = fuzz.token_sort_ratio(their_addy.lower(), formatted_address.lower())

            best_matches.append((
                name1, their_code, their_addy, their_postcode, their_city,
                best_match_name, our_code, formatted_address, our_addy,
                our_postcode, our_city, our_countrycode, channel, sub_channel,
                score, address_score
            ))
        else:
            best_matches.append((
                name1, their_code, their_addy, their_postcode, their_city,
                None, None, None, None, None, None, None, None, None,
                0, 0
            ))
        #if count == 200:
            #break

    results_df = pd.DataFrame(best_matches, columns=[
        'their name', 'their code', 'their address', 'their postcode',
        'their city', 'our matched name', 'our code', 'formatted_address',
        'our address', 'our postcode', 'our city', 'our country code', 'Channel', 'Sub Channel',
        'Match_Percentage', 'Match_Address_Score'
    ])
    results_df['95+ Confirmed_Match'] = (
        (results_df['Match_Percentage'] > 95) & 
        (results_df['Match_Address_Score'] > 95)
    ).astype(int)
    results_df['175+ Combined'] = ((results_df['Match_Percentage'] +  results_df['Match_Address_Score']) > 175).astype(int)

    results_df = results_df[[
        'their name', 'their address', 'their city', 'our matched name',
        'formatted_address', 'our city', 'our code', 'Channel', 'Sub Channel', 'Match_Percentage', 'Match_Address_Score', 
        '95+ Confirmed_Match', '175+ Combined'
    ]].sort_values(by='Match_Percentage', ascending=False)

    return results_df


def main():
    df_our_data = our_data()
    print("Our data loaded.")
    results_df = name_loop(df_our_data)
    print("Comparison completed.")
    
    return results_df

def save_results(results_df):
    results_df.to_excel(r'GitHub.xlsx', index=False)


results_df = main()
save_results(results_df)
