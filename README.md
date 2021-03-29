# Аспекты учета и поиска геоинформационных объектов с задействованием возможностей документоориентированной базы данных MongoDB.

__Онлайн-курс__: <a target="_blank" href="https://otus.ru/lessons/nosql-bd/">"OTUS.NoSQL"</a>.

__Период обучения:__ 30 сентября 2020 года — 4 апреля 2021 года.

<p style='text-align: right;'> «Лучше один раз увидеть, чем сто раз услышать!» (<i>пословица</i>)</p>

## Введение

**Геоинформация** - это любые сведения, отражающие расположение, форму и размеры объекта (далее - гео-объект). Ее учет ведется в картографии, геологии, метеорологии, землеустройстве, экологии, муниципальном управлении, транспорте, экономике, обороне и многих других областях. Геоинформация является неотъемлемой частью так называемых Больших данных, что приводит к необходимости разработки средств ее визуализации и анализа. 

> Можно было бы написать "сведения, отражающие свойства объектов материального мира". Однако на практике имелся факт осуществления энтузиастом накладки поверх Гугл-карт через их штатное API рисунков с топографией Средиземья и построение маршрутов героев Дж. Толкина, что не совсем "материально". Другим стыком с нематериальным может служить пример наборов данных по типу GeoIP.

Необходимо заметить, что документация по MongoDB является достаточно проработанной и удобной по навигации. Исчерпывающие сведения в разделе по [гео-объектам](https://docs.mongodb.com/manual/geospatial-queries/) подтолкнули к изучению изложенных в данной работе возможностей. Кроме того, после осуществленной разработки и достигнутых результатов в ходе написания настоящего конечного текста в документации MongoDB обнаружено [руководство](https://docs.mongodb.com/manual/tutorial/geospatial-tutorial/) по работе с гео-объектами, что только еще раз подтверждает о сильной его проработке.

Результат исследования представляет собой инструмент отображнения объектов данных типов, сведения о которых хранятся в MongoDB, на карте посредством web-доступа. Клиентская часть реализована с использованием [Leaflet](https://leafletjs.com/) (JavaScript-библиотека с открытым исходным кодом для мобильных интерактивных карт) и набора соотвествующих процедур асинхронного получения сведений от серверной части. Сервис реализован на базе созданного ранее на курсе ["OTUS.Web-python"](https://otus.ru/lessons/webpython/) конструктора программного обеспечения ["Dummy"](https://pypi.org/project/dummy_wsgi_framework/) на языке программирования Python3 с задействованием uWSGI. Особенности реализации процедур сбора демонстрационных сведений отражены по мере изложения, но основное внимание уделено простоте работы с геоинформацией средствами MongoDB.

## Гео-объекты MongoDB

В данной статье продемонстрированы базовые возможности оперирования в MongoDB такими [гео-объектами](https://docs.mongodb.com/manual/reference/geojson/) как: [точка](https://docs.mongodb.com/manual/reference/geojson/#point), [линия](https://docs.mongodb.com/manual/reference/geojson/#linestring), [полигон](https://docs.mongodb.com/manual/reference/geojson/#polygon). 

> Более сложные стурктуры, такие как: [набор точек](https://docs.mongodb.com/manual/reference/geojson/#multipoint), [набор линий](https://docs.mongodb.com/manual/reference/geojson/#multilinestring), [набор полигонов](https://docs.mongodb.com/manual/reference/geojson/#multipolygon) и [коллекция гео-объектов](https://docs.mongodb.com/manual/reference/geojson/#geometrycollection) не рассматриваются. 

Представляемое в рамках настоящей работы решение предполагает возможность хранения в обособленных коллекциях одной базы сведений о гео-объектах различных типов. Тем не менее хранение также возможно и в рамках одной коллекции. Названия полей, описывающих гео-объекты, могут быть произвольными, за исключением уникльноидентифицирующего атрибута документа - `ident`. Также необходимо соблюдать установленную MongoDB [структуру сведений](https://docs.mongodb.com/manual/geospatial-queries/#geojson-objects) о гео-объекте:

```
<field>: { type: <GeoJSON type> , coordinates: <coordinates> }
```

В рамках получения сведений клиентской стороной от серверной гео-объекты искусственно поделены на два вида - статичные и динамичные.

Под статичными понимаются те, свойства которых фиксированы, и, таким образом, актуализация сведений в отношении которых не требуется, в том числе при имзменении позиции наблюдения. В ранней <a href="https://habr.com/ru/post/523182/" target="_blank">статье</a> к данной категории относлись метеориты. С целью демонстрации возможностей работы с полигонами к ним добавлены - здания и сооружения (собраны для отдельного района г. Санкт-Петербурга).

Динамичные гео-объекты - это те, положение, форма или размер которых изменяются с течением времени даже при неизменной позиции наблюдателя. В качестве демонстрации возможности работы с таковыми осуществляется фоновый сбор перемещений таксопарка компании "Яндекс", представляемых на карте в виде части пути (несколько крайних точек пройденного маршрута) и текущих мест пребывания (точка).

### Предварительные действия

> Предполагается, что инфраструктура MongoDB развернута.

Создадим соотвествуюущу базу и коллекции. 

```mongodb
mongo  192.168.102.99  --port 49326
---
> use otus
switched to db otus
> db.dropDatabase()
{ "dropped" : "otus", "ok" : 1 }
> use otus
switched to db otus
> db
otus
> show collections
```

### Точки (статичные)

В качестве [точек](https://docs.mongodb.com/manual/reference/geojson/#point) используются [метеориты](https://data.nasa.gov/Space-Science/Meteorite-Landings/gh4g-9sfh). Создадим коллекцию и необходимые для работы индексы, указав названия полей, используемых для описания свойств данных гео-объектов.

```mongodb
> db.meteorites.createIndex( { "ident": 1 }, { unique: true } )
> db.meteorites.createIndex( { "location" : "2dsphere" } ) 
```

Изначально сведения о метоположении храняться в атрибуте `geolocation`. Однако оно не имеет необходимой струтктуры для гео-объекта типа "точка". Поэтому в качестве атрибута местоположения метеоритов выступает дополнительное, отсутствующее в демонстрационном наборе, поле `location`, куда перенесены сведения в необходимом формате:

```
location: { type: 'Point' , coordinates: [ LON, LAT ] }
```

Загрузка исходных данных о метеоритах: 

```shell
mongoimport --host 192.168.102.99  --port 49326 \
--db otus --collection meteorites --jsonArray \
--file ./foreign/meteorites/data.json

    2021-03-28T10:28:09.443+0300    connected to: mongodb://192.168.102.99:49326/
    2021-03-28T10:28:12.443+0300    [###.....................] otus.meteorites      1.62MB/10.1MB (16.0%)
    2021-03-28T10:28:15.443+0300    [#########...............] otus.meteorites      3.97MB/10.1MB (39.4%)
    2021-03-28T10:28:18.443+0300    [############............] otus.meteorites      5.39MB/10.1MB (53.4%)
    2021-03-28T10:28:21.443+0300    [#################.......] otus.meteorites      7.23MB/10.1MB (71.6%)
    2021-03-28T10:28:24.443+0300    [#####################...] otus.meteorites      8.83MB/10.1MB (87.5%)
    2021-03-28T10:28:27.443+0300    [#######################.] otus.meteorites      9.71MB/10.1MB (96.3%)
    2021-03-28T10:28:28.453+0300    [########################] otus.meteorites      10.1MB/10.1MB (100.0%)
    2021-03-28T10:28:28.454+0300    45716 document(s) imported successfully. 0 document(s) failed to import.
```

Исходя из уже имеющегося опыта, из набора 45716 объектов необходимо удалить метеорит, который не относится к земной поверхности (марсианский метеорит [Meridiani Planum](http://old.mirf.ru/Articles/art2427_2.htm)), так как его координаты не соответствуют стандарту земного геопозиционирования и не могут быть помещены в индекс (индексирование приводит к ошибке, равно как и вставка таких данных в индекс - `Can't extract geo keys: ... longitude/latitude is out of bounds, ...`).

```mongodb
db.meteorites.remove({"ident" : "32789"});
```

Кроме этого в наборе имеется 7315 метеоритов, чье местоположение неизветсно. Данный факт также не позволит включить их в гео-индекс и приведет к ошибке. Поэтому в индексе учтены только те метеориты, чье местоположение известно (38400 штук).

```mongodb
db.meteorites.updateMany( 
    {"geolocation":{$exists:true}},
    [{
        $set: {
            "location" : {
                "type": "Point",
                "coordinates" : [ 
                    { $toDouble: "$geolocation.longitude" } , 
                    { $toDouble: "$geolocation.latitude" } 
                ]
            }
        }
    }]
);
```

В результате в MongoDB в коллекции `meteorites` в атрибутах `location` содержится информация о местоположении 38400 из 45716 метеоритов. 

**Важное замечание:** согласно [документации](https://docs.mongodb.com/manual/geospatial-queries/#geospatial-data) данный порядок следования координат `{ долгота, широта }` является единственно верным с точки зрения MongoDB (`If specifying latitude and longitude coordinates, list the longitude first and then latitude`). Необходимо заострить внимание на этом обстоятельстве, так как в последующем при отображении информации на карте нужен будет другой порядок абсолютно для всех координат любых гео-объектов - `{ широта, долгота }`. Указанное приводит к тому, что после получения сведений из MongoDB для гео-объектов необходимо произвести перестановку в парах координат. Если для точки это выражается в одной перестановке, то для полигона это поисходит в рамках итерации по точкам границы. Было бы хорошо, если бы MongoDB поддерживала хранение и в формате `{ широта, долгота }`. 

### Полигоны (статичные)

В качестве [полигонов](https://docs.mongodb.com/manual/reference/geojson/#polygon) используются здания и сооружения, сведения о которых единоразово получены для отдельного района г. Санкт-Петербурга с использованием API сервиса [WikiMapia](https://wikimapia.org/api/).

> WikiMapia имеет лимит по числу запросов, при превышении которого сведения информационным ресурсом не предоставляются (при этом указанное не приводит к возникновению ошибки, что затрудняет понимание в фактическом наличии подобных данных). Указанное нивелировалось возможностью (предположительно неограниченного) получения дополнительных API-ключей доступа.

Изначально сведения о метоположении полигона разнесены по полям записи, то есть фактически отсутствует атрибут необходимой струтктуры для гео-объекта типа "полигон". Поэтому в его качестве выступает дополнительное поле `area`, куда перенесены сведения в необходимом формате. Структура гео-типа `полигон` имеет вид: 

```
area: { type: 'Polygon' , coordinates: [[ [LON_1, LAT_1], [LON_2, LAT_2], ..., [LON_1, LAT_1] ]] }
```

Создадим коллекцию и необходимые для работы индексы.

```mongodb
db.geo_wikimapia_polygons.createIndex( { "ident": 1 }, { unique: true } )
db.geo_wikimapia_polygons.createIndex( { "area" : "2dsphere" } ) 
```

[Сбор](./foreign/onetime_static_load_polygons_wikimapia.py) демонстрационных данных реализован на языке программировния Python3 с использованием библиотеки `pymongo`, поддерживающей исполнение набора инстукций вставки-обновления (`UPSERT`) за раз (`bulk_write(instructions)`).

В результате запросов к WikiMapia:

```shell
python3 ./foreign/onetime_static_load_polygons_wikimapia.py 

    Page 1 has docs count 50
    Page 2 has docs count 50
    ...
    Page 37 has docs count 35
    Max page 37 with some data
```

в MongoDB накоплена информация в отношении:

```mongodb
> db.geo_wikimapia_polygons.count()
```

1832 зданий и сооружений. Необходимо сделать важное замечание, почему не все 1835 полигона были сохранены ( 36 страниц * 50 полигонов + 35 полигонов = 1835 полигонов). 

**Важное замечание**: сведения о полигоне должны удовлетворять специфкации ([пункт 3.1.6 RFC 7946 "GeoJSON" August 2016](https://tools.ietf.org/html/rfc7946#section-3.1.6)). В частности, полигон, имеюищий пересечение граней, не может быть добавлен (иначе в MongoDB возникает ошибка `Edges <number K> and <number M> cross. Edge locations in degrees: [Kx1, Ky1]-[Kx2, Ky2] and [Mx1, My1]-[Mx2,My2]`). Кроме того, важно, чтобы полигон был "замкнут", то есть крайняя точка должна совпадать и первоначальной (иначе в MongoDB возникает ошибка `Loop is not closed`). Wikimapia иным образом походит к требованиям валидности координат полигонов, поэтому в MongoDB часть сохранить не удалось.

### Линии (динамичные) 

В качестве демонстрационных динамичных гео-объектов выбраны [линии](https://docs.mongodb.com/manual/reference/geojson/#linestring) и точки, отражающие крайние части маршрутов и фактическое пребывание атомобилей таксопарка компании "Яндекс" соотвественно.

**Важное замечание**: сведения о линии должны удовлетворять специфкации ([пункт 3.1.4 RFC 7946 "GeoJSON" August 2016](https://tools.ietf.org/html/rfc7946#section-3.1.4)), то есть линия должна содержать две разные точки (при этом она может также содержать и одинаковые).

Сбор демонстрационных данных [реализован](./foreign/upsert_yandex_taxi_loop.py) на языке программировния Python3 с использованием библиотек `requests`, `pymongo` и задействованием пакета многопорцессорной обработки  `multiprocessing`. Необходимость крайней обусловлена требованиями увеличения скорости получения актуальных сведений о местоположении и пути следования автомобилей с целью повышения частоты прорисовки маршрутов на карте (интерактивности). Сведения получаются в отношении заранее определенных точек района г. Санкт-Петербурга. Точки сбора данной информации располагаются на определенном коротком расстонии друг от друга и образуют заранее рассчитанную в проекте "ячеистую" структуру. Данный подход отличается от [алгоритма "заливки"](https://habr.com/ru/post/480956/), применявшегося иным разработчиком, исследовавшим подобную информацию ранее.

> __Вниманию Python-разработчиков__: не возможно организовать пул порцессов, к которым применены декораторы. Необходимо преписать код функций сбора \ обработки данных с условием отсутствия в них декораторов.

Изначально сведения о маршруте следования не имеют необходимой струтктуры для гео-объекта типа "линия". Поэтому в качестве данного атрибута выступает дополнительное поле `area`, куда перенесены сведения в необходимом формате. Структура гео-типа `линия` имеет вид: 
```
path: { type: 'LineString' , coordinates: [[ [LON_1, LAT_1], [LON_2, LAT_2], ..., [LON_N, LAT_N] ]] }
```

## Операции с гео-объектами

В рамках работы рассматриваются такие [операции](https://docs.mongodb.com/manual/geospatial-queries/#geospatial-query-operators) как: `$geoIntersects` и `$nearSphere`. 

Операция [$geoIntersects](https://docs.mongodb.com/manual/reference/operator/query/geoIntersects/#op._S_geoIntersects) является основной реализованной в проекте и используется для нахождения всех гео-объектов, имеющих пересечение по гео-расположению с текущей областью карты. Например, если в область карты (соотвествующий полигон, описываемый двумя крайними координатами) попадет чаcть маршрута (линии) или часть здания (полигона), то они буду подгружены из базы данных и отображены. Точки соотвественно появятся при их попадании в данную область. 

**Важное замечание**: при строгом подходе и оценке данного исследования можно утверждать, что оно фактически основано на единственном запросе "найти все объекты в области на карте". Однако, в рамках защиты необходимо заметить, что конечной целью являлась демонстрация именно простоты работы с геоинформацией в MongoDB.  

Использование иной операциии [$nearSphere](https://docs.mongodb.com/manual/reference/operator/query/nearSphere) продемонстрировано на примере выборки из MongoDb метеоритов с целью отображения их на карте только при условии присутствия их в "круговой" окрестности наблюдения. 
       
Операции [`$geoWithin`](https://docs.mongodb.com/manual/reference/operator/query/geoWithin/)(выборка гео-объектов, имеющих полное включение в заданную область) и [`$near`](https://docs.mongodb.com/manual/reference/operator/query/near/)(выборка гео-объектов в окрестности точки) в рамках настоящей работы не рассматриваются.

> Операции `$near` и `$nearSphere` шире по возможности, чем просто "нахождение в круговой окретсности", так как описывают не только макимальное удаление (`$maxDistance`) от точки наблюдения, но и минимальное (`$minDistance`). Данное обстоятельсво может быть использовано при работе с топографическими азимутальными секторами, углами обзора видеокамер городского наружного наблюдения, "классическими" областями действия сотовых вышек и иными гео-данными, учитывающими "примерное" удаление объектов от исходной точки наблюдения.

## Сервис демонстрации гео-объектов

Cервис реализован на базе авторского конструктора программного Web-обеспечения ["Dummy"](https://pypi.org/project/dummy_wsgi_framework/). Необходимо установить зависимости и запустить приложение (45 килобайт кода)

```shell
pip3 install -r requirements.txt
uwsgi --http 127.0.0.1:8080 --wsgi-file ./service/application.py
```

### Обстановка в области карты

Откройте браузер по адресу http://127.0.0.1:8080.

Вашему вниманию будет представлен район г. Санкт-Петербурга, где  отображены полигоны зданий. По мере перемещения по карте или изменении масштаба карты в асинхронном режиме подгружаются иные полигоны.

> Разработчикам на заметку: для записи GIF-анимации использовалось программное обеспечение [Peek](https://github.com/phw/peek).

![POLYGONS](./README.files/1_POLYGONS.gif). 

При перемещении в определенные районы (достаточно в исходной точке г. Санкт-Петербурга уменшить масштаб до размера "4") подгружаются указатели на конкретные места падения метеоритов. 

![METEORITES](./README.files/2_METEORITES.gif). 

С целью демонстрации в текущем приложении нет ограничения на степень масштабирования, при которой запросы к серверной части не происходят. Возможно уменшить масштаб карты и увидеть скопления метеоритов. 

Очередным открытием в имеющихся в NASA данных явилось наличие 64 метеоритов, местоположение падения которых имеют (абсолютно)одинаковые координаты. Указанное обнаружено в результате визуального изучения метеоритов на карте (выделяющаяся темная тень точки).

![METEORITES](./README.files/3_METEORITES.png). 

```mongo
> db.meteorites.find({"location.coordinates": [13.43333,58.58333] }).count()
    64
> db.meteorites.find({"location.coordinates": [13.43333,58.58333] }, {name: 1, _id: 0})
    { "name" : "Osterplana" }
    { "name" : "Österplana 002" }
    { "name" : "Österplana 003" }
    ...
    { "name" : "Österplana 064" }
```

Данные "необычные" сведения соответствуют метеориту "Österplana", имеющему удивительную [историю](https://en.wikipedia.org/wiki/Österplana_065). 

Для интерактивной демонстрации динамичных гео-объектов необходимо удалить имеющиеся сведения и убедиться в существовании индексов:

```mongodb
db.geo_yandex_taxi.deleteMany({})
db.geo_yandex_taxi.createIndex( { "ident": 1 }, { unique: true } )
db.geo_yandex_taxi.createIndex( { "last_point" : "2dsphere" } )
db.geo_yandex_taxi.createIndex( { "path" : "2dsphere" } )
```

и запустить их фоновый сбор в базу данных.

```
python3 ./foreign/upsert_yandex_taxi_loop.py 

    9       2.6140940189361572
    9       2.481816291809082
    9       2.528238296508789
    9       2.374605894088745
    9       2.5337154865264893
    9       2.7297616004943848
    9       2.60577392578125
    9       2.586944818496704
    9       2.5660433769226074
```

Исходные сведения о перемещении таксопартка "Яндекс" обезличенны и содержат крайние точки маршрута следования:

```
{'id': 'bcc095db8e3b56e057caebdb97af5693', 'display_tariff': 'business', 'free': True, 'static_icon': False, 'positions': [{'lon': 30.326291, 'lat': 59.974395, 'direction': 50.0, 'timestamp': '2021-03-24T23:49:01.000000+0000'}, {'lon': 30.326291, 'lat': 59.974395, 'direction': 50.0, 'timestamp': '2021-03-24T23:48:52.000000+0000'}, {'lon': 30.326291, 'lat': 59.974395, 'direction': 50.0, 'timestamp': '2021-03-24T23:48:43.000000+0000'}, {'lon': 30.326291, 'lat': 59.974395, 'direction': 50.0, 'timestamp': '2021-03-24T23:48:34.000000+0000'}]}
```

Данный формат свидетельсвует о том, что система "Яндекс" ориентирована на хранение ненормализованного документоориентированного вида сведений. Из них будут сформированы линия и крайняя фактическая точка местопребывания в необходимом формате:

![TAXI](./README.files/5_TAXI.gif)

Как продемонстрировано ниже помимо мониторинга на предмет появления нового динамичного объекта в текущей области карты системой осуществляется проверка покидания объектами ее границ. Иначе бы движущиеся объекты навсегда оставались по краям карты при выходе за периметр:

![TAXI](./README.files/4_TAXI.gif)

### Обстановка в области круговой окрестности

В данном разделе продемонстрирована выборка только тех гео-объектов, которые попадают в круговую окрестность, располагаемую по центру карты.

Откройте браузер по адресу http://localhost:8080/circle/.

![NEAR](./README.files/6_NEAR.gif)

Leaflet позволяет осуществить запрос у пользователя текущих координат. Таким образом, например, при наличии в полном объеме сведений о каких-либо сведениях клиенту посредством веб браузера можно рекомендовать интересуемые его ближайшие объекты (банкоматы, столовые, места общего пользования, места подзарядки телефонов, городской транспорт, друзей рядом, новые знакомства и иное).  

## Технические особенности реализациии

При использовании данных наработок помимо перечисленных аспектов необходмо учитывать следующее.

### Конфигурационный файл

Параметр конфигурации сервиса [`base_config.py`](./base_config.py) содержит отсылку на вид (`статичный` или `динамичный`), название коллекции базы MongoDB ("meteorites", "geo_wikimapia_polygons", "geo_yandex_taxi") и атрибуты ("location", "area", "last_point", "path"), содержащие сведения о гео-объектах с указанием их GeoJSON-типа ("Point", "LineString", "Polygon"), а именно:

```python3
...
MONGODB_DB_COLLECTIONS = dict(
    static={
        "meteorites": {
            "location": POINT_OBJECT,
        },
        "geo_wikimapia_polygons": {
            "area": POLYGON_OBJECT,
        },
    },
    dynamic={
        "geo_yandex_taxi": {
            "last_point": POINT_OBJECT,
            "path": LINE_STRING_OBJECT,
        },
    },
)
...
```

Таким образом, при необходимости подгрузки сведений из иной коллекции необходимо определиться какая она (статичная\динамичная) и какого типа данные (точка\линия\полигон) в каком атрибуте сохранены. После перезапуска сервиса, сведения о данных гео-объектах станут доступны на интерактивной карте.

При отсутсвии в конфигурации динамичной коллекции, генерируемая сервисом страница HTML не будет содержать инструкцию на JavaScript, осуществляющую перезапрос сведений даже при неизменной локации.

### Ненагружающий запоздалый AJAX запрос

Запрос сведений клиентской частью от серверной реализован через асинхронные запросы (ajax). При этом с целью недопущения испонения сервисом заросов, являющихся промежуточными, например, при последовательном переходе от участка карты к участку, запросы происходят с некоторой малой задержкой, во время которой данный запрос может быть отменен последующим. То есть фактически должна быть исполнена выборка только в конечном положении наблюдения, в том числе и при работе с масштабированием.

```js
 function get_data(...){
    ...
    if (xhr && !(xhr.readyState === 4)) {
        xhr.abort();
        console.log('Previous AJAX #' + xhr.__dt + ' was aborted');
    }
    clearTimeout(timer);
    xhr = new XMLHttpRequest();
    xhr.responseType = 'json';
    xhr.__dt = Date.now();
    console.log('Start AJAX #' + xhr.__dt);
    timer = setTimeout(function() {
        // find objects in area.
    }
}
```

Работа по старту AJAX-запроса и его прерывании, если пользователь направляет новый запрос, продемонстрирована ниже. 

![CLEVER_AJAX](./README.files/7_CLEVER_AJAX.gif). 

Промежуточные перемещения и зуммирования не приводят к совершению каких-либо действий серверной сторной.

## Направления работы

### Соотвествие координат

MongoDB использует систему координат WGS84 ([`MongoDB geospatial queries on GeoJSON objects calculate on a sphere; MongoDB uses the WGS84 reference system for geospatial queries on GeoJSON objects`](https://docs.mongodb.com/manual/geospatial-queries/#geojson-objects)), [из глоссария](https://docs.mongodb.com/manual/reference/glossary/#term-wgs84)).

При этом Leaflet по-умолчанию использует систему координат [EPSG 3857]([https://leafletjs.com/reference-1.7.1.html#crs-l-crs-epsg3857]).

Исходя из описания, [EPSG 3857](https://epsg.io/3857) допустима для координат между `85.06°S` и `85.06°N`. То есть при работе на "боевую" необходимо у Leaflet выставить параметр CRS в ["L.CRS.EPSG4326"](https://leafletjs.com/reference-1.7.1.html#crs-l-crs-epsg4326), поскольку [он](https://epsg.io/4326) не имеет таких ограничений и целиком соотвествует системе геокодирования MongoDB.
И именно поэтому при работе с `широтой` и `долготой` в MongoDB вместо `$near` необходимо применять `$nearSphere`.

### Запредельные координаты

К сожалению в данной работе не решен нюанс запроса сведений по области карты, находящейся за пределами стандартных для MongoDB широты и долготы. Например, при изначальной подгрузке карты возможно осуществить ее пролистываение в сторону и тем самым Leaflet станет запрашивать сведения, подобные этим:

```
pymongo.errors.OperationFailure: longitude/latitude is out of bounds, lng: 561.213 lat: 89.9823 ... 

Valid longitude values are between -180 and 180, both inclusive.
Valid latitude values are between -90 and 90, both inclusive.
```

Однако данный момент возможно решить, если проводить "нормирование" запрашиваемой области (по типу остатка от деления и пр), а при отображении на карте - "денормирование" в зависимости от смещения периметра карты относительно полученных координат гео-объектов.

### Нагрузочное тестирование

В рамках работы не рассматривались вопросы шардирования сведений о гео-объектах и не исследовалась отдача при нагрузочном тестировании. 

### Расширение источников

В результате рефакторинга представляется возможной организация запроосв свелений не только из разных коллекций, как это реализовано в настоящее время, но и от разных баз данных MongoDB. Указанное повысит гипкость использования разработанного инструмента.

## Выводы

Представленный результат позволяет организовать на его базе ядро практически любого онлайн сервиса - от работы со статичными объектами, до мониторинга передвижения грузо-пассажирского транспорта, в том числе [авиа](https://www.flightradar24.com/), или анализа движения погодных фронтов (температура, осадки).

## Вместо заключения

<p style='text-align: right;'> «Лучше один раз увидеть, чем сто раз услышать!» (<i>пословица</i>)</p>

![8](./README.files/8.png)

![9](./README.files/9.png) 
