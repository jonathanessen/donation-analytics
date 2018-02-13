from sys import argv
from datetime import date, timedelta
from math import ceil
from numpy import array

def process_donation(recipient_id, donor_name, donor_zip, transact_date,
                     transact_amt, transact_id):
    '''
    Index the transaction in the hash tables
    '''
    donor_key = (donor_name, donor_zip)
    if donor_key in transactions_by_donor:
        is_repeat = check_repeat(transact_date, donor_key)
    else:
        is_repeat = False
    
    transactions_by_id[transact_id] = {'donor_name': donor_name,
                                       'donor_zip' : donor_zip,
                                       'transact_date': transact_date,
                                       'transact_amt': transact_amt,
                                       'recipient_id': recipient_id,
                                       'is_repeat': is_repeat}
    
    recipient_date_zip_repeat_key = (recipient_id, transact_date, donor_zip, is_repeat)
    
    if recipient_date_zip_repeat_key not in transactions_by_recipient_date_zip_repeat:
        transactions_by_recipient_date_zip_repeat[
            recipient_date_zip_repeat_key] = [transact_id]
    else:
        transactions_by_recipient_date_zip_repeat[
            recipient_date_zip_repeat_key].append(transact_id)
    
    if donor_key not in transactions_by_donor:
        transactions_by_donor[donor_key] = [transact_id]
    else:
        transactions_by_donor[donor_key].append(transact_id) 
        
def check_repeat(current_transact_date, donor_key):
    '''
    Check if the current transaction is a repeat
    '''
    is_repeat = False
    
    for tid in transactions_by_donor[donor_key]:
        if (transactions_by_id[tid]['transact_date'] <= current_transact_date):
            is_repeat = True
    
    return is_repeat

def get_date_from_string(date_string):
    '''
    Convert mmddyyyy string to datetime.date object
    '''
    if len(date_string) == 8:
        try:
            contrib_date = date(year=int(date_string[4:]),
                                month=int(date_string[:2]),
                                day=int(date_string[2:4]))
        except:
            contrib_date = None
    else:
        contrib_date = None
        
    return contrib_date

def timedelta_cyear(transact_date, cyears):
    '''Return the timedelta between transaction_date and transaction_date + cyears'''
    return (date(transact_date.year + cyears, transact_date.month, transact_date.day)
            - transact_date)

def days_elapsed(start_date, end_date):
    '''Return the number of days elapsed between start_date and end_date'''
    return int((end_date - start_date) / timedelta(days=1))

def dates_in_past_cyear(current_date):
    '''Return all the dates contained in the past calendar year, including current_date'''
    current_date_minus_one_cyear = current_date + timedelta_cyear(current_date, -1)
    day_count = days_elapsed(current_date_minus_one_cyear, current_date)
    return [current_date_minus_one_cyear + d * timedelta(days=1)
            for d in range(day_count + 1)]

def percentile(pctl, data_values):
    """Return the percentile"""
    idx = ceil((pctl / 100.) * data_values.size) - 1
    data_values.partition(idx)
    return data_values[idx]


if __name__ == "__main__":
    itcont_filename = argv[1]
    percentile_filename = argv[2]
    repeat_donors_filename = argv[3]
    
    transact_id = 0
    transactions_by_id = {}
    transactions_by_donor = {}
    transactions_by_recipient_date_zip_repeat = {}

    with open(percentile_filename) as percentile_file:
        percentile_value = int(percentile_file.read())

    with open(itcont_filename, mode="r") as itcont_file, \
         open(repeat_donors_filename, mode="w") as repeat_donors_file:
        for itcont_line in itcont_file:
            line = itcont_line.split('|')
            recipient_id_string = line[0]
            donor_name_string = line[7]
            donor_zip_string = line[10]
            contrib_date_string = line[13]
            contrib_amount_string = line[14]
            other_id_string = line[15]

            if recipient_id_string != "":
                recipient_id = recipient_id_string
            else:
                continue

            if donor_name_string != "":
                donor_name = donor_name_string
            else:
                continue

            try:
                if len(donor_zip_string) >= 5:
                    int(donor_zip_string[:5]) # throws error if non-int
                    donor_zip = donor_zip_string[:5]
                else:
                    continue
            except:
                continue

            contrib_date = get_date_from_string(contrib_date_string)
            if contrib_date == None:
                continue

            try:
                contrib_amount = float(contrib_amount_string)
            except:
                continue

            if other_id_string != "":
                continue

            # Index the transaction
            transact_id += 1
            donation_info = (recipient_id, donor_name, donor_zip,
                             contrib_date, contrib_amount)
            process_donation(*donation_info, transact_id)

            if transactions_by_id[transact_id]['is_repeat'] == True:
                # Collect data on repeat donations
                dates = dates_in_past_cyear(contrib_date)
                keys = [(recipient_id, d, donor_zip, True) for d in dates]
                tids = [tid for k in keys 
                        if k in transactions_by_recipient_date_zip_repeat
                        for tid in transactions_by_recipient_date_zip_repeat[k]]
                repeat_contrib_amounts = array([
                    transactions_by_id[t]['transact_amt'] for t in tids])

                # Do the computations
                repeat_contrib_total = int(round(repeat_contrib_amounts.sum()))
                repeat_contrib_percentile = int(round(
                    percentile(percentile_value, repeat_contrib_amounts)))

                # Write results to output file
                repeat_donors_file.write(recipient_id + '|'
                                         + donor_zip + '|'
                                         + str(contrib_date.year) + '|'
                                         + str(repeat_contrib_percentile) + '|'
                                         + str(repeat_contrib_total) + '|'
                                         + str(len(tids)) + '\n')