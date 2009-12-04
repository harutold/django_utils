django_utils
============
Description is only on Russian currently.
 

email_auth_backend
-----

    AUTHENTICATION_BACKENDS = ('django_utils.EmailBackend',)

Визуальный редактор в админку 
-----

Визуальный редактор, смена форматов ввода даты

    from django_utils import WYSIWYGForm, AdminWYSIWYG

#### settings:

+ WYSIWYG_DELETE_FILES - добавление галочки для удаления файлов в FileField. Работает только для необязательных полей.
+ WYSIWYG_DATE_INPUT_FORMATS - подменяет форматввода даты во всех DateField (только ввода и только DateField)

    WYSIWYG_DATE_INPUT_FORMATS  = ('%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d',)
    WYSIWYG_DELETE_FILES = True

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

+ middleware.get_current_user
+ middleware.get_request

#### django_utils.middleware.NoCacheOpera
Отключает кеширование в Опере, которая зачастую кеширует всё, что надо и не надо.

#### django_utils.middleware.AjaxDebug
Скидывает содержимое response AJAX-запросов в статичный файл в папке MEDIA_ROOT

#### django_utils.middleware.ProfileMiddleware
subj

Decorators
-----

+ json
+ csv_decor
+ render_to
+ allow_tags
+ paged

Management
-----
+ clearpyc
+ dumpdata_special
+ triggers (useless for our purposes?)

Templatetags
-----

#### compare
+ ifin
+ ifnotin
+ equal_to

#### math
+ div
+ mult
+ num
+ rev
+ sub

#### text
+ truncatesmart
+ truncatechars

#### query_set
+ order_by

Разное
-----
+ fallback_to
+ flatatt
+ SFieldSet
+ cache (likely, will be removed)
