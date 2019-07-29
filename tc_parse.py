""" Test parse script for time clock transactions in DD XML files """
import sys
import xml.etree.ElementTree as et
from TimeClockTransaction import *
from DDDB import *
import logging

# Setup logging
# Define format for formatter
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# Define logger with name __name__. Set level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define log file and set formatting for file entries
file_handler = logging.FileHandler('/home/gene/log/DD/timeclocktx.log')
file_handler.setFormatter(formatter)

# Add file handler to logger
logger.addHandler(file_handler)


def send_to_db(tc_transactions):
    """ Sends each time clock transaction to the database """
    db = DDDB()

    for transaction in tc_transactions:
        # Is it a new clock in?
        if transaction.send_count == 1:
            #print("clockin:")
            #print("{} {}".format(transaction.staff_name, transaction.send_count))
            db.clock_in(transaction.staff_id, transaction.clock_in_time)
        else:
            #print("something else clock:")
            #print("{} {}".format(transaction.staff_name, transaction.send_count))
            db.update_clock_in(transaction.staff_id, transaction.clock_in_time, transaction.clock_out_time)


def main():
    # Check for file(s), skip first arg because it's this file's name
    cmdline_args = sys.argv[1:]
    # No files? Error message and quit
    if not cmdline_args:
        print("Usage: {} filename1 filename2 ... filenameXX".format(sys.argv[0]))
        exit()

    # List of time clock transactions from files
    trans_list = []

    # Parse each file
    for file in cmdline_args:

        # Write to log
        logger.info("TimeClockTransactions in file: {}".format(file))

        tree = et.parse(file)
        root = tree.getroot()

        # Build a list of all Time Clock transactions in this file
        tc_trans = []
        for trans in root.findall('./TRANSACTION'):
            trans_type = trans.find('./TRANSACTIONTYPE_DESC').text
            if trans_type == 'Time Clock':
                tc_trans.append(trans)

        # Process Time Clock transactions
        for trans in tc_trans:
            staff_id = int(trans.find('./STAFFMEMBER').text)
            staff_name = trans.find('./STAFFMEMBER_NAME').text
            send_count = int(trans.find('./SENDCOUNT').text)
            tx_date = trans.find('./DATE').text
            tx_time = trans.find('./TIME').text

            # Write to log
            logger.debug("\n")
            logger.debug("staff_id: {}".format(staff_id))
            logger.debug("staff_name: {}".format(staff_name))
            logger.debug("send_count: {}".format(send_count))
            logger.debug("tx_date: {}".format(tx_date))
            logger.debug("tx_time: {}".format(tx_time))

            # Check staff id. Must be 1002-1099 or skip
            if not 1099 >= staff_id >= 1002:
                logger.debug("Don't want ID: {}\n".format(staff_id))
                continue

            time_in = trans.find('./TIME_ATTENDANCE/TIMEIN').text
            date_in = trans.find('./TIME_ATTENDANCE/DATEIN').text

            # There may not be a clock out time and date depending on the type of
            # Time Clock transaction. If not, set to None
            try:
                time_out = trans.find('./TIME_ATTENDANCE/TIMEOUT').text
                date_out = trans.find('./TIME_ATTENDANCE/DATEOUT').text
            except AttributeError:
                time_out = None
                date_out = None

            # Write to log
            logger.debug("time_in: {}".format(time_in))
            logger.debug("date_in: {}".format(date_in))
            logger.debug("time_out: {}".format(time_out))
            logger.debug("date_out: {}".format(date_out))

            # Fix date from mm/dd/yyyy hh:mm -> yyyy-mm-dd hh:mm:ss
            (m, d, y) = date_in.split('/')
            fix_time_in = '{}-{}-{} {}:00'.format(y, m, d, time_in)

            if time_out:
                (m, d, y) = date_out.split('/')
                fix_time_out = '{}-{}-{} {}:00'.format(y, m, d, time_out)
            else:
                fix_time_out = time_out

            # Write to log
            logger.debug("fix_time_in: {}".format(fix_time_in))
            logger.debug("fix_time_out: {}".format(fix_time_out))

            tct = TimeClockTransaction(staff_id, staff_name, send_count,
                                       tx_date, tx_time, fix_time_in, fix_time_out)
            trans_list.append(tct)

        # End for trans

    # End for file
    # Write to log
    for t in trans_list:
        logger.info("\n {}".format(t))

    # Send to db
    send_to_db(trans_list)



if __name__ == '__main__':
    main()
