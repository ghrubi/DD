""" Test parse script for order transactions in DD XML files """
from Order import *
import sys
import xml.etree.ElementTree as et
from DDDB import *
import re
import logging

# Setup logging
# Define format for formatter
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# Define logger with name __name__. Set level
logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

# Define log file and set formatting for file entries
file_handler = logging.FileHandler('/home/gene/log/DD/ordertx.log')
file_handler.setFormatter(formatter)

# Add file handler to logger
logger.addHandler(file_handler)


def send_to_db(ck_transactions):
    """ Sends each order transaction to the database """
    db = DDDB()

    db.add_orders(ck_transactions)


def main():
    # Check for file(s), skip first arg because it's this file's name
    cmdline_args = sys.argv[1:]
    # No files? Error message and quit
    if not cmdline_args:
        print("Usage: {} filename1 filename2 ... filenameXX".format(sys.argv[0]))
        exit()

    # List of Orders retrieved from files
    orders = []

    # Parse each file
    for file in cmdline_args:

        # Write to log
        logger.info("CheckTransactions in file: {}".format(file))

        tree = et.parse(file)
        root = tree.getroot()

        # Build a list of all check transactions in this file
        ck_trans = []
        for trans in root.findall('./TRANSACTION'):
            trans_type = trans.find('./TRANSACTIONTYPE_DESC').text
            if trans_type == 'Check':
                ck_trans.append(trans)

        # Get all transactions
        for trans in ck_trans:
            # If check send count is 2 or greater, it's an update to a check.
            # I'll deal with the send count later.
            check_send_count = int(trans.find('./SENDCOUNT').text)
            #if check_send_count > 1:
            #    continue

            # It looks like deleted checks have a send count of 1 and a cover count of 0. Skip.
            # Also, this could be screwed up checks, generally. I'll deal with it later so I can get some
            # logging of the entire set of data.
            check_cover_count = int(trans.find('./CHECK/COVERCOUNT').text)
            #if check_send_count == 1 and check_cover_count == 0:
            #    continue

            # Collect data elements that we need from the check section
            check_num = int(trans.find('./CHECK/CHECKNUMBER').text)
            check_date = trans.find('./CHECK/DATEOPENED').text
            check_time = trans.find('./CHECK/TIMEFIRSTORDER').text

            # Fix date-time. mm/dd/yyyy hh:mm -> yyyy-mm-dd hh:mm:00
            (m, d, y) = check_date.split('/')
            check_date = '{}-{}-{} {}:00'.format(y, m, d, check_time)

            # In case of malformed XML. Found that CUSTOMERNAME is missing sometimes. Fuck you, DD!
            try:
                check_name = trans.find('./CHECK/CUSTOMERNAME').text
            except AttributeError:
                check_name = "Unknown"

            # Clean up check name in case there's shit in it.
            check_name = re.sub(r'[$#@~!&*()\[\];.,:?^`\\/]', '', check_name)

            check_tax = float(trans.find('./CHECK/TAX').text)
            check_amt = float(trans.find('./CHECK/CHECKTOTAL').text) - float(check_tax)

            # It looks like deleted checks have a send count of 1 and a cover count of 0. Skip.
            # Or, the check could just be screwed up. Log and skip.
            if check_send_count == 1 and check_cover_count == 0:
                logger_out_str = "\nCheck has Send Count of 1 and Cover Count of 0. Skipping."
                logger_out_str += "\n Check#: {}"
                logger_out_str += "\n Check Date: {}"
                logger_out_str += "\n Check time: {}"
                logger_out_str += "\n Name: {}"
                logger_out_str += "\n Send Count: {}"
                logger_out_str += "\n Cover Count: {}"
                logger_out_str += "\n Check Amount: {}"
                logger_out_str += "\n Check Tax: {}"
                logger.info(logger_out_str.format(check_num, check_date, check_time, check_name,
                                                  check_send_count, check_cover_count, check_amt, check_tax))

                # Skip to next trans.
                continue

            # Move to receipt section of transaction to get the payment type(Cash, credit card, etc.)
            # Sometime receipt section isn't present for some reason, handle. Fuck you DD!
            try:
                check_type = trans.find('./RECEIPT/PROFITCENTER_DESC').text
                check_pay_type = trans.find('./RECEIPT/RECEIPTTYPE_DESC').text
            except AttributeError:
                logger_out_str = "\nMissing RECEIPT Section. Skipping."
                logger_out_str += "\n Check#: {}"
                logger_out_str += "\n Check Date: {}"
                logger_out_str += "\n Check time: {}"
                logger_out_str += "\n Name: {}"
                logger_out_str += "\n Send Count: {}"
                logger_out_str += "\n Cover Count: {}"
                logger_out_str += "\n Check Amount: {}"
                logger_out_str += "\n Check Tax: {}"
                logger.info(logger_out_str.format(check_num, check_date, check_time, check_name,
                                                  check_send_count, check_cover_count, check_amt, check_tax))

                # Skip to next trans.
                continue

            # End try/except AttributeError

            # Write to log
            logger.debug("Check#: {}".format(check_num))
            logger.debug("Check Date: {}".format(check_date))
            logger.debug("Send Count: {}".format(check_send_count))
            logger.debug("Cover Count: {}".format(check_cover_count))
            logger.debug("Check Time: {}" .format(check_time))
            logger.debug("Fixed Date: {}".format(check_date))
            logger.debug("Name: {}".format(check_name))
            logger.debug("Tax: {}".format(check_tax))
            logger.debug("Check Amount: {}".format(check_amt))
            logger.debug("Check Type: {}".format(check_type))
            logger.debug("Paid: {}".format(check_pay_type))

            # If send count is 1, it's a new order.
            if check_send_count == 1:
                check_is_new = True

            # If the send count is 2 and cover count is 1, it maybe a messed up check coming for round 2.
            # The guess is that a send count of 1, but cover count of 0 is an incomplete check somehow. Maybe this
            # is the fixed/completed version. We'll see.
            # This may also be an updated check and that's why the send count is 2. Set check to not new, and
            # let the DB update function deal with whether it's new or and update.
            elif (check_send_count, check_cover_count) == (2, 1):
                logger.info("It's a check with send count 2 and cover count 1. Set to updated check. The DB will deal.")
                check_is_new = False

            # If the send count is 2 and cover count is 0 with a check amount of $0.00, it's a voided check.
            elif (check_send_count, check_cover_count, check_amt) == (2, 0, 0):
                logger.info("It's an update to an order. Void check.")
                check_is_new = False

            # Otherwise, it's something else entirely. Skip.
            else:
                continue

            # Create new Order object
            order = Order(check_num, check_date, check_name, check_amt, check_tax, check_type,
                          check_pay_type, check_is_new)

            # Grab individual items for the check. They're located in the order sections
            for item in trans.findall('./ORDER'):

                # Some items have no item code descriptions. When they don't,
                # skip them.
                try:
                    item_desc = item.find('./ITEMCODE_DESC').text
                except AttributeError:
                    continue

                item_quantity = int(item.find('./ITEMQUANTITY').text)
                item_price = float(item.find('./ITEMPRICE').text)

                # Negative prices are discounts
                if float(item_price) < 0:
                    item_is_discount = True
                else:
                    item_is_discount = False

                # Write to log
                logger.debug("   {:<2} {:<25} {:>7.2F} {:>7.2F}".format(item_quantity, item_desc, item_price,
                                                                        item_quantity * item_price))
                logger.debug("    Discount?: {}".format(item_is_discount))

                # Create an OrderItem, and add to Order
                # If check is not new, only add negative quantity items to order
                #if check_is_new:
                order_item = OrderItem(item_desc, item_price, item_quantity, item_is_discount)
                order.add(order_item)
                #else:
                #    if item_quantity < 0:
                #        order_item = OrderItem(item_desc, item_price, item_quantity, item_is_discount)
                #        order.add(order_item)

            # End for item
            logger.debug("\n")
            logger.debug(order)
            orders.append(order)

        # End for transaction
        for order in orders:
            logger.info(order)
            logger.info("\n")

    # End for file
    send_to_db(orders)

    #return orders


if __name__ == '__main__':
    main()
    #orders = main()

    #for order in orders:
    #    print(order)
    #    print()

