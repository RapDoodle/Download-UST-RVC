# -*- coding: utf-8 -*-
DISP_MODE_LOG = 0
DISP_MODE_OK = 1
DISP_MODE_WARNING = 2
DISP_MODE_ERROR = 3

def y_n_choice(msg='Do you want to continue?', default_choice=False):
    default_choice_str = 'yes' if default_choice else 'no'
    while (True):
        choice = input(f'{msg} (default: {default_choice_str}) [Y/n] ')
        if choice == '':
            # Case: default
            return default_choice
        if choice.lower() == 'y':
            # Case: confirm
            return True
        if choice.lower() == 'n':
            # Case: reject
            return False
        # Case: unkown, continue


def display(msg, mode=DISP_MODE_LOG):
    if mode == DISP_MODE_OK:
        prefix = '[√]'
    elif mode == DISP_MODE_WARNING:
        prefix = '[!]'
    elif mode == DISP_MODE_ERROR:
        prefix = '[x]'
    else:
        prefix = '[*]'
    print(f'{prefix} {msg}')

