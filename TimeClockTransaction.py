""" Represents a time clock transaction """


class TimeClockTransaction():
    def __init__(self, staff_id, staff_name, send_count, entry_date, entry_time, clock_in_time, clock_out_time):
        self.staff_id = staff_id
        self.staff_name = staff_name
        self.send_count = send_count
        self.entry_date = entry_date
        self.entry_time = entry_time
        self.clock_in_time = clock_in_time
        self.clock_out_time = clock_out_time

    def __repr__(self):
        print("Time_Clock_Transaction({}, {}, {}, {}, {}, {}, {})".format(self.staff_id, self.staff_name,
                                                                          self.send_count, self.entry_date,
                                                                          self.entry_time, self.clock_in_time,
                                                                          self.clock_out_time))

    def __str__(self):
        retval = "Entry: {} {}\n".format(self.entry_date, self.entry_time)
        retval += "   StaffID  : {}\n".format(self.staff_id)
        retval += "   Name     : {}\n".format(self.staff_name)
        retval += "   Send #   : {}\n".format(self.send_count)
        retval += "   Clock In : {}\n".format(self.clock_in_time)
        retval += "   Clock Out: {}\n\n".format(self.clock_out_time)

        return retval
