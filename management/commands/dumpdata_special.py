# -*- coding: utf-8 -*-
from optparse import make_option

from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_app, get_apps, get_models, get_model
from django.db.models.fields.related import RelatedField

def intuplelist0(tuplelist,el):
    for tuple in tuplelist:
        if el == tuple[0]:
            return True
    return False
def intuplelist1(tuplelist,el):
    for tuple in tuplelist:
        if el == tuple[1]:
            return True
    return False
        
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('-e', '--exclude', dest='exclude',action='append', default=[], 
            help='Apps to exclude (use multiple --exclude to exclude multiple apps).'),
        make_option('--exclude_model', dest='excludem',action='append', default=[], 
            help='Models to exclude (use multiple --exclude to exclude multiple models).'),
        make_option('--extrasort', action='store_true', 
            help='Sort models in order to prevent \
                 nowhere liks at LOADDATA. (Not realy ready yet)'),
        #make_option('--includem', dest='includem',action='append', default=[], 
        #    help='Models to include (use multiple --include to exclude multiple models).'),
    )
    help = 'Output the contents of the database as a fixture of the given format.'
    args = '[appname ...]'

    def handle(self, *app_labels, **options):
        format = options.get('format','json')
        indent = options.get('indent',None)
        exclude = options.get('exclude',[])
        exclude_models = options.get('excludem',[])
        #includem = options.get('includem',[])
        show_traceback = options.get('extrasort', False)
        extrasort = options.get('traceback', False)
        
        excluded_apps = [get_app(app_label) for app_label in exclude]
        excluded_models = [(get_app(app_label.split('.')[0]),
                            get_model(app_label.split('.')[0],
                                      app_label.split('.')[1])
                            ) for app_label in exclude_models]

        if len(app_labels) == 0:
            app_list = [app for app in get_apps() if app not in excluded_apps]
        else:
            app_list = [get_app(app_label) for app_label in app_labels]
        
        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % format)

        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)
        
        objects = []
        models=[]
        for app in app_list:
            for model in get_models(app):
                if intuplelist0(excluded_models, app) and\
                intuplelist1(excluded_models, model):
                    pass
                else:
                    models.append(model)
        
        if extrasort:
            models = sort_by_relation(models)
            
        
        for model in models:
            try:
                objects.extend(model._default_manager.all().order_by(pk))
            except:
                objects.extend(model._default_manager.all())
        try:
            return serializers.serialize(format, objects, indent=indent)
        except Exception, e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)


def sort_by_relation(models):
    u'''
     Сортирует список моделей так, что те, на кого ссылаются идут раньше,
       чем те, которые ссылаются (в общем при прохождении списка, когда
       встечается связь(RelatedField) то о модели, на которую
       ссылаются уже известно)
     Для решения проблем с петлями
      (A(x->B); B(x->A); или A(x->B); B(x->C); C(x->A) и т.п. ))
      после извлечения всех элементов, не участвующих в петлях,
      удаляем все необязательные связи и опять извлекаем.
      (Можно было бы сразу пренебречь необязательными связями,
      но в данной функции, если связи есть то стараемся их учитывать
      до последнего)
     
     TODO: Если ссылки на себя - проблема НЕ РЕШЕНА (пока прото игнорируется).
     TODO: протестиь это функционал нормально
     
     Идея взята из http://www.djangosnippets.org/snippets/533/
     
    '''
    
    def related_field(field_class):
        u'''
         Возвращает True если класс наследуется от RelatedField
         field_class - поле класса
        '''
        
        
        if field_class == RelatedField:
            return True
        try:
            for base in field_class.__bases__:
                if not (base == RelatedField):
                    items.extend(parents(base, seen))
                else:
                    return True
        except:
            pass
        return False
    
    def get_related(model):
        u'''
         Возвращает список связанных моделей
         (на которые ссылается данная модель)
         В том числе и связи ManyToMany
        '''
        
        res = []
        for field in model._meta.fields:
            if related_field(field.__class__):
                res.append(field)
        res.extend(model._meta.many_to_many)
        return res
    def remove_zerocons(graph):
        u'''
         Удаляет нулевые связи
        '''
        
        for (node,nodeinfo) in graph.items():# по всем узлам
            for x in xrange(len(nodeinfo[1])):# по всем связям
                (who_poin_on_me,reqired) = nodeinfo[1][x]
                if not reqired:# если не обязатедьная связь
                    if graph[who_poin_on_me][0]>0:
                        graph[who_poin_on_me][0] -= 1
                    else: # Вдруг где ошибся
                        raise Exception
                    del(graph[model][1][x])
        
        return graph

    def sort_possible(graph):
        u'''
        Сортируется всё, что получится (петли пропускаются)
        '''
        
        sorted = []
        while len(roots) != 0:
            root = roots.pop()
            sorted.append(root)
            for child in graph[root][1]:
                graph[child[0]][0] -= 1
                if graph[child[0]][0] == 0:
                    roots.append(child[0])
            del graph[root]
        return (sorted,graph)
    
    # {Модель: [На скольких ссылается,[ (Кто ссылается на,Обязательная связь(True,False)), ....]]}
    graph={}
    
    rel_to_fields=[]
    # Модели, где есть поле rel_to = self. Формат: [(Модель,Поле),...]
    rel_to_self = []
    
    #Список моделей
    for model in models:
        graph[model] = [0,[]]
    
    #Считаем связи
    for model in models:
        rel_to_fields = (get_related(model))
        # Отсечем связи на не включенные в дамп модели, связи самого на себя
        # а также повторные связи (A(), B(x->A,y->A))
        for field in rel_to_fields:
            if graph.has_key(field.rel.to) and (field.rel.to != model) and\
               not intuplelist0(graph[field.rel.to][1],model):
                graph[field.rel.to][1].append((model, not field.null))
                graph[model][0] += 1
            elif (field.rel.to != model):# rel_to = self
                rel_to_self.append((model, field))
    
    roots = [node for (node, nodeinfo) in graph.items() if nodeinfo[0] == 0]
    
    sorted,graph = sort_possible(graph) #sorted - Результат
    for x in xrange(len(models)):
        y = models[x]
        models[x] = None
        if not y in sorted:
            print 'NOT IN',y
        if y in models:
            print 'DOUBLE',y

    # Если остались петли
    if len(graph.items()):
        try:
            graph = remove_zerocons(graph)
        except:
            print 'Unknown error during loops Fight. Wrong Algorithm(('
        newSorted,graph = sort_possible(graph)
        sorted.extend(newSorted)
        if len(graph.items()): #неразрешимые сложнопредставляемые кольца
            print "Collisions in loop relations. Skipped models: ",
            for (node,nodeinfo) in graph.items():
                sorted.append(node)
                print node,' ',
    
    return sorted #, rel_to_self