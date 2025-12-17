program nestedloops;

var
    i, j, s: integer;

begin
    s := 0;

    for i := 1 to 3 do
        for j := 1 to 2 do
            s := s + i * j;
end.