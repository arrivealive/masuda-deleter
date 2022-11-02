# from django.template.defaulttags import register
from django import template
from django.core import paginator

register = template.Library()

@register.filter
def show_page_num(num, page_obj:paginator.Page):
    pager_arm_left_length, pager_arm_right_length = get_pager_arm_lengths(page_obj.number, page_obj.paginator.num_pages)
    last = page_obj.paginator.num_pages
    current = page_obj.number
    if num in [1, last]:
        return True
    if num >= current - pager_arm_left_length and num <= current + pager_arm_right_length:
        return True
    return False

def get_pager_arm_lengths(current, last):
    arm_length = 10
    left_arm_length = arm_length
    right_arm_length = arm_length
    left_remainder = 0
    # current page が端っこの方のときの pager の腕の長さを決める
    if current - 1 <= arm_length:
        left_remainder = arm_length - (current - 2) if current > 1 else arm_length
        left_arm_length -= left_remainder
    right_remainder = 0
    if last - current < arm_length:
        right_remainder = arm_length - (last - current - 1) if current < last else arm_length
        right_arm_length -= right_remainder
    # 未調整の pager の腕の長さを調整する
    if right_arm_length == arm_length:
        if current + (right_arm_length + left_remainder) < last:
            right_arm_length += left_remainder
        else:
            right_arm_length = last - current - 1
    if left_arm_length == arm_length:
        if current - (left_arm_length + right_remainder) > 1:
            left_arm_length += right_remainder
        else:
            left_arm_length = current - 2

    return (left_arm_length, right_arm_length)
    