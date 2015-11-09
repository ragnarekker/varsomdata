# -*- coding: utf-8 -*-
# __author__ = 'ragnarekker'


def remove_norwegian_letters(name_inn):
    """

    :param name_inn:
    :return:
    """

    if name_inn is None:
        return None

    name = name_inn

    if u'å' in name:
        name = name.replace(u'å', 'aa')
    if u'ø' in name:
        name = name.replace(u'ø', 'oe')
    if u'æ' in name:
        name = name.replace(u'æ', 'ae')

    name = name.encode('ascii', 'ignore')
    name = name.strip()                 # removes whitespace to left and right
    name = name.replace('\n', '')
    name = name.replace('\t', '')

    return name


def add_norwegian_letters(name_inn, use_encoding='utf8'):
    """

    :param name_inn:
    :return:
    """

    if name_inn is None:
        return None

    name = name_inn.decode(use_encoding, 'ignore')

    if u'ae' in name:
        name = name.replace(u'ae', 'æ'.decode(use_encoding, 'ignore'))
    if u'oe' in name:
        name = name.replace(u'oe', 'ø'.decode(use_encoding, 'ignore'))
    if u'aa' in name:
        name = name.replace(u'aa', 'å'.decode(use_encoding, 'ignore'))

    return name


if __name__ == "__main__":

    a = u'æøå'.encode('utf8')
    c = add_norwegian_letters('Proeve.')
    b = 1
