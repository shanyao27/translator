program CaseTest;

var
  day: integer;
  score: integer;

begin
  { простой case с числами }
  day := 3;
  case day of
    1: writeln('Monday');
    2: writeln('Tuesday');
    3: writeln('Wednesday');
    4: writeln('Thursday');
    5: writeln('Friday');
    6: writeln('Saturday');
    7: writeln('Sunday');
    else writeln('Invalid day')
  end;

  { case с несколькими значениями в одной ветке }
  score := 85;
  case score of
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99: writeln('A');
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89: writeln('B');
    70, 71, 72, 73, 74, 75, 76, 77, 78, 79: writeln('C');
    else writeln('F')
  end;

  { case без ветки else }
  day := 6;
  case day of
    1: writeln('Weekday');
    2: writeln('Weekday');
    3: writeln('Weekday');
    4: writeln('Weekday');
    5: writeln('Weekday')
  end;

  { case в цикле }
  day := 1;
  while day <= 3 do
  begin
    case day of
      1: writeln('first');
      2: writeln('second');
      3: writeln('third')
    end;
    day := day + 1
  end
end.
