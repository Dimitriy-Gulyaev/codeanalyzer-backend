from lexical_analyzer import LexicalAnalyzer, UnknownLexemeException
from os import environ


def start_lexical_analyzer(path_to_code: str, path_to_result: str):
    with open(path_to_code, 'r') as f_code, open(path_to_result, 'w') as f_result:
        source = f_code.read()
        analyzer = LexicalAnalyzer(source)
        try:
            analyzer.parse()
        except UnknownLexemeException as e:
            print(e.msg)
            print(f'unparsed part: {source[e.pos:]}')
        f_result.write(str([str(lex) for lex in analyzer.lexemes]))


if __name__ == '__main__':
    path_to_test_files = environ.get('PATHTOTESTFILES')
    code_filename = 'task_1.txt'
    result_filename = 'res_lex.txt'
    start_lexical_analyzer(path_to_test_files + f'\\{code_filename}',
                           path_to_test_files + f'\\results\\{result_filename}')
