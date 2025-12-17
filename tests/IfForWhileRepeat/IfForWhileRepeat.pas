program ifelse;

var
    x, y, s, i, i1: integer;

begin
    x := 5;
    y := 3;
    s := 0;
    i := 0;
    i1 := 0;

    for i := 1 to 5 do
        s := s + i;

    if x > y then
    begin
        x := x + 1;
        y := y * 2;
        x := x + y;
    end
    else
    begin
        x := x - 1;
        y := y + 4;
    end;

    while i < 5 do
    begin
        i := i + 1;
    end;

    repeat
        i1 := i1 + 1;
    until i1 = 5;
end.