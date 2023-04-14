import re
from .decorators import phone_zone, name_params


def validate_email(email):
    email_pattern = '[А-Яа-яёЁ\w.-]+@([A-Za-zА-Яа-яёЁ0-9][A-Za-zА-Яа-яёЁ0-9-]+\.)+[A-Za-zА-Яа-яёЁ0-9]{2,4}$'
    res = re.match(email_pattern, email)
    return email if res else None


def validate_username(username):
    username_pattern = '[\w-]{2,150}$'
    res = re.match(username_pattern, username)
    return username if res else None


def validate_password(password):
    password_pattern = '(?=^.{8,128}$)(?=.*\d)(?=.*\W)(?=.*[A-Z])(?=.*[a-z])(?!.*\s)'
    res = re.match(password_pattern, password)
    return password if res else None


@phone_zone(countries=['BY', 'RU'])
def validate_phone(phone, phone_patterns: []):
    digit_phone = re.sub(r"\D", "", phone)
    res = [re.match(pattern, digit_phone) for pattern in phone_patterns]
    match_res = list(filter(lambda r: r is not None, res))
    return digit_phone if len(match_res) else None


@name_params(len_from=3, len_to=15, capitalize=True)
def validate_name(name, name_pattern: ''):
    res = re.match(name_pattern, name)
    return name if res else None



# def validate_phone(phone):
#     digit_phone = re.sub(r"[\D]", "", phone)
#     phone_pattern_BY = '375(44|29|25|33)\d{7}$'
#     phone_pattern_RU = '79\d{9}$'
#     res=re.match(phone_pattern_BY, digit_phone)
#     return digit_phone if res else None


# def validate_name(name):
#     name_pattern = '[A-Za-zА-Яа-яёЁ]+'
#     res = re.findall(name_pattern, name)
#     return ''.join(res).capitalize() if len(res) >= 1 else None


