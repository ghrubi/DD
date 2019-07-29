""" Module containing Database activities for DD transactions """

import atexit
import pymysql
import logging

# Setup logging
# Define format for formatter
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# Define logger with name __name__. Set level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define log file and set formatting for file entries
file_handler = logging.FileHandler('/home/gene/log/DD/dddbtx.log')
file_handler.setFormatter(formatter)

# Add file handler to logger
logger.addHandler(file_handler)


class DDDB():
    """ Encapsulates the database connection and functions within """
    def __init__(self):
        # Open database connection
        self.db_conn = pymysql.connect("tiny", "ddUser", "ddd@t@", "dd_data")

        # Prepare a cursor object using cursor() method
        self.cursor = self.db_conn.cursor()

        # On exit, be sure to disconnect from DB
        atexit.register(self.__db_disconnect)

    def __db_disconnect(self):
        """ Database disconnect """
        print("Closing DB connection...")
        self.cursor.close()
        self.db_conn.close()
        print("Closed.")

    def clock_in(self, staff_id, clock_in_time):
        """ Submit clock in event to database """
        self.cursor.callproc('StaffClockIn', (staff_id, clock_in_time))
#        self.db_conn.commit()

    def update_clock_in(self, staff_id, clock_in_time, clock_out_time):
        """ Submit clock in/out update event to database """
        self.cursor.callproc('StaffUpdateClockInOut', (staff_id, clock_in_time, clock_out_time))
#        self.db_conn.commit()

    def add_orders(self, order_list):
        for order in order_list:
            if order.is_new:
                logger.info("DB insert receipt:")
            else:
                logger.info("DB update receipt:")

            logger.info("\n{}:{}:{}:{}:{}:{}:{}".format(order.check_num, order.check_time, order.check_name,
                                                        order.check_amount, order.check_tax, order.check_type,
                                                        order.check_pay_type))

            db_retval = ''
            if order.is_new:
                self.cursor.callproc('NewReceipt2', (order.check_num, order.check_time, order.check_name,
                                                     order.check_amount, order.check_tax, order.check_type,
                                                     order.check_pay_type, db_retval))
                # Get return value from db proc. Must reference the last arg(7)
                self.cursor.execute("SELECT @_NewReceipt2_7")

            else:
                self.cursor.callproc('UpdateReceipt', (order.check_num, order.check_time, order.check_name,
                                                       order.check_amount, order.check_tax, order.check_type,
                                                       order.check_pay_type, db_retval))
                # Get return value from db proc. Must reference the last arg(7)
                self.cursor.execute("SELECT @_UpdateReceipt_7")

            # Get the DB proc return val. Return val is a tuple and we want the first element.
            # Grab first element and toss the rest. This converts it to an int also
            db_status, *_ = self.cursor.fetchone()
            logger.info("Database returned : %s " % db_status)
            #print(type(db_status))

            # If db status is 1, order NewReceipt or UpdateReceipt was successful.
            # Now, add all the items for order to db as well
            if db_status:
                logger.info("DB insert receipt details:")
                for item in order:
                    logger.info("  {:<2} {:<25} {:>7.2F}".format(item.quantity, item.name, item.price))
                    if item.is_discount:
                        self.cursor.callproc('AddDiscountItem', (order.check_num, order.check_time, item.name,
                                                                 item.price, item.quantity))
                    else:
                        self.cursor.callproc('AddOrderItem', (order.check_num, order.check_time, item.name,
                                                              item.price, item.quantity))
                # End for item

                # Commit additions, changes, and items to db
                #self.db_conn.commit()
            else:
                if order.is_new:
                    logger.info("Receipt is a duplicate. Skip details and move to next receipt.")
                else:
                    logger.info("Update receipt not found in DB. Skip details and move to next receipt.")
        # End for order

