program nestedif;

var x: integer;

begin
    x := 10;

    if x > 0 then
        if x < 20 then
            x := x + 5
        else
            x := x - 5;
end.