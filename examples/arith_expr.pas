program ArithExprDemo;
var
  a, b, c, res: integer;
begin
  a := 2;
  b := 3;
  c := 4;

  res := a + b * c;       { 2 + 3*4 = 14 }
  writeln('res1=', res);

  res := (a + b) * c;     { (2+3)*4 = 20 }
  writeln('res2=', res);
end.
