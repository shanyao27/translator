program LogicExprDemo;
var
  a, b: integer;
  ok: boolean;
begin
  a := 10;
  b := 3;

  ok := (a > b) and not (b = 0);

  if ok then
    writeln('ok = true')
  else
    writeln('ok = false');
end.
