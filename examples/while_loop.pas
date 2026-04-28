program WhileDemo;
var
  i, n, s: integer;
begin
  n := 5;
  i := 1;
  s := 0;

  while i <= n do
  begin
    s := s + i;
    i := i + 1;
  end;

  writeln('sum =', s);
end.
