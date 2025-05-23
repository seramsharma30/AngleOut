import pandas as pd


def sum_finder(data_frame, col_name):
    # Calculate the total sum of the specified column
    total = data_frame[col_name].sum()

    if 1000000 > total >= 9999:
        total_k = total / 1000
        return f"{total_k:.0f}K" if total_k.is_integer() else f"{total_k:.2f}K"
    
    elif total >= 1000000:
        total_m = total / 1000000
        return f"{total_m:.0f}M" if total_m.is_integer() else f"{total_m:.2f}M"
    
    
    
    return total