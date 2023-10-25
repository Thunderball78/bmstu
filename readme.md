## Итоговая работа
## 12448/1 ИНЖДАН МГТУ им. Н.Э. Баумана
## Инженер данных (Data engineer)
## Андреев Андрей Анатольевич

## КЛАССИФИКАЦИЯ ГОСКОНТРАКТОВ ПО ОБЪЕКТАМ ЗАКУПКИ

### Задача: необходимо на основе данных с ftp.zakupki.gov.ru научиться определять группу, к которой относится контракт с кодом ОКПД-2 41, 42, 43, 71.1.

Группы могут быть следующими:

1.	Строительно-монтажные работы (СМР)
2.	Проектно-изыскательские работы (ПИР)
3.	Строительный надзор
4.	Подключение коммуникаций
5.	Прочее.

По ОКПД-2 контракты в общем случае должны разделяться так:
- Строительно-монтажные работы (СМР) - 41, 42, 43(кроме нижеперечисленных)
- Проектно-изыскательские работы (ПИР) - 41.1, 71.1
- Подключение коммуникаций - 43.22
- Строительный надзор – четкой группы нет.


Проблема: Далеко не всегда контракты указываются с нужным кодом, поэтому есть проблема как такие контракты "отловить" и определить в нужную группу.

Поэтому задача предполагает классификацию контрактов на основе объекта закупки, который сформулирован естественным языком. Также предполагаем, что могут иметь значение цена контракта и его длительность.
На основе этого на входе данные о контрактах. На выходе необходимо получить группу для каждого контракта.

Иногда контракт может относиться одновременно в несколько групп.

В приложении ниже пример нескольких контрактов, у которых неверно проставлен ОКПД-2.



# Отчет о проделанной работе
Анализ датасета показал, что он не размечан, нет признаков явно указывающих, какой код и группа верные, а какой нет. Поэтому, можно провести разметку прибегнув к кластеризации.

Если предположить, что количество некорректных кодов ОКПД-2 большое, тогда выполним кластеризацию данных по столбцу с описанием контракта. На основе полученной кластеризации, получаем размеченные данные, с помощью которых, можно обучить модель классификации с учетом стоимости и количества дней исполнения контракта.

Выполнена задача по классификации определения группы, к которой относится контракт с кодом ОКПД-2 41, 42, 43, 71.1.
В качестве модели выбрал алгоритм логистической регрессии. Точность модели получилось 0.81. 

В процессе работы были выполнены шаги:

1. Загрузка csv файла объемом 25Гб. Поскольку файл не помещался в памяти, было приняло решение загрузить его в базу данных. В процессе загрузки данные загружались порциями, при возникновении исключений, строка отбрасывалась. В базу данных загружал только необходимые признаки:
- id, 
- contract_number (номер контракта), 
- object_name (наименование услуги),
- object_code (код услуги), 
- cost (стоимость), 
- contract_execution_days (длительность контракта в днях -  рассчитывался как разница дат начала и окончания контракта).

2. Провел разведочный анализ данных. Сделал очистку данных от дублей и пропусков, а также от пустых строк и латинских символов. Поскольку в данных нет явной разметки, принял решение выполнить кластеризацию
данных, а уже кластеризованные данные в качестве разметки использовать для обучения модели классификатора.

3. Для выполнения классификации по наименованию услуги был выполнен NLP процесс  (токкенизация, леммотизация, стеминг, удаление стоп слов и знаков пунктуации). 

4. Выполнил класстеризацию  по наименованию услуги. Для этого уже разобранный текст на предыдущем шаге был векторизирован. К полученным признакам добавленны стоимость за день и группа контракта (как задано в условии). Группа была закодировна с помощью OneHotEncoder.
Услуги распределились по класстеру, визуально видно, что описание услуги соответствует класстеру. Но полученные класстера не сосвем соответствуют группам по условию. Вожможно не обходимо либо пересмотреть группировку кодов и обратится за помощью к специалисту из предметной области для уточнения ТЗ. В итоге было принято решение обучить модель классификации, а в качестве метки использовать кластер.

# Вывод
Провел анализ применения разных моделей машинного обучения. Лучше всех (точнее и производительнее) показала модель логистической регрессии: 

