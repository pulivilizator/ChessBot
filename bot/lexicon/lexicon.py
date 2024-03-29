LEXICON_COMMANDS_MENU = {
    '/start': 'Запуск бота',
    '/help': 'Помощь',
    '/play_with_bot': 'Начать игру с ботом',
    '/play_with_human': 'Найти противника для игры',
    '/statistic': 'Показать статистику',
    '/rival_stat': 'Показать статистику соперника',
    '/cancel': 'Выход в меню',
}

LEXICON_HANDLER_COMMANDS = {
    '/start': 'Привет, я бот для игры в шахматы.\n'
              'Я нахожусь в супербетном бетатесте.\n'
              'Для получения доп. информации напиши /help, или выбери команду в меню.\n'
              'По поводу вопросов, неточностей пишите сюда - @telejkatupa',
    '/help': 'Правила для игры стандартные.\n\n'
             'Суть игры такая: \n'
             '1) Выбираешь игру с ботом или с человеком\n'
             '2) Приходит картинка игрового поля, и кнопки для хода.\n'
             '3) Нажимаешь на кнопку которой хочешь походить, и нажимаешь куда хочешь походить.\n'
             'Если за последние 24 часа было совершено менее 3х ходов, игра прекращается\n\n'
             'Команды и их описание доступны в меню.\n\n'
             'Из-за невозможности добавить эмодзи шахмат разного цвета(я их не нашел), используются приписки "B"(Black) - у черных, "W"(White) - у белых.\n\n'
             '/start - Запуск бота\n'
             '/help - Помощь\n'
             '/play_with_bot - Начать игру с ботом\n'
             '/play_with_human - Найти противника для игры\n'
             '/statistic - Показать статистику\n'
             '/rival_stat - Показать статистику соперника\n'
             '/cancel - Выход в меню\n\n'
             'По поводу неточностей и дополнений пишите сюда: @telejkatupa',
    '/statistic': 'Ваша статистика:\n',
    '/cancel': 'Если захотите сыграть, пишите',
}

LEXICON_FIGURES = {
    'p': 'B♙',
    'P': 'W♙',
    'r': 'B♜',
    'R': 'W♖',
    'n': 'B♞',
    'N': 'W♘',
    'b': 'B♝',
    'B': 'W♗',
    'q': 'B♛',
    'Q': 'W♕',
    'k': 'B♚',
    'K': 'W♔',
    0: '⬜',
    1: '⬛'
}
