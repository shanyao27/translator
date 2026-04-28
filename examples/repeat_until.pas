program RepeatUntilDemo;
var
  x, cnt: integer;
begin
  cnt := 0;

  repeat
    readln(x);
    if x <> 0 then
      cnt := cnt + 1;
  until x = 0;

  writeln('count =', cnt);
end.
