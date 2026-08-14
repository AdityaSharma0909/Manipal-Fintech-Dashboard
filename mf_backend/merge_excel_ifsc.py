import pandas as pd
import argparse

def merge_ifsc_codes(old_file_path, new_file_path, output_file_path, old_bank_col, new_bank_col, new_ifsc_col):
    print(f"Reading old file: {old_file_path}")
    # Read the old file (handles both .xlsx and .ods)
    if old_file_path.endswith('.ods'):
        df_old = pd.read_excel(old_file_path, engine='odf')
    else:
        df_old = pd.read_excel(old_file_path)
        
    print(f"Reading new file with IFSCs: {new_file_path}")
    df_new = pd.read_excel(new_file_path)
    
    # We only need the bank name and the IFSC code from the new file
    df_new_subset = df_new[[new_bank_col, new_ifsc_col]].copy()
    
    # Filter out rows where IFSC is 'NOT_FOUND' or empty
    df_new_subset = df_new_subset[
        (df_new_subset[new_ifsc_col].notna()) & 
        (df_new_subset[new_ifsc_col] != 'NOT_FOUND') &
        (df_new_subset[new_ifsc_col] != '')
    ]
    
    # Drop duplicates in case the new file has the same bank multiple times
    df_new_subset = df_new_subset.drop_duplicates(subset=[new_bank_col])
    
    print("Merging data...")
    # Perform a left join to bring the IFSC codes into the old dataframe
    # This preserves ALL existing columns and rows from the old file
    df_merged = pd.merge(
        df_old, 
        df_new_subset, 
        left_on=old_bank_col, 
        right_on=new_bank_col, 
        how='left'
    )
    
    # If the old file already had an 'IFSC Code' column and you want to UPDATE it:
    # df_merged['Old IFSC Column'] = df_merged['Old IFSC Column'].fillna(df_merged[new_ifsc_col])
    
    # If the bank name columns had different names, drop the extra one from the new file
    if old_bank_col != new_bank_col:
        df_merged = df_merged.drop(columns=[new_bank_col])
        
    print(f"Saving updated data to: {output_file_path}")
    df_merged.to_excel(output_file_path, index=False)
    print("Done!")

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Update these paths and column names to match your exact files
    
    OLD_EXCEL_FILE = r"old_file.xlsx"
    NEW_EXCEL_FILE = r"CUSTOMER_BANK_ACCOUNT_with_IFSC.xlsx"
    OUTPUT_FILE = r"updated_old_file_with_ifsc.xlsx"
    
    # The column name in the old file that contains the bank name
    OLD_BANK_COLUMN = "Name" 
    
    # The column name in the new file that contains the bank name
    NEW_BANK_COLUMN = "Name"
    
    # The column name in the new file that contains the IFSC code
    NEW_IFSC_COLUMN = "IFSC Code"
    
    # Uncomment the following line to run the script:
    # merge_ifsc_codes(OLD_EXCEL_FILE, NEW_EXCEL_FILE, OUTPUT_FILE, OLD_BANK_COLUMN, NEW_BANK_COLUMN, NEW_IFSC_COLUMN)
