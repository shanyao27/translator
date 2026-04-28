"""
Тесты эквивалентности по курсовой работе.
Запуск: pytest test_equivalence.py -v
"""
import pytest
from src.pipeline import run
from src.errors import LexError, ParseError, SemanticError, TranslatorError


def test_07_if_missing_then():
    """2.01 — Пропущено then."""
    pas = "program Test; begin if a > b writeln('ok'); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "then"'):
        run(pas)


def test_08_if_nonbool_condition():
    """2.02 — Условие if не boolean."""
    pas = "program Test; var x: integer; begin if x then writeln(x); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Ожидалось логическое выражение'):
        run(pas)


def test_09_if_empty_then():
    """2.03 — Пустая ветка then."""
    pas = "program Test; var a, b: integer; begin if a > b then else writeln('no'); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалась ветка после "then"'):
        run(pas)


def test_10_if_empty_else():
    """2.04 — Пустая ветка else."""
    pas = "program Test; var a, b: integer; begin if a > b then writeln('ok') else; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалась ветка после "else"'):
        run(pas)


def test_11_if_missing_begin_end():
    """2.05 — Незакрытый begin..end в then."""
    pas = "program Test; var a, b: integer; begin if a > b then begin writeln('ok'); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "end"'):
        run(pas)


def test_12_if_semicolon_before_else():
    """2.06 — Точка с запятой перед else."""
    pas = "program Test; var a, b: integer; begin if a > b then writeln('ok'); else writeln('no'); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Неожиданный символ ;'):
        run(pas)


def test_13_if_missing_condition():
    """2.07 — Отсутствие условия в if."""
    pas = "program Test; begin if then writeln('ok'); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось условие'):
        run(pas)


def test_14_for_nonint_counter():
    """3.01 — Счётчик for не integer (real)."""
    pas = "program Test; var x: real; begin for x := 1.0 to 5.0 do writeln(x); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Счётчик цикла должен быть целым'):
        run(pas)


def test_15_for_missing_do():
    """3.02 — Пропущено do."""
    pas = "program Test; var i: integer; begin for i := 1 to 10 writeln(i); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "do"'):
        run(pas)


def test_16_for_wrong_assign_op():
    """3.03 — Неверный оператор присваивания (= вместо :=)."""
    pas = "program Test; var i: integer; begin for i = 1 to 10 do writeln(i); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось ":="'):
        run(pas)


def test_17_for_undeclared_counter():
    """3.04 — Счётчик for не объявлен."""
    pas = "program Test; begin for i := 1 to 10 do writeln(i); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Неизвестный идентификатор счётчика'):
        run(pas)


def test_18_for_start_exceeds_end():
    """3.05 — Начальное значение превышает конечное."""
    pas = "program Test; var i: integer; begin for i := 5 to 1 do writeln(i); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Начальное значение превышает конечное'):
        run(pas)


def test_19_for_missing_to_downto():
    """3.06 — Отсутствие to / downto."""
    pas = "program Test; var i: integer; begin for i := 1 10 do writeln(i); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "to" или "downto"'):
        run(pas)


def test_20_for_real_boundary():
    """3.07 — Граница цикла вещественная (5.5)."""
    pas = "program Test; var i: integer; begin for i := 1 to 5.5 do writeln(i); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Граница цикла должна быть целым числом'):
        run(pas)


def test_21_for_counter_modification():
    """3.08 — Изменение счётчика внутри цикла."""
    pas = "program Test; var i: integer; begin for i := 1 to 10 do begin i := 5; end; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Изменение счётчика внутри цикла'):
        run(pas)


def test_22_for_empty_body():
    """3.09 — Пустое тело цикла (do;)."""
    pas = "program Test; var i: integer; begin for i := 1 to 10 do; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Пустое тело цикла'):
        run(pas)


def test_23_var_unknown_type():
    """4.01 — Неизвестный тип переменной."""
    pas = "program Test; var x: uint64; begin end."
    with pytest.raises((ParseError, SemanticError, TranslatorError), match=r'Ожидался тип данных'):
        run(pas)


def test_24_var_missing_colon():
    """4.02 — Отсутствие двоеточия в объявлении переменной."""
    pas = "program Test; var x integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось ":"'):
        run(pas)


def test_25_var_ident_starts_with_digit():
    """4.03 — Идентификатор начинается с цифры."""
    pas = "program Test; var 1x: integer; begin end."
    with pytest.raises((ParseError, LexError, TranslatorError), match=r'Идентификатор начинается с цифры'):
        run(pas)


def test_26_var_undeclared_usage():
    """4.04 — Использование необъявленной переменной."""
    pas = "program Test; begin y := 10; end."
    with pytest.raises(SemanticError, match=r'Неизвестный идентификатор'):
        run(pas)


def test_27_var_duplicate_declaration():
    """4.05 — Повторное объявление переменной."""
    pas = "program Test; var x: integer; x: real; begin end."
    with pytest.raises(SemanticError, match=r'Повторное объявление переменной'):
        run(pas)


def test_28_var_reserved_word_as_name():
    """4.06 — Зарезервированное слово в качестве имени переменной."""
    pas = "program Test; var begin: integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Использование зарезервированного слова в качестве имени переменной'):
        run(pas)


def test_29_var_missing_semicolon():
    """4.07 — Отсутствие точки с запятой после объявления переменной."""
    pas = "program Test; var x: integer begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось ";"'):
        run(pas)


def test_30_while_missing_do():
    """5.01 — Отсутствие ключевого слова do в while."""
    pas = "program Test; var x: integer; begin while x < 10 x := x + 1; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "do"'):
        run(pas)


def test_31_while_nonbool_condition():
    """5.02 — Условие while не является boolean."""
    pas = "program Test; var x: integer; begin while x do x := x + 1; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Ожидалось логическое выражение'):
        run(pas)


def test_32_while_missing_condition():
    """5.03 — Отсутствие условия в while."""
    pas = "program Test; var x: integer; begin while do x := x + 1; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось выражение'):
        run(pas)


def test_33_while_empty_body():
    """5.04 — Пустое тело цикла while."""
    pas = "program Test; var x: integer; begin while x < 10 do; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Пустое тело цикла'):
        run(pas)


def test_34_type_missing_name():
    """6.01 — Отсутствие имени типа."""
    pas = "program Test; type = record x: integer; end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось имя типа'):
        run(pas)


def test_35_record_missing_end():
    """6.02 — Отсутствие end у record."""
    pas = "program Test; type TRec = record x: integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "end"'):
        run(pas)


def test_36_record_empty():
    """6.03 — Пустой record."""
    pas = "program Test; type TRec = record end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Пустой record'):
        run(pas)


def test_37_record_nonexistent_field():
    """6.04 — Обращение к несуществующему полю записи."""
    pas = "program Test; type TRec = record x: integer; end; var r: TRec; begin r.z := 5; end."
    with pytest.raises(SemanticError, match=r'Обращение к несуществующему полю'):
        run(pas)


def test_38_record_duplicate_type():
    """6.05 — Повторное объявление типа."""
    pas = "program Test; type TRec = record x: integer; end; type TRec = record y: real; end; begin end."
    with pytest.raises(SemanticError, match=r'Повторное объявление типа'):
        run(pas)


def test_39_record_duplicate_field():
    """6.06 — Повторное объявление поля в record."""
    pas = "program Test; type TRec = record x: integer; x: real; end; begin end."
    with pytest.raises((ParseError, SemanticError, TranslatorError), match=r'Повторное объявление поля'):
        run(pas)


def test_40_record_unknown_field_type():
    """6.07 — Неизвестный тип поля записи."""
    pas = "program Test; type TRec = record x: unknowntype; end; begin end."
    with pytest.raises((ParseError, SemanticError, TranslatorError), match=r'Ожидался тип (поля|данных)'):
        run(pas)


def test_41_record_missing_equals():
    """6.08 — Отсутствие = при объявлении type."""
    pas = "program Test; type TRec record x: integer; end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "="'):
        run(pas)


def test_42_record_missing_record_keyword():
    """6.09 — Отсутствие ключевого слова record."""
    pas = "program Test; type TRec = 42; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "record"'):
        run(pas)


def test_43_arith_division_by_zero():
    """7.01 — Деление на 0."""
    pas = "program Test; var x: real; begin x := 10 / 0; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Деление на 0'):
        run(pas)


def test_44_arith_type_mismatch():
    """7.02 — Несовместимые типы при присваивании (boolean → integer)."""
    pas = "program Test; var i: integer; b: boolean; begin i := b; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Недопустимое преобразование типов'):
        run(pas)


def test_45_arith_unbalanced_parens():
    """7.03 — Несбалансированные скобки."""
    pas = "program Test; var x: integer; begin x := (5 + 3 * 2; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Несбалансированные скобки'):
        run(pas)


def test_46_arith_invalid_op_for_type():
    """7.04 — Недопустимая операция для данного типа (mod на real)."""
    pas = "program Test; var x: real; begin x := x mod 3; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Недопустимая операция для данного типа'):
        run(pas)


def test_47_arith_missing_operand():
    """7.05 — Пропущен операнд в выражении."""
    pas = "program Test; var x: integer; begin x := 5 + ; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось выражение'):
        run(pas)


def test_48_arith_extra_closing_paren():
    """7.06 — Лишняя закрывающая скобка."""
    pas = "program Test; var x: integer; begin x := (5 + 3)); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Лишняя скобка'):
        run(pas)


def test_49_arith_invalid_symbol():
    """7.07 — Недопустимый символ в выражении."""
    pas = "program Test; var x: integer; begin x := 5 @ 3; end."
    with pytest.raises((LexError, ParseError, TranslatorError), match=r'Недопустимый символ в выражении'):
        run(pas)


def test_50_repeat_missing_until():
    """8.01 — Отсутствие until в repeat."""
    pas = "program Test; var x: integer; begin repeat x := x + 1; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось until'):
        run(pas)


def test_51_repeat_nonbool_condition():
    """8.02 — Условие until не является boolean."""
    pas = "program Test; var x: integer; begin repeat x := x + 1; until x; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Ожидалось логическое выражение'):
        run(pas)


def test_52_repeat_empty_body():
    """8.03 — Пустое тело repeat."""
    pas = "program Test; var x: integer; begin repeat until x = 10; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Пустое тело цикла'):
        run(pas)


def test_53_repeat_missing_condition():
    """8.04 — Отсутствие условия в until."""
    pas = "program Test; var x: integer; begin repeat x := x + 1; until; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось выражение'):
        run(pas)


def test_54_func_undeclared_call():
    """9.01 — Вызов необъявленной подпрограммы."""
    pas = "program Test; begin NonExistentProc(); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Вызов необъявленной подпрограммы'):
        run(pas)


def test_55_func_missing_return_type():
    """9.02 — Отсутствие типа возвращаемого значения функции."""
    pas = "program Test; function GetValue; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидался тип возвращаемого значения'):
        run(pas)


def test_56_func_wrong_arg_count():
    """9.03 — Неверное количество параметров."""
    pas = "program Test; function Sum(a, b: integer): integer; begin Sum := a + b; end; begin writeln(Sum(1)); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Неверное количество параметров'):
        run(pas)


def test_57_func_arg_type_mismatch():
    """9.04 — Несоответствие типов аргументов."""
    pas = "program Test; function Sum(a, b: integer): integer; begin Sum := a + b; end; begin writeln(Sum(1, 'x')); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Несоответствие типов аргументов'):
        run(pas)


def test_58_func_procedure_returns_value():
    """9.05 — Процедура не может возвращать значение."""
    pas = "program Test; procedure Print(); begin Print := 5; end; begin Print(); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Процедура не может возвращать значение'):
        run(pas)


def test_59_func_missing_identifier():
    """9.06 — Функция должна возвращать значение."""
    pas = "program Test; function Sum(a, b: integer): integer; begin end; begin writeln(Sum(1,2)); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Функция должна возвращать значение'):
        run(pas)


def test_60_func_missing_begin():
    """9.07 — Ожидался идентификатор."""
    pas = "program Test; procedure ; begin end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидался идентификатор'):
        run(pas)


def test_61_func_duplicate_declaration():
    """9.08 — Ожидалось begin."""
    pas = "program Test; procedure Print(); var x: integer; end; begin Print(); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "begin"'):
        run(pas)


def test_62_array_nonint_index():
    """10.01 — Индекс должен быть целым."""
    pas = "program Test; var arr: array[1..5] of integer; begin arr[1.5] := 10; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Индекс должен быть целым'):
        run(pas)


def test_63_array_invalid_range():
    """10.02 — Неверный диапазон."""
    pas = "program Test; var arr: array[5..1] of integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Неверный диапазон'):
        run(pas)


def test_64_array_missing_brackets():
    """10.03 — Ожидалось [."""
    pas = "program Test; var arr: array of integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "\["'):
        run(pas)


def test_65_array_missing_of():
    """10.04 — Ожидался индекс массива."""
    pas = "program Test; var arr: array[1..5] of integer; begin arr := 10; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Ожидался индекс массива'):
        run(pas)


def test_66_array_access_non_array():
    """10.05 — Индекс вне границ массива."""
    pas = "program Test; var arr: array[1..5] of integer; begin arr[10] := 5; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Индекс вне границ массива'):
        run(pas)


def test_67_array_unknown_element_type():
    """10.06 — Ожидалось of."""
    pas = "program Test; var arr: array[1..5] integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "of"'):
        run(pas)


def test_68_array_missing_array_keyword():
    """10.07 — Ожидался тип элементов."""
    pas = "program Test; var arr: array[1..5] of unknowntype; begin end."
    with pytest.raises((ParseError, SemanticError, TranslatorError), match=r'Ожидался тип элементов'):
        run(pas)


def test_69_array_bool_index():
    """10.08 — Ожидалось array."""
    pas = "program Test; var arr: [1..5] of integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось array'):
        run(pas)


def test_70_const_duplicate():
    """11.1 — Повторное объявление константы."""
    pas = "program Test; const PI = 3.14; PI = 3.15; begin end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Повторное объявление константы'):
        run(pas)


def test_71_const_reserved_word_as_name():
    """11.2 — Зарезервированное слово как имя константы."""
    pas = "program Test; const begin = 1; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Использование зарезервированного слова в качестве имени константы'):
        run(pas)


def test_72_const_reassignment():
    """11.3 — Изменение значения константы."""
    pas = "program Test; const PI = 3.14; begin PI := 3.15; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Изменение значения константы'):
        run(pas)


def test_73_const_unary_minus_on_string():
    """11.4 — Недопустимый символ в выражении."""
    pas = "program Test; const S = -'hello'; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Недопустимый символ в выражении'):
        run(pas)


def test_74_case_missing_of():
    """12.01 — Отсутствие of в case."""
    pas = "program Test; var x: integer; begin case x 1: writeln('one'); end; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "of"'):
        run(pas)


def test_75_case_missing_end():
    """12.02 — Отсутствие end в case."""
    pas = "program Test; var x: integer; begin case x of 1: writeln('one'); end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "end"'):
        run(pas)


def test_76_case_empty():
    """12.03 — Метка выбора уже использовалась в этом блоке."""
    pas = "program Test; var x: integer; begin case x of 1: writeln('one'); 1: writeln('dup'); end; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Метка выбора уже использовалась в этом блоке'):
        run(pas)


def test_77_case_integer_label_ok():
    """12.04 — Пустой case."""
    pas = "program Test; var x: integer; begin case x of end; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Оператор case должен содержать хотя бы одну ветку'):
        run(pas)


def test_78_case_missing_expression():
    """12.06 — Тип метки не совпадает с типом выражения."""
    pas = "program Test; var x: integer; begin case x of 'a': writeln('letter'); end; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Тип метки не совпадает с типом выражения'):
        run(pas)


def test_79_case_duplicate_else():
    """12.05 — Повторное объявление ветки else."""
    pas = "program Test; var x: integer; begin case x of 1: writeln('one'); else writeln('a'); else writeln('b'); end; end."
    with pytest.raises((ParseError, TranslatorError), match=r'Повторное объявление ветки "else"'):
        run(pas)


def test_80_string_invalid_op():
    """13.01 — Недопустимая операция для строки."""
    pas = "program Test; var s: string; begin s := s * 2; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Недопустимая операция для строки'):
        run(pas)


def test_81_string_type_mismatch_compare():
    """13.02 — Несовместимые типы при сравнении строки и числа."""
    pas = "program Test; var s: string; begin if s > 5 then writeln('err'); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Несовместимые типы при сравнении'):
        run(pas)


def test_82_string_unclosed_literal():
    """13.03 — Незакрытый строковый литерал."""
    pas = "program Test; var s: string; begin s := 'unclosed; end."
    with pytest.raises((LexError, TranslatorError), match=r'Незакрытый строковый литерал'):
        run(pas)


def test_83_string_newline_in_literal():
    """13.04 — Недопустимый символ # в строке."""
    pas = "program Test; var s: string; begin s := 'ab#0cd'; end."
    with pytest.raises((LexError, TranslatorError), match=r'Недопустимый символ в строке'):
        run(pas)


def test_84_implicit_string_to_int():
    """14.01 — Недопустимое преобразование типов (string → integer)."""
    pas = "program Test; var x: integer; begin x := 'hello'; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Недопустимое преобразование типов'):
        run(pas)


def test_85_implicit_bool_to_int():
    """14.02 — Недопустимое преобразование типов (boolean → integer)."""
    pas = "program Test; var x: integer; b: boolean; begin x := b; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Недопустимое преобразование типов'):
        run(pas)


def test_86_implicit_char_to_int():
    """14.03 — Недопустимое преобразование типов (char → integer)."""
    pas = "program Test; var x: integer; c: char; begin x := c; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Недопустимое преобразование типов'):
        run(pas)


def test_87_oop_class_missing_end():
    """15.01 — Отсутствие end у класса."""
    pas = "program Test; type TRec = class x: integer; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидалось "end"'):
        run(pas)


def test_88_oop_duplicate_class():
    """15.02 — Повторное объявление класса."""
    pas = "program Test; type TRec = class x: integer; end; type TRec = class y: real; end; begin end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Повторное объявление класса'):
        run(pas)


def test_89_oop_empty_class():
    """15.03 — Пустой класс."""
    pas = "program Test; type TRec = class end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Пустой класс'):
        run(pas)


def test_90_oop_duplicate_class_field():
    """15.04 — Повторное объявление поля класса."""
    pas = "program Test; type TRec = class x: integer; x: real; end; begin end."
    with pytest.raises((ParseError, SemanticError, TranslatorError), match=r'Повторное объявление поля'):
        run(pas)


def test_91_oop_undefined_class_var():
    """15.05 — Повторное объявление метода."""
    pas = "program Test; type TRec = class procedure Speak(); procedure Speak(); end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Повторное объявление метода'):
        run(pas)


def test_92_oop_wrong_constructor_arg_count():
    """15.06 — Ожидался идентификатор конструктора."""
    pas = "program Test; type TRec = class constructor ; end; begin end."
    with pytest.raises((ParseError, TranslatorError), match=r'Ожидался идентификатор конструктора'):
        run(pas)


def test_93_oop_method_for_nonexistent_class():
    """15.07 — Класс не объявлен."""
    pas = "program Test; procedure Ghost.DoSomething(); begin end; begin end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Класс не объявлен'):
        run(pas)


def test_94_oop_call_method_on_undeclared():
    """15.08 — Метод не объявлен в классе."""
    pas = "program Test; type TRec = class procedure Speak(); end; procedure TRec.Run(); begin end; begin end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Метод не объявлен в классе'):
        run(pas)


def test_95_oop_missing_constructor_id():
    """15.09 — Вызов метода на необъявленном объекте."""
    pas = "program Test; begin obj->DoSomething(); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Вызов метода на необъявленном объекте'):
        run(pas)


def test_96_oop_constructor_wrong_arg_types():
    """15.10 — Обращение к несуществующему методу."""
    pas = "program Test; type TRec = class x: integer; end; var r: TRec; begin r->Ghost(); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Обращение к несуществующему методу'):
        run(pas)


def test_97_oop_constructor_not_declared():
    """15.11 — Обращение к несуществующему полю."""
    pas = "program Test; type TRec = class x: integer; end; var r: TRec; begin r->ghost := 1; end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Обращение к несуществующему полю'):
        run(pas)


def test_98_oop_nonexistent_method():
    """15.12 — Неверное количество аргументов конструктора."""
    pas = "program Test; type TRec = class constructor Create(n: string); end; constructor TRec.Create(n: string); begin end; var r: TRec; begin r := TRec.Create('a', 'b'); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Неверное количество аргументов конструктора'):
        run(pas)


def test_99_oop_field_type_mismatch():
    """15.13 — Несоответствие типов аргументов конструктора."""
    pas = "program Test; type TRec = class constructor Create(n: string); end; constructor TRec.Create(n: string); begin end; var r: TRec; begin r := TRec.Create(42); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Несоответствие типов аргументов конструктора'):
        run(pas)


def test_100_oop_duplicate_method_impl():
    """15.14 — Конструктор не объявлен."""
    pas = "program Test; type TRec = class x: integer; end; var r: TRec; begin r := TRec.Create(); end."
    with pytest.raises((SemanticError, TranslatorError), match=r'Конструктор не объявлен'):
        run(pas)

def test_101_golden_path():
    """Позитивный тест: все конструкции языка в одной программе."""
    pas = """program GoldenPath;

const
  MAX = 5;

type
  TPoint = record
    x: integer;
    y: integer;
  end;

var
  i, j : integer;
  r    : real;
  flag : boolean;
  arr  : array[1..5] of integer;
  pt   : TPoint;

function Square(n: integer): integer;
begin
  Square := n * n
end;

procedure PrintNum(n: integer);
begin
  writeln(n)
end;

begin
  i := 3;
  if i > 0 then
    writeln(i)
  else
    writeln(i);

  for i := 1 to MAX do
    arr[i] := Square(i);

  j := 1;
  while j <= MAX do
  begin
    r := 3.14;
    j := j + 1
  end;

  i := 0;
  repeat
    i := i + 1
  until i >= MAX;

  case i of
    1: writeln(i);
    2: writeln(i)
  else
    writeln(i)
  end;

  pt.x := 10;
  pt.y := 20;

  flag := (i mod 2) = 0;
  PrintNum(arr[1])
end.
"""
    result = run(pas)
    assert "#include" in result
    assert "int main" in result