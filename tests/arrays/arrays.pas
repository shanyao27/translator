program arrays;

var
    a: array[1..5] of integer;
    i: integer;

begin
    a[1] := 10;
    a[2] := 20;

    i := a[1] + a[2];
end.