program ifelse;

var
    x, y: integer;

begin
    x := 5;
    y := 3;

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
end.