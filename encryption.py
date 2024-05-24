import os
from datetime import datetime
import string as strings
from hashlib import md5, sha3_256, sha3_384
from secrets import choice as secret_choice


def generate_random_string(length):
    characters = strings.ascii_letters + strings.digits
    random_string = ''.join(secret_choice(characters) for _ in range(length))
    return random_string


def generate_seed(day=False, week=False, month=False, year=False):
    import random
    """
        Generate a random string to use as seed
        :param day: True to set that the same arrangement will be formed for a specific day only.
        :param week: True to set that the same arrangement will be formed for a specific week.
        :param month: True to set that the same arrangement will be formed for a specific month.
        :param year: True to set that the same arrangement will be formed for a specific year.
        :param seed: A string to use as a seed for rearranging the code.
        It is generally not recommended,
        except for special cases where a specific arrangement must be generated consistently.
        Using a seed may result in predictable arrangements and should be used with caution.
        :return: The rearranged string
        if all are false then return a unique string each time
        you must set only one as true, if multiple values are True, the priority followed is:
        1 - seed
        2 - day
        3 - week
        4 - month
        5 - year
        """
    if day:
        seed = (datetime.now().day * 2) + ((datetime.now().day // 7) * 40) + (datetime.now().month * 128) + (
                datetime.now().year * 1050)
    elif week:
        seed = (datetime.now().day // 7) + (datetime.now().month * 10) + (datetime.now().year * 100)
    elif month:
        seed = (datetime.now().month * 13) + (datetime.now().year * 100)
    elif year:
        seed = (datetime.now().year * 99)
    else:
        seed = str((datetime.now().microsecond * 8) + (datetime.now().second * 14) + (datetime.now().minute * 131) + (
                datetime.now().hour * 1031) + (datetime.now().day * 27491) + (
                           (datetime.now().day // 7) * 402464) + (datetime.now().month * 1740020) + (
                           datetime.now().year * 1042000)) + generate_random_string(random.randint(25, 100))
    seed = (str(seed) if not isinstance(seed, str) else seed)
    seed = sha3_256(seed.encode("utf-32")).hexdigest()
    random.seed(seed)
    seed += "".join([chr(random.randint(33, 126)) for _ in range(random.randint(6, 35))])
    return seed


def rearrange(string, day=False, week=False, month=False, year=False, seed=None):
    import random
    """
    Rearrange string
    :param string: The string to be rearranged
    :param day: True to set that the same arrangement will be formed for a specific day only.
    :param week: True to set that the same arrangement will be formed for a specific week.
    :param month: True to set that the same arrangement will be formed for a specific month.
    :param year: True to set that the same arrangement will be formed for a specific year.
    :param seed: A string to use as a seed for rearranging the code.
    It is generally not recommended,
    except for special cases where a specific arrangement must be generated consistently.
    Using a seed may result in predictable arrangements and should be used with caution.
    :return: The rearranged string
    if all are false then return a unique string each time
    you must set only one as true, if multiple values are True, the priority followed is:
    1 - seed
    2 - day
    3 - week
    4 - month
    5 - year
    """
    if seed is not None:
        seed = seed
    else:
        seed = generate_seed(day=day, week=week, month=month, year=year)
    random.seed(seed)
    ua = list(string)
    random.shuffle(ua)
    ua = "".join(ua)
    return ua


def tasagare_hash(text):
    """
    Hashes the given string
    :param text:
    :return:
    """
    text = rearrange(text, seed=os.getenv("RE_SEED", "UIUAG8RWIUSHSZ'/FPEJBDFVO;JBDEIRODF"))
    text = sha3_384(text.encode()).hexdigest()
    return text
