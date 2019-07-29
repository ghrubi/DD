""" Order and Order Item classes """
from ResettingIterator import ResettingIterator


class Order(ResettingIterator):
    def __init__(self, check_num, check_time, check_name, check_amount, check_tax, check_type, check_pay_type,
                 is_new=True):
        self.check_num = check_num
        self.check_time = check_time
        self.check_name = check_name
        self.check_amount = check_amount
        self.check_tax = check_tax
        self.check_type = check_type
        self.check_pay_type = check_pay_type
        self.is_new = is_new

        super().__init__()

    @property
    def check_total(self):
        return self.check_amount + self.check_tax

    def __repr__(self):
        return "Order({}, '{}', '{}', {}, {}, '{}', '{}', {})".format(self.check_num, self.check_time, self.check_name,
                                                                      self.check_amount, self.check_tax, self.check_type,
                                                                      self.check_pay_type, self.is_new)

    def __str__(self):
        #retVal = "{}, '{}', '{}', {}, {}, '{}', '{}'".format(self.check_num, self.check_time, self.check_name,
        #                                                          self.check_amount, self.check_tax, self.check_type,
        #                                                          self.check_pay_type)
        retVal = "{}, '{}', '{}', '{}', '{}', {}".format(self.check_num, self.check_time, self.check_name,
                                                         self.check_type, self.check_pay_type, self.is_new)
        for item in iter(self):
            retVal += "\n    {}".format(item)

        #retVal += "\n_________________________" # Underscores?
        retVal += "\n-------------------------" # Or, hyphens?
        retVal += "\nSub Total: ${:>7.2f}".format(self.check_amount)
        retVal += "\n      Tax: ${:>7.2f}".format(self.check_tax)
        retVal += "\n    Total: ${:>7.2f}".format(self.check_total)

        return retVal


class OrderItem:
    def __init__(self, name, price, quantity, is_discount=False):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.is_discount = is_discount

    def __repr__(self):
        return "OrderItem('{}', {}, {}, {})".format(self.name, self.price, self.quantity, self.is_discount)

    def __str__(self):
        return "{:<2} {:<25} ${:>7.2f}".format(self.quantity, self.name, self.quantity * self.price)


