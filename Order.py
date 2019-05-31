""" Order and Order Item classes """

class Order:
    def __init__(self, check_num, check_time, check_name, check_amount, check_tax, check_type, check_pay_type):
        self.check_num = check_num
        self.check_time = check_time
        self.check_name = check_name
        self.check_amount = check_amount
        self.check_tax = check_tax
        self.check_type = check_type
        self.check_pay_type = check_pay_type

        self.order_items = []
        self.__curr_pos = 0

    @property
    def check_total(self):
        return self.check_amount + self.check_tax

    def add(self, order_item):
        self.order_items.append(order_item)

    def __repr__(self):
        return "Order({}, '{}', '{}', {}, {}, '{}', '{}')".format(self.check_num, self.check_time, self.check_name,
                                                                  self.check_amount, self.check_tax, self.check_type,
                                                                  self.check_pay_type)

    def __str__(self):
        #retVal = "{}, '{}', '{}', {}, {}, '{}', '{}'".format(self.check_num, self.check_time, self.check_name,
        #                                                          self.check_amount, self.check_tax, self.check_type,
        #                                                          self.check_pay_type)
        retVal = "{}, '{}', '{}', '{}', '{}'".format(self.check_num, self.check_time, self.check_name,
                                                     self.check_type, self.check_pay_type)
        for item in self.order_items:
            retVal += "\n    {}".format(item)

        retVal += "\n_________________________"
        retVal += "\nSub Total: ${:.2f}".format(self.check_amount)
        retVal += "\n      Tax: ${:.2f}".format(self.check_tax)
        retVal += "\n    Total: ${:.2f}".format(self.check_total)

        return retVal

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__has_more():
            # Reset pos pointer
            self.__curr_pos = 0
            raise StopIteration

        ret_obj = self.order_items[self.__curr_pos]
        self.__curr_pos += 1
        return ret_obj

    def __has_more(self):
        #print("pos {}, len{}".format(self.__curr_pos, len(self.order_items)))
        return self.__curr_pos < len(self.order_items)


class OrderItem:
    def __init__(self, name, price, quantity, is_discount=False):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.is_discount = is_discount

    def __repr__(self):
        return "OrderItem('{}', {}, {}, {})".format(self.name, self.price, self.quantity, self.is_discount)

    def __str__(self):
        return "{} {} ${:.2f}".format(self.quantity, self.name, self.quantity * self.price)


