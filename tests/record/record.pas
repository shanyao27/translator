program RecordTest;

type
  Point = record
    x: real;
    y: real;
  end;

  Person = record
    age: integer;
    score: real;
  end;

var
  p: Point;
  q: Point;
  person: Person;
  dist: real;

begin
  { присваивание полей записи }
  p.x := 3.0;
  p.y := 4.0;
  writeln(p.x, p.y);

  { использование полей в выражениях }
  q.x := p.x * 2.0;
  q.y := p.y * 2.0;
  writeln(q.x, q.y);

  { поля в арифметике }
  dist := p.x * p.x + p.y * p.y;
  writeln(dist);

  { запись с integer и real полями }
  person.age := 25;
  person.score := 9.5;
  writeln(person.age, person.score);

  { условие с полем записи }
  if person.age > 18 then
    writeln('adult')
  else
    writeln('minor');

  { поле записи в цикле }
  p.x := 0.0;
  while p.x < 5.0 do
  begin
    p.x := p.x + 1.0
  end;
  writeln(p.x)
end.
