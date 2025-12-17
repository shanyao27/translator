program test;
var
    x, y, s: integer;

function add(a: integer; b: integer): integer;
begin
    add := a + b;
end;

procedure print_sum(a: integer; b: integer);
begin
    s := add(a, b);
    writeln('Sum = ', s);
end;

begin
    x := 10;
    y := add(x, 5);
    writeln('Result of function add: ', y);

    print_sum(3, 4);
end.