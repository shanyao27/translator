program ConstTest;

const
  MAX = 100;
  MIN = -5;
  PI = 3.14;
  GREETING = 'Hello, World!';
  FLAG = true;

var
  i: integer;
  r: real;

begin
  { использование целочисленной константы в цикле }
  i := 0;
  while i < MAX do
  begin
    i := i + 1
  end;
  writeln(i);

  { арифметика с константами }
  r := PI * 2.0;
  writeln(r);

  { строковая константа }
  writeln(GREETING);

  { отрицательная константа }
  i := MIN + 10;
  writeln(i);

  { boolean константа }
  if FLAG then
    writeln('flag is true')
  else
    writeln('flag is false')
end.
