module.exports = {
    env: {
        browser: true,
        es2021: true,
        node: true,
    },
    root: true,
    extends: [
        'eslint:recommended',
        'plugin:vue/vue3-essential',
        'plugin:vue/vue3-strongly-recommended',
        'plugin:vue/vue3-recommended',
        'plugin:@typescript-eslint/recommended',
    ],
    parser: 'vue-eslint-parser',
    parserOptions: {
        parser: '@typescript-eslint/parser',
        extraFileExtensions: ['.vue'],
        ecmaVersion: 'latest',
        sourceType: 'module',
    },
    plugins: [
        'import',
        'vue',
        '@typescript-eslint',
    ],
    // Распознавать сокращения пути Vite при импортах
    settings: {
        'import/parsers': {
            '@typescript-eslint/parser': ['.ts', '.tsx'],
        },
        'import/resolver': {
            typescript: {
                project: ['tsconfig.json'],
            },
        },
    },
    rules: {
        'import/extensions': [
            'warn',
            'ignorePackages',
            {
                ts: 'never',
                js: 'never',
            },
        ],
        // Максимальная длина строк
        'max-len': ['warn', { code: 120, ignoreComments: true }],
        'vue/max-len': ['warn', {
            code: 120,
            template: 120,
            ignoreComments: true,
        }],
        // Принуждает использовать висящие запятые в списках
        // уменьшает количество ошибок при копипасте
        'comma-dangle': ['warn', {
            arrays: 'always-multiline',
            objects: 'always-multiline',
            imports: 'always-multiline',
            exports: 'always-multiline',
            functions: 'never',
        }],
        // Файл должен заканчиваться пустой строкой
        'eol-last': 'warn',
        // Порядок импорта
        'import/order': [
            'warn',
            {
                alphabetize: {
                    // Большие/маленькие буквы в названиях импортов
                    // важны, если планируется CI/CD
                    caseInsensitive: false,
                    order: 'asc',
                },
                groups: [
                    'builtin',
                    'external',
                    'index',
                    'sibling',
                    'parent',
                    'internal',
                ],
            },
        ],
        // Задаёт отступ в два пробела
        // Сделано чтобы убрать неравномерные отступы
        // и знаки табуляции из проекта
        indent: [
            'warn',
            2,
        ],
        // Предпочитать одиночные кавычки
        'jsx-quotes': [
            2,
            'prefer-single',
        ],
        // Запрещает дублировать импорты
        'no-duplicate-imports': 'warn',
        'no-restricted-imports': [
            'warn',
            {
                paths: [
                    {
                        message: 'Please use import foo from \'lodash-es/foo\' instead.',
                        name: 'lodash',
                    },
                    {
                        message: 'Avoid using chain since it is non tree-shakable. Try out flow instead.',
                        name: 'lodash-es/chain',
                    },
                    {
                        importNames: ['chain'],
                        message: 'Avoid using chain since it is non tree-shakable. Try out flow instead.',
                        name: 'lodash-es',
                    },
                    {
                        message: 'Please use import foo from \'lodash-es/foo\' instead.',
                        name: 'lodash-es',
                    },
                ],
                patterns: [
                    'lodash/**',
                    'lodash/fp/**',
                ],
            },
        ],
        // Предупреждает о неиспользованных переменных
        'no-unused-vars': 'warn',
        // Отступ в пробелах в фигурных скобках на одной строке
        // Верно: { object }
        // Неверно: {Object}
        'object-curly-spacing': [
            2,
            'always',
        ],
        // Предпочитать одиночные кавычки
        quotes: [
            2,
            'single',
        ],
        // У нас используются точки с запятой для терминации выражений
        semi: 'warn',
        'sort-imports': [
            'warn',
            {
                ignoreCase: false,
                ignoreDeclarationSort: true,
                ignoreMemberSort: false,
            },
        ],
        // Предупреждает о забытых console.log и console.table
        'no-console': ['warn', { allow: ['warn', 'warn'] }],
        // Запрещает использовать названия компонентов из одного слова
        // Кроме перечисленных исключений
        // Используй шаблон СекцияКомпонент при названии файлов
        'vue/multi-word-component-names': [
            'warn',
            {
                ignores: ['index', 'default', '404', '[[index]]'],
            },
        ],
        // Отключает ошибку при использовании нескольких элементов в темплейте в Vue 3
        // Так всё ещё не рекомендуется делать, но фиксить это сейчас себе дороже
        'vue/no-multiple-template-root': 0,
        // Правило, запрещающее :key в template, устарело и не используется во Vue 3
        'vue/no-v-for-template-key': 0,
        // Автофикс обработчиков событий
        'vue/v-on-event-hyphenation': ['warn', 'always', {
            autofix: true,
            ignore: [],
        }],
        // Без пробелов в конце строки
        'no-trailing-spaces': ['warn'],
        // Отключает ошибку, возникающую, если между словом function и скобками есть пробел
        'space-before-function-paren': 0,
        // Запрещает использовать await внутри цикла
        // Используй promise.All вместо этого
        'no-await-in-loop': 'warn',
        // Принуждает использовать строгое сравнение там, где это уместно
        eqeqeq: ['warn', 'smart'],
        // Разрешает переменные вида variable_name вместо variableName
        camelcase: 0,
        // Отключает ошибку, когда единственный экспорт из файла - именованный
        'import/prefer-default-export': 0,
        // Позволяет передавать state как параметр в Store
        'no-param-reassign': ['warn', {
            props: true,
            ignorePropertyModificationsFor: ['state'],
        }],
        'import/no-extraneous-dependencies': ['warn', { devDependencies: true }],
    },
};