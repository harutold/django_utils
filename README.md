django_utils
============
Description is only on Russian currently.


email_auth_backend
-----
#### Usage:

    AUTHENTICATION_BACKENDS = ('django_utils.EmailBackend',)

Визуальный редактор в админку 
-----

Визуальный редактор, смена форматов ввода даты

#### Usage:
    from django_utils import WYSIWYGForm, AdminWYSIWYG

#### settings:

WYSIWYG_DELETE_FILES - добавление галочки для удаления файлов в FileField. Работает только для необязательных полей.

WYSIWYG_DATE_INPUT_FORMATS = ('%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d',) - Подменяет форматввода даты во всех DateField (только ввода и только DateField)


Функции обработки строк
-----

clean_html - Очищает входной HTML от ненужных коварных тегов. Требует Genshi.
capitalize

Заготовки методов класса
-----

filesize_generic

middleware
-----
#### django_utils.middleware.ThreadLocals

middleware.get_current_user
middleware.get_request

Возвращают текущего пользователя и реквест соответственно

+ __middleware.NoCacheOpera__

#### django_utils.middleware.NoCacheOpera
Отключает кеширование в Опере, которая зачастую кеширует всё, что надо и не надо.

Декораторы
-----

+ json
+ render_to
+ allow_tags

Другое
-----
+ __fallback_to__
+ __flatatt__
+ __SFieldSet__
