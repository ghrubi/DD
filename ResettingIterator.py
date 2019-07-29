""" ResettingIterator abstract class. It contains a list and a position state for
iterating over. """
from abc import ABC, abstractmethod


class ResettingIterator(ABC):

    def __init__(self):
        self.__iter_list = []
        self.__curr_pos = 0

    def add(self, item):
        self.__iter_list.append(item)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__has_more():
            # Reset pos pointer
            self.__curr_pos = 0
            raise StopIteration

        ret_obj = self.__iter_list[self.__curr_pos]
        self.__curr_pos += 1
        return ret_obj

    def __has_more(self):
        #print("pos {}, len{}".format(self.__curr_pos, len(self.__iter_list)))
        return self.__curr_pos < len(self.__iter_list)


