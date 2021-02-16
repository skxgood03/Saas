#自定义插件

from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):

    # template_name = 'django/forms/widgets/radio.html'
    # option_template_name = 'django/forms/widgets/radio_option.html'

    template_name = 'widgets/color_radio/radio.html'
    option_template_name = 'widgets/color_radio/radio_option.html'