"""Answers list"""
import random

SLOGAN = [
    """Сегодня в клубе Гараж несравненный DJ Баян""",
    """Наш Баян - правильный Баян!""",
    """ООО "Аояма-Баян" - рытьё котлованов, ям и окопов.""",
    """Дарите любимым только Баян!""",
    """Баян подходит для всей полости рта""",
    """Баян - садо без смазо.""",
    """Баян - высокое качество по низким ценам.""",
    """ "Баян" - правильное пиво!""",
    """Новый "Орбит Баян", на вкус действительно как Баян!""",
    """Найди под крышечкой Баян - найди свою радость!""",
    """Баян дарит людям радость!""",
    """Смотрите новую искромётную комедию "Баян едет в Бобруйск"!""",
    """И на восмьй день Господь создал Баян для нашей радости!""",
    """Баян позволит жить полной жизнью""",
    """Баян делает твой день веселее.""",
    """Скоро на экранах: телесериал "Баян в погоне за сексом с тёщей" """,
    """Портативные ядерные установки "Megaton Баян" - заявите миру о себе!""",
    """Баян приносит инновации в наш мир.""",
    """Гроб "Happy Баян" - чтобы жизнь не кончалась.""",
    """Чистый Баян. Чистая мощь!""",
    """Покупайте новый кефир "Био-Баян"!""",
    """Пояс шахида "Баян" - с ним ты всегда в центре внимания!""",
    """Табачная компания "Прима Баян" - Народная марка""",
    """Баян. За качество отвечаю.""",
    """Вступайте в общество защиты прав унитазов "Фаянсовый Баян"!""",
    """ "Баян из Нью-Йорка". Смотрите в кинотеатрах страны""",
    """Баян круче Кольца Всевластья!""",
    """Во всех кинотеатрах страны! Новая лирическая комедия "Слющай, Гиви, купи мой Баян!" """,
    """Баян - почувствуй нашу любовь!""",
    """Все в мире для тебя, если у тебя есть Баян""",
    """Приглашаем на концерт фашистской музыки "Баян фюрера". Число билетов ограничено!""",
    """Мода. Стиль. Баян.""",
    """Баян - главный секрет женских побед!""",
    """Смотрите в кинотеатрах страны новый фильм "Серёга и его Баян" """,
    """Благодарим Баян за наше счастливое детство!""",
    """Баян в кармане - не вошь на аркане!""",
    """Обещайте ей, что угодно, но дарите только Баян!""",
    """Сила Баян в твоих руках.""",
    """Играй в Баян и начинай жить.""",
    """Баян - первый среди лидеров!""",
    """Купи Баян и надейся на лучшее""",
    """Баян. Управляй мечтой.""",
    """Секс-шоп "Баян". Подари себе праздник!""",
    """Заходите в наш стрип-бар "Похотливый Баян"!""",
    """Голактеко безопасносте с Баян!!11111адинадин""",
    """Баян жжот, остальные сосут!""",
    """Майонез "Баян" - король Вашего стола.""",
    """Баян - выбор сильнейших!""",
    """Баян. Пожалуйста, ещё Баян.""",
    """Магазин хасидской одежды "Баян энд хасидушки" - выделись из толпы!""",
    """Жгун "Баян" - отжыгай по полной!""",
    """Застраховано Баян лтд лимитед.""",
    """Не имей сто друзей, а имей Баян!""",
    """Баян - настоящее китайское качество - не какая-нибудь европейская подделка!""",
    """Баян - лучший подарок для Вашего шефа.""",
    """Лизни Баян и мир станет проще""",
    """С "Любимым" хорошо, а с Баян ещё лучше!""",
    """Баян - и ты опять летаешь во сне.""",
    """Баян. Заставь их уважать твой авторитет!""",
    """Калькуляторы Баян - точность и надёжность.""",
    """Это может быть только Баян!""",
    """Баян - твоё второе имя.""",
    """Баян превращает мечты в реальность.""",
    """Пацифистское движение "Баян" - Давайте жить дружно""",
    """Пожалуй, самый лучший Баян в СССР...""",
    """Чувствуешь? Это Баян.""",
    """Вам не хватает любви? Баян даст её вам!""",
    """Вступайте в нашу национал-патриотическую партию "Баян"! "Баян" или смерть!""",
    """Баян - лучший продукт рабского труда!""",
    """Баян - это вам не хрен собачий!""",
    """Не ссы, попробуй новый Баян!""",
    """Болит голова? День не задался? Баян - именно то, что тебе нужно!""",
    """Теперь и Баян записан в Death Note...""",
    """Баян - лучшее из Японии!""",
    """Пиво "Баян" - доброе пиво!""",
    """Мороженое "Баян" из натуральных компонентов - вкус счастья!""",
    """Новые покрышки Баян - покрути планету""",
    """Сериал Баян не поймет ни одна бабушка!""",
    """Баян. Пожалуй, лучшее пиво в мире.""",
    """Каждый охотник желает знать где сидит Баян!""",
    """Баян позаботится о тебе!""",
    """Клуб "Баян". Не надо слов - въеби спидов!""",
    """Сигареты "Баян" - не лошадь, не умрешь!""",
    """Новая жевательная резинка "Ароматный Баян" - на вкус как настоящий Баян!""",
    """Баян, который живёт на крыше""",
    """Баян - всегда что-то новое!""",
    """Баян - торкает не по-детски!""",
    """Сборник порно "Баян" не даст скучать вам и вашим рукам.""",
    """Баян. Последний штрих в вашем стиле.""",
    """Баян удовлетворит все твои желания.""",
    """Новый гель от гемороя "Баян" - ваша жопа будет вам благодарна!""",
    """Раньше я думал, что это сифилис. Теперь я понял, что это Баян!""",
    """Баян - в каждом глоточке фруктовые кусочки!""",
    """Баян - в желудке всё спокойно""",
    """Каждый извращенец мечтает о Баяне.""",
    """Новый концерт Бори Моисеева "Голубой Баян" - число билетов ограничено.""",
    """Мой Мир. Мой Баян.""",
    """Баян. Ведь вы этого достойны!""",
    """ "Баян" - свежий йогурт от счастливой коровы!""",
    """Баян всегда на шаг впереди!""",
    """Даже у последнего засранца есть Баян!""",
    """Поисковая система Баян ищет что надо.""",
    """Баян работает за шестерых!""",
    """Баян - наслаждение, которое не забыть.""",
    """Элитные девочки ждут вас в борделе "Баян" """,
    """Баян не оставит в трудную минуту.""",
    """Я готов на всё ради Баян, а ты?""",
    """Баян согреет в непогоду""",
    """Мексиканская неделя с кетчупом "Сеньор Баян"!""",
    """Баян - всё по-честному.""",
    """Кофе "Баян" - настоящий мерзкий китайский кофе!""",
    """Самый лучший среди Баяннов. Самый Баян среди лучших!""",
    """Гагарин долетался, а Баян допизделся!""",
    """ "Баян ниггера" - новый сбоник рэп-музыки. Yo, чувак!""",
    """Баян - зимой и летом мечтают об этом!""",
    """Целый месяц "Баян" защищает ваш дом от комаров!""",
    """Покупайте новую игру "Баян 3: Нашествие похотливых гомосеков"!""",
    """Баян без цензуры, только у нас!""",
    """Баян. Пей легенду!""",
    """Не все йогурты одинаково полезны. Баян полезен!""",
    """Баян - стирка без кипячения!""",
    """Баян - не поперхнись от смеха!""",
    """Поющие унитазы "Баян" - какать стало ещё приятнее!""",
    """Агенство киллеров "Дон Баян". Мы рады любым клиентам!""",
    """ "АнтиБаян" - даже лучше, чем Баян!""",
    """Баян. Отступники наступают!""",
    """Баян - райское наслаждение!""",
    """Баян накачает мышцу""",
    """Едем на дачу - Баян в придачу!""",
    """Баян - ваш новый ангел-хранитель.""",
    """Баян - нечто обтекаемое""",
    """Баян - яркий всплеск головокружительного обьёма.""",
    """Билл Каулитц любит только Баян!""",
    """Новый мобильный телефон "Баян 7650" - форма говорит о содержании...""",
    """Баян - видь яснее, делай дольше!""",
    """Сэмки "Чоткий Баян" - пацаны одобрят!""",
    """Баян - добавь себе ещё 100 лет""",
    """Смотрите в кинотеатрах садомазопедофилокомедию "Мистер и миссис Баян" """,
    """Не можете пёрнуть? Газер "Баян" поможет вам газануть как следует!""",
    """Момент настал, прими Баян""",
    """Рождественские какашки "Баян" - подари любимым праздник!""",
    """Новый тариф "МТС.Баян" - революция в мире мобильной связи!""",
    """Газонокосилки "Баян" - закоси по-взрослому!""",
    """Ваша жена сердита на вас? Подарите ей Баян!""",
    """Внедорожник "Баян 4х4" - трудно догнать, невозможно обойти.""",
    """Кто в супе хозяин? Конечно же бульонные кубики Баян!""",
    """Баян. Чувствуешь, что живёшь.""",
    """Баян любит вас!""",
    """Баян. Форма говорит о содержании...""",
    """Хочется Баян? Добро пожаловать в ресторан "Хрустящий Баян"!""",
    """Баян - мой стиль жизни!""",
    """Баян надерёт задницу всему миру""",
    """Естественно Баян!""",
    """Баян. Вы с этого хуеете?""",
    """Часы "Rolex Баян" - традиции качества""",
    """Баян - для лучшего будущего.""",
    """Баян. Захват мира подождёт.""",
    """Красота форм. Совершенство функций. Баян.""",
    """Баян - Ваш путь к богатству!""",
    """Баян это страсть!""",
    """Чай "Баян" - душа поёт!""",
    """Баян. Всё остальное - компромисс.""",
    """Не говорите никому, где я беру Баян!""",
    """Баян. Прикоснись к неизведанному.""",
    """Покупая у нас Баян, вы получите фирменное ведёрко, чтобы хранить в нём ваш Баян!""",
    """Каждый Баян имеет свою неповторимую историю.""",
    """Баян. На этом можно обогнать время.""",
    """Новая постановка Театра Сатиры - "Баян нашей юности" """,
    """Под каждой крышечкой Баян вас ждёт сюрприз!""",
    """Попробуйте новую бобруйскую колу "Баян". Аффтар, выпий Баян!""",
    """Баян! Теперь с ванильным вкусом!""",
    """Баян делает это дольше всех!""",
    """Баян - ощути силу!""",
    """Пивнушка "Баян" на Старом Арбате - мы всегда вам рады!""",
    """Туалетная бумага "Баян Плюс" - нежнее нежного!""",
    """Секс-кукла "Баян" - простой путь к счастью!""",
    """Настоящая арабская шаурма только в сети ресторанов "Гоги и Баян" """,
    """Побалуй себя. Баян.""",
    """Майки с надписью "Баян"! Покажи людям, что ты Баян!""",
    """ "Баян Pro" - для продвинутых пользователей!""",
    """Сосалки "Баян" - мы научили мир сосать!""",
    """Проголодался? Попробуй новый Баян!""",
    """Ножницы Баян отрежут самое дорогое.""",
    """Пацаны выбирают Баян.""",
    """Всё, что тебе надо это Баян.""",
    """Ты создан для счастья, как Баян для тебя!""",
    """Баян освежает дыхание! Баян облегчает понимание!""",
    """Баян - всегда Баян!""",
    """Баян. Где бы вы ни были!""",
    """Баян знает всё о твоих желаниях!""",
    """Пиво "Баян" варится из натуральных компонентов на лучших баварских заводах!""",
    """iБаян - новый хит от компании Apple.""",
    """Новая книга "Баян для чайников" уже в продаже""",
    """Баян - тонкий намёк на твоё превосходство.""",
    """Летайте самолётами "Баян" """,
    """Продаётся щенок породы Баян. Есть родословная.""",
    """Смотрите в кинотеатрах страны новый мистический триллер "Баян из бездны"!""",
    """Терроризм стал опаснее. Секс стал безопаснее. Презервативы "Баян".""",
    """Попробуйте новый корм для кошек "Кискас-Баян"!""",
    """А у меня в кармане новый Баян!""",
    """Хватит пукать - прими Баян в капсулах!""",
    """ "Гарри Поттер и Баян" - скоро в кинотеатрах""",
    """ "Мисс оргазм и Баян" - новый порнофильм Джорджа Лукаса!""",
    """Не тупи, Баян купи!""",
    """Я и Баян: мы такие разные, и всё-таки мы вместе!""",
    """Ты хочешь счастья - значит ты хочешь Баян""",
    """Баян подарит вам белоснежную улыбку и арктическую свежесть""",
    """Хорошо иметь домик в деревне! А ещё лучше иметь Баян!""",
    """Баян - Будущее зависнет от тебя.""",
    """С Баян вы будете неотразимы!""",
    """Баян - эстэтично и практично!""",
    """Дезодорант "Баян" - ни пота, ни запаха""",
    """Покупая у нас Баян, второй Баян вы получаете в подарок!""",
    """Заводы - рабочим! Землю - крестьянам! Баян - мне!!!""",
    """Баян - одно имя, одна легенда.""",
    """ "Баян XXL" - супер упаковка - весёлая тусовка!""",
    """Смотрите в кинотеатрах новый боевик "Малыш Баян и его банда" """,
    """Баян. Я это люблю.""",
    """Баян - прикосновение нежности""",
    """Баян - хозяин дороги""",
    """Будь лучше с Баян""",
    """Баян обеспечит культурный шок.""",
    """Баян - просто мне так удобно!""",
    """Баян - вершина твоего успеха!""",
    """Баян - когда мозгу нужна помощь.""",
    """Баян и точка.""",
    """Баян. Полный Баян.""",
    """Ты, я и Баян...""",
    """Кошельки "Баян" - ваши деньги будут довольны!""",
    """Удовольствие - это скушать Баян!""",
    """Таблетки "Стоит как Баян!" - Виагра отдыхает...""",
    """Гель "Баян" - и всё пойдёт как по маслу!""",
    """Баян есть, проблем нет.""",
    """Если вы видите Баян, значит, это не ваш Баян!""",
    """Хотите новый слоган? Баян уже придумал его""",
    """Плевать, что ты Баян, я все равно люблю тебя!""",
    """Потные подмышки? Тебе поможет Баян!""",
    """Акустика Баян - мега бас, аж вытек глаз!""",
    """Да пребудет с тобой Баян!""",
    """Выделись из толпы! - Купи нашу футболку с надписью "Баян"!""",
    """Диарея застала врасплох? Баян не так уж плох!""",
    """Садо-мазо комплект "Баян". Играй серъезно!""",
    """Баян - уничтожь стереотипы!""",
    """Баян наполнит счастьем твои последние дни.""",
    """Королевы покупают Баян!""",
    """Открой мир с Баян.""",
    """Элитные проститутки в салоне "Баян" """,
    """Баян между ног? Баян встал и смог!""",
    """Баян ищет надёжного хозяина""",
    """Попробуйте новый суп "Магги Баян с шампиньонами"!""",
    """Обувь "Баян" - оставь свой след!""",
    """Баян - выбор реальных пацанов!""",
    """Гель "Баян" - забудьте об анальных трещинах!""",
    """Не грусти Баян похрусти!""",
    """Баян - в любом месте веселее вместе!""",
    """Баян помогает жить насыщеннее""",
    """Баян - не то, что кажется!""",
    """Попробуйте новый кофе "Nescafe Баян"!""",
    """Туалетная бумага "Баян Лайт" - кайф и нега для вашей задницы!""",
    """Баян. Аромат желания.""",
    """ "Баян из Парижа". Смотрите в кинотеатрах страны""",
    """Я могу объять необъятное. Я могу больше. Я - Баян!""",
    """ "Баян" - просто добавь воды!""",
    """Войди в счастливое завтра с Баян.""",
    """Ганджа "Баян от Боба Марли" - just дует!""",
    """Неоспоримые достоинства Баяна.""",
    """Баян - на радость детям!""",
    """Баян сделает это ровно и аккуратно.""",
    """Баян не гнётся даже при -273 по цельсию!""",
    """Баян вкуси или лапу соси.""",
    """Я - бог. Я - идол. Я - Баян.""",
]


FUCKING_ADVICE = [
    """Альцгеймер - это блять не родственник!""",
    """Анализируй блять неудачи!""",
    """Боишься, блять - не делай!""",
    """Будет ли это ебать тебя через год?""",
    """Будешь гоняться за тенями — проебёшь настоящее!""",
    """Будь блять внимательнее!""",
    """Будь блять настойчивым!""",
    """Будь последовательным, ёпта!""",
    """Будь проще, ёпта!""",
    """Будь эффективнее, ёбта!""",
    """Веди логи, блять!""",
    """Включи блять воображение!""",
    """Вноси блять разнообразие!""",
    """Возьми блять выходной!""",
    """Впечатляй блять!""",
    """Всегда блять имей запасной вариант!""",
    """Выбрось нахуй и начни заново!""",
    """Выйди блять за рамки!""",
    """Высыпайся блять как следует!""",
    """Выясни блять всю хуйню!""",
    """Дай блять глазам отдохнуть!""",
    """Делай блять всё по-порядку!""",
    """Делай блять перерывы!""",
    """Делай больше пизди меньше!""",
    """Деньги — хуёвая цель!""",
    """Держи себя в руках, блять!""",
    """Дохуя планируешь — нихуя не успеешь!""",
    """Если кто-то смог блять, то и ты сможешь!""",
    """Если советы не приносят тебе пользу - значит, ты не умеешь их давать. Йопта""",
    """Если тебя это не радует нахуя ты это делаешь?""",
    """Живи проще — будет пизже!""",
    """Заведи блять ежедневник!""",
    """Задавай блять правильные вопросы!""",
    """Займись блять делом!""",
    """Займись блять чем-нибудь новым!""",
    """Закрой нахуй чатики!""",
    """Запиши блять — и не забудешь!""",
    """Знаешь что не прав — не спорь блять""",
    """Знай меру, ёпта!""",
    """Иди блять отдохни немного!""",
    """Избегай блять конфликтов!""",
    """Извинись, ёпта!""",
    """Изучай блять чужие работы!""",
    """Изучил, блять - используй!""",
    """Имей терпение, ёпта!""",
    """Импровизируй, ёпта!""",
    """Исправляй ебаные ошибки!""",
    """Исходи блять из своего опыта!""",
    """Ищи блять идеи попроще!""",
    """Ищи блять того кто шарит!""",
    """Кадрируй, блять!""",
    """Как тратишь время так блять и живёшь""",
    """Купи блять видеорегистратор!""",
    """Купи блять нормальную вспышку!""",
    """Купи блять нормальный объектив!""",
    """К успеху придёт упорный""",
    """Накосячил, блять - сознайся!""",
    """Напиши блять так, чтобы сам запомнил!""",
    """Настрой блять резкость!""",
    """Научись блять принимать критику!""",
    """Не вали горизонт, ёпта!""",
    """Не вороши блять прошлое!""",
    """Не еби мозги окружающим!""",
    """Не жалей блять о сделанном!""",
    """Не живи блять воспоминаниями!""",
    """Не задирай блять iso при дневном свете!""",
    """Не задрачивайся на мелочах!""",
    """Не занудствуй, блять!""",
    """Не зацикливайся блять на прошлом!""",
    """Не знаешь — не пизди!""",
    """Не ищи блять отмазок!""",
    """Не мешай блять другим работать!""",
    """Не можешь помочь — съебись и не мешай!""",
    """Не нравится - перепиши блять заново!""",
    """Не отвлекайся на хуйню!""",
    """Не пизди чужие картинки!""",
    """Не понял - переспроси, блять!""",
    """Не рви блять жопу напрасно!""",
    """Не суетись блять!""",
    """Не халтурь, блять!""",
    """Не хватайся блять за всё сразу!""",
    """Не части, блять!""",
    """Обосрался сам — не вини других!""",
    """Остановись блять и подумай!""",
    """Отвлекись — или совсем ёбнешься!""",
    """Отложи блять телефон!""",
    """Во второй раз ебашь лучше чем в первый!""",
    """Отрицающий ошибку наебет себя дважды""",
    """Перечитай блять написанное!""",
    """Повторяй блять пройденное!""",
    """Подбери уже блять значение диафрагмы!""",
    """Подготовься блять!""",
    """Покажи бля на что ты способна!""",
    """Получил совет - применяй, блять!""",
    """Пользуйся блять ручным фокусом!""",
    """Попытайся блять ещё раз!""",
    """Поставил цель — запиши блять!""",
    """Прикинь блять дважды!""",
    """Сначала блять проверь сам!""",
    """Сомневаешься — спроси блять!""",
    """Сосредоточься блять!""",
    """Стремись блять к качеству!""",
    """Тренируй ёбаную память!""",
    """Хуёвый мастер ругает инструмент""",
    """Гордись нашей историей!""",
    """Делай блять хорошо - хуёво само получится!""",
    """Лучше заниматься хуйней чем маяться делом!""",
    """Найди блять себе хобби!""",
    """Не делай блять чужую работу!""",
    """Не завидуй, блять - работай!""",
    """Не подражай, блять!""",
    """Нет идей - спизди!""",
    """Не трожь блять чего не понимаешь!""",
    """Отношения - это блять не только ебля!""",
    """Пиздеца не исправить но избежать можно""",
    """Попроси уже совета блять!""",
    """Посмотри блять со стороны!""",
    """Равняйся на лучших, ёпта!""",
    """Сконцентрируйся на чём-то одном, блять!""",
    """Читай блять документацию!""",
]


def get_slogan():
    """Get lozung"""
    tmp_list = SLOGAN + FUCKING_ADVICE
    return tmp_list[random.randint(0, len(tmp_list))]


def get_fucking_advice():
    """Get sovet"""
    return FUCKING_ADVICE[random.randint(0, len(FUCKING_ADVICE))]
