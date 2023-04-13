def phone_zone(countries):
    def pattern_define(phone_validator):
        def wrapped(*args):
            phone_patterns = []
            if 'BY' in countries:
                phone_patterns.append('375(44|29|25|33)\d{7}$')
            if 'RU' in countries:
                phone_patterns.append('79\d{9}$')
            return phone_validator(*args, phone_patterns)
        return wrapped
    return pattern_define


def name_params(len_from, len_to, capitalize):
    def pattern_define(name_validator):
        def wrapped(*args):
            name_pattern = '[A-Za-zА-Яа-яёЁ]{' + str(len_from) + ',' + str(len_to) + '}$'
            valid_name = name_validator(*args, name_pattern)
            return valid_name.capitalize() if valid_name and capitalize else valid_name
        return wrapped
    return pattern_define
