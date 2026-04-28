program IfElseDemo;
var
  a, b, maxv: integer;
begin
  a := 7;
  b := 12;

  if a > b then
    maxv := a
  else
    maxv := b;

  writeln('max =', maxv);

  { пример if с блоком }
  if (a = 7) and (b > 0) then
  begin
    writeln('a is 7 and b positive');
    a := a + 1;
  end
  else
    writeln('condition false');
end.