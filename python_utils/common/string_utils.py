def check_string_for_tag(main_str, tag, num_occur=1, exact=True):
    """
    :type main_str: str
    :type tag: str
    :type num_occur: int
    :type exact: bool
    """
    indx = 0
    for i in range(0, num_occur):
        found_indx = main_str.find(tag, indx)
        if found_indx == -1:
            return False
        indx = found_indx + len(tag)
    if exact:
        found_indx = main_str.find(tag, indx)
        if found_indx != -1:
            return False

    return True
